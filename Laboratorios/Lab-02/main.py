import argparse
import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

GRAPHQL_URL = "https://api.github.com/graphql"
TIMEOUT = 60

TARGET_REPOS = 1000
PAGE_SIZE = 50

DATA_DIR = Path(__file__).parent / "data"
JSON_PATH = DATA_DIR / "top_java_repos.json"
CSV_PATH = DATA_DIR / "top_java_repos.csv"

REPOS_DIR = DATA_DIR / "repos"

CK_RESULTS_DIR = DATA_DIR / "ck_results"

CK_JAR_PATH = Path(__file__).parent / "ck.jar"

EXCLUDED_CSV = DATA_DIR / "ck_excluded.csv"

load_dotenv()

def load_repos_from_csv(path: Path = CSV_PATH):
    """Carrega a lista de repositórios a partir do CSV gerado na etapa de extração."""
    if not path.exists():
        print(f"Erro: arquivo {path} não encontrado. Rode primeiro --extract.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def sanitize_repo_name(name_with_owner: str) -> str:
    """Converte "owner/repo" em um nome seguro para diretório, ex: owner__repo."""
    return name_with_owner.replace("/", "__")


def clone_repo(name_with_owner: str, url: str, base_dir: Path = REPOS_DIR) -> Path:
    """Clona um único repositório (se ainda não estiver clonado) e retorna o caminho local.

    Usa `git clone --depth 1` para reduzir o tamanho do clone.
    """

    base_dir.mkdir(parents=True, exist_ok=True)
    safe_name = sanitize_repo_name(name_with_owner)
    dest = base_dir / safe_name

    if dest.exists():
        print(f"[clone] Repositório já clonado em {dest}")
        return dest

    print(f"[clone] Clonando {name_with_owner} em {dest}...")
    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                url,
                str(dest),
            ],
            check=True,
        )
    except FileNotFoundError:
        print("Erro: git não encontrado no PATH. Instale o Git e tente novamente.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao clonar {name_with_owner}: {e}")
        # Não encerramos o script aqui para permitir continuar com outros repositórios
    return dest


def run_ck_on_repo(
    repo_path: Path,
    output_base_dir: Path = CK_RESULTS_DIR,
    exit_on_error: bool = True,
    use_jars: bool = True,
) -> Path | None:
    """Executa a ferramenta CK em um repositório Java já clonado.

    Retorna o diretório onde os arquivos CSV de métricas foram gerados,
    ou ``None`` em caso de falha quando ``exit_on_error`` for ``False``.

    ``use_jars`` controla se o CK tentará resolver tipos externos a partir
    dos JARs do projeto. Repos muito grandes ou multi-módulo às vezes
    quebram o parser do JDT nesse modo; nesses casos, ``use_jars=False``
    serve como fallback (perde-se precisão na resolução de tipos, mas as
    métricas estruturais continuam corretas).
    """

    if not CK_JAR_PATH.exists():
        print(
            f"Erro: arquivo CK JAR não encontrado em {CK_JAR_PATH}. "
            "Baixe o JAR do projeto CK e renomeie para 'ck.jar' nesta pasta.",
        )
        sys.exit(1)

    if not repo_path.exists():
        print(f"Erro: diretório do repositório não encontrado: {repo_path}")
        if exit_on_error:
            sys.exit(1)
        return None

    output_base_dir.mkdir(parents=True, exist_ok=True)
    safe_name = sanitize_repo_name(repo_path.name)
    output_dir = output_base_dir / safe_name
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[ck] Executando CK em {repo_path} (use_jars={use_jars})...")
    try:
        subprocess.run(
            [
                "java",
                "-Xmx8g",  # heap maior para repos grandes (elasticsearch, jdk, etc.)
                "-jar",
                str(CK_JAR_PATH),
                str(repo_path),
                "true" if use_jars else "false",  # use jars
                "0",  # max files per partition (0 = automático)
                "false",  # variables and fields metrics? (false para reduzir tamanho)
                str(output_dir),
            ],
            check=True,
        )
    except FileNotFoundError:
        print("Erro: Java não encontrado no PATH. Instale o Java (>= 8) e tente novamente.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar CK em {repo_path}: {e}")
        if exit_on_error:
            sys.exit(1)
        return None

    print(f"[ck] Métricas geradas em {output_dir}")
    return output_dir


def get_token():
    """Lê o token de acesso do GitHub da variável de ambiente GITHUB_TOKEN."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: defina GITHUB_TOKEN.")
        sys.exit(1)
    return token


def build_query():
    """Monta e retorna a query GraphQL usada para buscar os repositórios Java com mais estrelas."""
    return """
    query TopJavaRepos($cursor: String, $first: Int!) {
      search(
        query: "language:Java sort:stars-desc"
        type: REPOSITORY
        first: $first
        after: $cursor
      ) {
        pageInfo {
          endCursor
          hasNextPage
        }
        nodes {
          ... on Repository {
            nameWithOwner
            url
            stargazerCount
            createdAt
            releases {
              totalCount
            }
          }
        }
      }
    }
    """


def fetch_page(token, cursor=None, max_attempts=5):
    """Busca uma página de repositórios na API GraphQL do GitHub usando o cursor informado."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"query": build_query(), "variables": {"cursor": cursor, "first": PAGE_SIZE}}

    for attempt in range(max_attempts):
        try:
            response = requests.post(GRAPHQL_URL, json=payload, headers=headers, timeout=TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    print("Erro GraphQL:", data["errors"], file=sys.stderr)
                    sys.exit(1)
                return data["data"]["search"]

            if response.status_code in {502, 503, 504}:
                wait = 5 * (attempt + 1)
                print(f"Erro {response.status_code}. Tentando novamente em {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue

            print(f"Erro HTTP {response.status_code}: {response.text}", file=sys.stderr)
            sys.exit(1)

        except requests.RequestException as e:
            print(f"Erro de conexão: {e}", file=sys.stderr)
            time.sleep(5)

    print("Máximo de tentativas atingido.")
    sys.exit(1)


def extract_top_java_repos(token, target_repos=TARGET_REPOS):
    """Extrai top repositórios Java por estrelas e retorna a lista."""
    all_repos = []
    cursor = None
    has_next = True

    print("Iniciando coleta")

    while has_next and len(all_repos) < target_repos:
        result = fetch_page(token, cursor)

        all_repos.extend(result["nodes"])

        cursor = result["pageInfo"]["endCursor"]
        has_next = result["pageInfo"]["hasNextPage"]

        print(f"Coletados até agora: {len(all_repos)}")

    return all_repos[:target_repos]


def save_json(repos, path=JSON_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(repos, f, ensure_ascii=False, indent=2)


def save_csv(repos, path=CSV_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "nameWithOwner",
        "url",
        "stargazerCount",
        "createdAt",
        "releasesCount",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for repo in repos:
            releases = repo.get("releases") or {}
            writer.writerow(
                {
                    "nameWithOwner": repo.get("nameWithOwner"),
                    "url": repo.get("url"),
                    "stargazerCount": repo.get("stargazerCount"),
                    "createdAt": repo.get("createdAt"),
                    "releasesCount": releases.get("totalCount"),
                }
            )


def run_extract():
    token = get_token()
    repos = extract_top_java_repos(token)
    save_json(repos)
    save_csv(repos)
    print(f"CSV salvo em {CSV_PATH}")


def clone_top_repos(limit: int = 10):
    """Clona os primeiros N repositórios listados em `top_java_repos.csv`."""

    repos = load_repos_from_csv()
    limit = min(limit, len(repos))
    print(f"Clonando os {limit} primeiros repositórios da lista...")

    for i, repo in enumerate(repos[:limit], start=1):
        name = repo["nameWithOwner"]
        url = repo["url"]
        print(f"[{i}/{limit}] {name}")
        clone_repo(name, url)


def _save_excluded(rows: list[dict]) -> None:
    """Persiste a lista de repositorios excluidos em ``data/ck_excluded.csv``.

    Mescla com entradas pre-existentes (mesmo nome = atualizado).
    """
    existing: dict[str, dict] = {}
    if EXCLUDED_CSV.exists():
        with open(EXCLUDED_CSV, "r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                existing[row["name_with_owner"]] = row

    for row in rows:
        existing[row["name_with_owner"]] = row

    EXCLUDED_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(EXCLUDED_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["name_with_owner", "reason", "stage", "excluded_at"]
        )
        writer.writeheader()
        for row in existing.values():
            writer.writerow(row)


def measure_all_repos(limit: int | None = None, skip_existing: bool = True) -> None:
    """Clona (se necessário) e executa CK para **todos** os repositórios da lista.

    - ``limit``: se informado, processa apenas os ``limit`` primeiros repositórios.
    - ``skip_existing``: pula repositórios que já possuem ``class.csv`` em
      ``data/ck_results/<owner>__<repo>/`` (útil para retomar execuções).

    Esta função é a versão "batch" de ``measure_single_repo`` e atende ao
    requisito de coletar métricas para os 1.000 repositórios.
    """

    repos = load_repos_from_csv()
    total = len(repos) if limit is None else min(limit, len(repos))
    print(f"Iniciando medição em lote para {total} repositórios...")

    from datetime import datetime, timezone

    successes: list[str] = []
    failures: list[dict] = []
    skipped: list[str] = []

    def _record_failure(name: str, reason: str, stage: str) -> None:
        failures.append(
            {
                "name_with_owner": name,
                "reason": reason,
                "stage": stage,
                "excluded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        )

    for i, repo_info in enumerate(repos[:total], start=1):
        name = repo_info["nameWithOwner"]
        url = repo_info["url"]
        safe_name = sanitize_repo_name(name)
        ck_output_dir = CK_RESULTS_DIR / safe_name

        print()
        print(f"=== [{i}/{total}] {name} ===")

        class_csv = ck_output_dir / "class.csv"
        if (
            skip_existing
            and class_csv.exists()
            and class_csv.stat().st_size > 0
        ):
            print(f"[skip] CK já executado em {ck_output_dir}")
            skipped.append(name)
            continue

        try:
            local_repo_path = clone_repo(name, url)
        except SystemExit:
            _record_failure(name, "git não encontrado", "clone")
            break
        except Exception as e:
            print(f"[erro] clone falhou para {name}: {e}")
            _record_failure(name, f"clone: {e}", "clone")
            continue

        if not local_repo_path.exists():
            print(f"[erro] diretório de clone ausente para {name}")
            _record_failure(name, "clone ausente", "clone")
            continue

        result = run_ck_on_repo(local_repo_path, exit_on_error=False, use_jars=True)
        if result is None:
            # Fallback: tenta de novo sem resolucao de jars (perde precisao
            # na resolucao de tipos externos, mas evita o crash do JDT em
            # repos gigantes/multi-modulo).
            print(f"[retry] {name}: tentando de novo com use_jars=False")
            result = run_ck_on_repo(
                local_repo_path, exit_on_error=False, use_jars=False
            )
            if result is not None:
                successes.append(name)
                continue
            _record_failure(
                name,
                "CK NPE/erro mesmo com use_jars=False (provavel JDT incompativel com sintaxe Java moderna)",
                "ck_both_modes",
            )
            continue

        successes.append(name)

    if failures:
        _save_excluded(failures)

    print()
    print("=== Resumo da medição em lote ===")
    print(f"Sucesso: {len(successes)}")
    print(f"Pulados (já processados): {len(skipped)}")
    print(f"Falhas: {len(failures)}")
    if failures:
        print(f"Exclusões registradas em: {EXCLUDED_CSV}")
        print("Detalhes das falhas:")
        for f in failures:
            print(f"  - {f['name_with_owner']} [{f['stage']}]: {f['reason']}")


def measure_single_repo(index: int = 1):
    """Clona (se necessário) e roda CK para **um** repositório da lista.

    `index` é 1-based (1 = primeiro repositório do CSV).

    Esta função atende ao requisito da Lab02S01 de gerar um `.csv` com
    o resultado das medições de 1 repositório.
    """

    repos = load_repos_from_csv()

    if index < 1 or index > len(repos):
        print(f"Índice inválido: {index}. Deve estar entre 1 e {len(repos)}.")
        sys.exit(1)

    repo_info = repos[index - 1]
    name = repo_info["nameWithOwner"]
    url = repo_info["url"]
    stars = repo_info["stargazerCount"]

    print(f"Selecionado repositório #{index}: {name} ({stars} stars)")

    local_repo_path = clone_repo(name, url)
    ck_output_dir = run_ck_on_repo(local_repo_path)

    print()
    print("=== Resultado da medição ===")
    print(f"Repositório: {name}")
    print(f"Caminho local: {local_repo_path}")
    print(f"Arquivos de métricas (por exemplo, class.csv, method.csv) em: {ck_output_dir}")
    print(
        "Use, por exemplo, o arquivo 'class.csv' gerado por CK como o arquivo de "
        "resultado das medições para este repositório."
    )


def main():
    parser = argparse.ArgumentParser(description="Lab 02")
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Executa a extração e salva os Top Java repos em data/top_java_repos.csv",
    )

    parser.add_argument(
        "--clone",
        action="store_true",
        help=(
            "Clona os repositórios listados em data/top_java_repos.csv "
            "(veja também o parâmetro --limit)."
        ),
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Número máximo de repositórios a processar (usado com --clone "
            "ou --measure-all). Padrão para --clone: 10. Padrão para "
            "--measure-all: todos. Para 1.000, use --limit 1000."
        ),
    )

    parser.add_argument(
        "--measure-one",
        type=int,
        metavar="IDX",
        help=(
            "Clona (se necessário) e executa CK para um único repositório da lista, "
            "onde IDX é a posição (1-based) no CSV. Ex.: --measure-one 1."
        ),
    )

    parser.add_argument(
        "--measure-all",
        action="store_true",
        help=(
            "Clona (se necessário) e executa CK para todos os repositórios da lista. "
            "Combine com --limit para processar apenas os N primeiros."
        ),
    )

    args = parser.parse_args()

    if args.extract:
        run_extract()
        return

    if args.measure_one is not None:
        measure_single_repo(args.measure_one)
        return

    if args.measure_all:
        measure_all_repos(limit=args.limit)
        return

    if args.clone:
        clone_top_repos(limit=args.limit if args.limit is not None else 10)
        return

    parser.print_help()


if __name__ == "__main__":
    main()

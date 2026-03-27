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

load_dotenv()


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
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["nameWithOwner", "url", "stargazerCount"])
        writer.writeheader()
        writer.writerows(repos)


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
        default=10,
        help=(
            "Número máximo de repositórios a clonar (usado com --clone). "
            "Padrão: 10. Para 1.000, use --limit 1000."
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

    args = parser.parse_args()

    if args.extract:
        run_extract()
        return

    if args.measure_one is not None:
        measure_single_repo(args.measure_one)
        return

    if args.clone:
        clone_top_repos(limit=args.limit)
        return

    parser.print_help()


if __name__ == "__main__":
    main()

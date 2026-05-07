"""Lab03S01 - coleta de Pull Requests dos repositórios selecionados.

  - state: MERGED ou CLOSED;
  - reviews.totalCount >= 1;
  - (closedAt|mergedAt) - createdAt > 1 hora.

Para cada repositório é gerado um arquivo JSON em `data/prs_brutos/`
(checkpoint), permitindo retomar a execução de onde parou.
"""

import os
import sys
import json
import time
import random
import argparse
from pathlib import Path
from datetime import datetime, timezone

import requests
import pandas as pd
from dotenv import load_dotenv

GRAPHQL_URL = "https://api.github.com/graphql"
TIMEOUT = 90
# Listagem só pede poucos campos; 100 reduz páginas em repositórios enormes (ex.: tensorflow).
LIST_PAGE_SIZE = 100
LISTAGEM_LOG_A_CADA_PAGINAS = 12
DETAILS_BATCH_SIZE = 10   # quantos PRs detalhar por request (batch via aliases)
DETALHES_LOG_A_CADA_LOTES = 25
MIN_REVIEW_HOURS = 1      # filtro de tempo de revisão: estritamente maior que 1h
MAX_RETRIES = 10
# Limite padrão: repositórios grandes podem ter dezenas de milhares de PRs filtrados;
# sem teto, a fase de detalhes vira milhares de requisições GraphQL (horas/dias).
DEFAULT_MAX_PRS_PER_REPO = 2500

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INPUT_CSV = DATA_DIR / "repositorios.csv"
OUTPUT_DIR = DATA_DIR / "prs_brutos"

load_dotenv()


def get_token():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: defina GITHUB_TOKEN.", file=sys.stderr)
        sys.exit(1)
    return token


# Fase 1: query LEVE de listagem — só campos para aplicar filtros
LIST_QUERY = """
query RepoPRs($owner: String!, $name: String!, $cursor: String, $first: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequests(
      states: [MERGED, CLOSED]
      first: $first
      after: $cursor
      orderBy: {field: CREATED_AT, direction: DESC}
    ) {
      pageInfo { endCursor hasNextPage }
      nodes {
        number
        createdAt
        closedAt
        mergedAt
        reviews { totalCount }
      }
    }
  }
}
"""


def build_details_query(numbers):
    """Monta uma query com aliases para buscar detalhes de vários PRs num único request."""
    aliases = []
    for n in numbers:
        aliases.append(f"""
    pr{n}: pullRequest(number: {n}) {{
      number
      title
      state
      createdAt
      closedAt
      mergedAt
      additions
      deletions
      changedFiles
      body
      reviews {{ totalCount }}
      comments {{ totalCount }}
      participants {{ totalCount }}
    }}""")
    return (
        "query RepoPRDetails($owner: String!, $name: String!) {\n"
        "  repository(owner: $owner, name: $name) {"
        + "".join(aliases)
        + "\n  }\n}\n"
    )


def graphql_request(token, query, variables, max_attempts=MAX_RETRIES):
    """POST na API GraphQL com retry exponencial para erros transientes e rate limit."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"query": query, "variables": variables}

    for attempt in range(max_attempts):
        try:
            resp = requests.post(
                GRAPHQL_URL, json=payload, headers=headers, timeout=TIMEOUT
            )

            # Verificar rate limit primário via headers antes de processar
            remaining = resp.headers.get("X-RateLimit-Remaining", "?")
            reset = resp.headers.get("X-RateLimit-Reset", "?")
            if remaining == "0":
                reset_time = int(reset) if reset != "?" else 0
                wait = max(reset_time - int(time.time()), 60)
                print(f"  rate limit primário atingido. Aguardando {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue

            # Rate limit secundário
            if resp.status_code == 403:
                if "rate limit" in resp.text.lower() or "api rate limit" in resp.text.lower():
                    # Exponencial com jitter: 2^attempt * base + random jitter
                    base_wait = min(2 ** attempt * 10, 300)  # max 5 min
                    jitter = random.uniform(0, base_wait * 0.1)
                    wait = base_wait + jitter
                    print(f"  rate limit secundário. Aguardando {wait:.1f}s (tentativa {attempt + 1}/{max_attempts})...", file=sys.stderr)
                    time.sleep(wait)
                    continue

            # Erros de servidor temporários
            if resp.status_code in {502, 503, 504}:
                base_wait = min(2 ** attempt * 3, 120)  # exponencial: 3s, 6s, 12s, ..., max 2 min
                jitter = random.uniform(0, base_wait * 0.2)
                wait = base_wait + jitter
                print(f"  HTTP {resp.status_code} (tentativa {attempt + 1}/{max_attempts}). Retry em {wait:.1f}s...", file=sys.stderr)
                time.sleep(wait)
                continue

            if resp.status_code != 200:
                print(f"  HTTP {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
                # Não retry para 4xx (exceto 403 rate limit, já tratado acima)
                if resp.status_code >= 500:
                    time.sleep(min(2 ** attempt * 5, 60))
                    continue
                return None

            data = resp.json()
            if "errors" in data:
                # Pode ser timeout do GraphQL — tenta novamente
                error_msg = str(data.get("errors", ""))
                if "timeout" in error_msg.lower() or "deadline exceeded" in error_msg.lower():
                    base_wait = min(2 ** attempt * 5, 120)
                    jitter = random.uniform(0, base_wait * 0.15)
                    wait = base_wait + jitter
                    print(f"  GraphQL timeout/deadline (tentativa {attempt + 1}/{max_attempts}). Retry em {wait:.1f}s...", file=sys.stderr)
                    time.sleep(wait)
                    continue
                print(f"  Erro GraphQL: {data['errors']}", file=sys.stderr)
                return None
            return data["data"]

        except requests.Timeout:
            base_wait = min(2 ** attempt * 3, 90)
            jitter = random.uniform(0, base_wait * 0.2)
            wait = base_wait + jitter
            print(f"  Timeout na requisição (tentativa {attempt + 1}/{max_attempts}). Retry em {wait:.1f}s...", file=sys.stderr)
            time.sleep(wait)
        except requests.RequestException as e:
            base_wait = min(2 ** attempt * 3, 90)
            jitter = random.uniform(0, base_wait * 0.2)
            wait = base_wait + jitter
            print(f"  Erro de conexão: {e} (tentativa {attempt + 1}/{max_attempts}). Retry em {wait:.1f}s...", file=sys.stderr)
            time.sleep(wait)

    print(f"  FALHA: máximo de tentativas ({max_attempts}) atingido.", file=sys.stderr)
    return None


def parse_iso(dt_str):
    if not dt_str:
        return None
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


def passes_filters(pr):
    """Filtros do enunciado: >=1 review e tempo de revisão > 1h."""
    if pr["reviews"]["totalCount"] < 1:
        return False

    created = parse_iso(pr["createdAt"])
    end = parse_iso(pr.get("mergedAt") or pr.get("closedAt"))
    if not created or not end:
        return False

    delta_hours = (end - created).total_seconds() / 3600
    return delta_hours > MIN_REVIEW_HOURS


def fetch_pr_details(token, owner, name, numbers):
    """Fase 2: busca campos pesados (additions/deletions/body/...) em batch via aliases."""
    detalhes = []
    total = len(numbers)
    total_lotes = max(1, (total + DETAILS_BATCH_SIZE - 1) // DETAILS_BATCH_SIZE)
    for i in range(0, len(numbers), DETAILS_BATCH_SIZE):
        lote_idx = i // DETAILS_BATCH_SIZE + 1
        if lote_idx == 1 or lote_idx % DETALHES_LOG_A_CADA_LOTES == 0 or lote_idx == total_lotes:
            print(
                f"   … detalhes: lote {lote_idx}/{total_lotes} "
                f"({min(i + DETAILS_BATCH_SIZE, total)}/{total} PRs)…",
                flush=True,
            )
        chunk = numbers[i : i + DETAILS_BATCH_SIZE]
        query = build_details_query(chunk)
        data = graphql_request(token, query, {"owner": owner, "name": name})
        if data is None or data.get("repository") is None:
            print(f"  falha ao buscar detalhes de {owner}/{name} chunk {i}", file=sys.stderr)
            continue
        repo = data["repository"]
        for n in chunk:
            pr = repo.get(f"pr{n}")
            if pr is not None:
                detalhes.append(pr)
        time.sleep(0.5 + random.uniform(0, 0.3))
    return detalhes


def fetch_prs_for_repo(token, owner, name, max_prs_per_repo=0):
    """Pagina sobre PRs MERGED/CLOSED (query leve), filtra, depois busca detalhes em batch.

    A listagem usa orderBy CREATED_AT DESC: os PRs aprovados são dos mais recentes para
    os mais antigos. Se max_prs_per_repo > 0, para a listagem ao atingir esse total
    (amostra dos mais recentes) e evita varrer todo o histórico do repositório.
    max_prs_per_repo == 0 significa sem limite.
    """
    aprovados_numbers = []
    total_vistos = 0
    cursor = None
    has_next = True
    listagem_cortada_por_limite = False
    limite = max_prs_per_repo if max_prs_per_repo and max_prs_per_repo > 0 else 0
    pagina_listagem = 0

    # Fase 1: listagem leve + filtragem
    while has_next:
        pagina_listagem += 1
        variables = {
            "owner": owner,
            "name": name,
            "cursor": cursor,
            "first": LIST_PAGE_SIZE,
        }
        data = graphql_request(token, LIST_QUERY, variables)
        if data is None or data.get("repository") is None:
            print(f"  falha ao buscar página de {owner}/{name}", file=sys.stderr)
            break

        prs = data["repository"]["pullRequests"]
        nodes = prs["nodes"]
        page_info = prs["pageInfo"]

        for pr in nodes:
            total_vistos += 1
            if passes_filters(pr):
                aprovados_numbers.append(pr["number"])
                if limite and len(aprovados_numbers) >= limite:
                    listagem_cortada_por_limite = True
                    has_next = False
                    break

        if listagem_cortada_por_limite:
            break

        if (
            pagina_listagem == 1
            or pagina_listagem % LISTAGEM_LOG_A_CADA_PAGINAS == 0
        ):
            print(
                f"   … listagem em curso: {total_vistos} PRs vistos, "
                f"{len(aprovados_numbers)} aprovados (pág. {pagina_listagem})…",
                flush=True,
            )

        cursor = page_info["endCursor"]
        has_next = page_info["hasNextPage"]

        time.sleep(0.4 + random.uniform(0, 0.3))

    if limite:
        aprovados_numbers = aprovados_numbers[:limite]

    total_aprovados_listagem = len(aprovados_numbers)

    # Fase 2: detalhes só dos aprovados
    print(
        f"   listagem: {total_vistos} vistos, {total_aprovados_listagem} aprovados "
        f"(limite={'∞' if not limite else limite}) — buscando detalhes..."
    )
    selecionados = fetch_pr_details(token, owner, name, aprovados_numbers)

    meta = {
        "max_prs_per_repo": limite or None,
        "listagem_cortada_por_limite": listagem_cortada_por_limite,
        "total_aprovados_na_listagem": total_aprovados_listagem,
    }
    return selecionados, total_vistos, meta


def filename_for(name_with_owner):
    """Nome do arquivo de checkpoint para o repo."""
    return name_with_owner.replace("/", "__") + ".json"


def main():
    parser = argparse.ArgumentParser(description="Coleta PRs filtrados dos repos do CSV.")
    parser.add_argument(
        "--input",
        default=str(INPUT_CSV),
        help="CSV de repositórios (saída da Pessoa 1).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limite de repositórios a processar (debug).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reprocessa repositórios mesmo que já tenham checkpoint.",
    )
    parser.add_argument(
        "--max-prs-per-repo",
        type=int,
        default=DEFAULT_MAX_PRS_PER_REPO,
        help=(
            "Máximo de PRs filtrados por repositório (mais recentes primeiro). "
            f"Padrão {DEFAULT_MAX_PRS_PER_REPO}. Use 0 para sem limite (pode ser muito lento)."
        ),
    )
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Erro: {args.input} não encontrado.", file=sys.stderr)
        sys.exit(1)

    if args.max_prs_per_repo < 0:
        print("Erro: --max-prs-per-repo deve ser >= 0 (0 = sem limite).", file=sys.stderr)
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    token = get_token()
    df = pd.read_csv(args.input)
    if args.limit:
        df = df.head(args.limit)

    total_repos = len(df)
    print(f"Processando {total_repos} repositórios.\n")

    for idx, row in enumerate(df.itertuples(index=False), 1):
        nwo = row.nameWithOwner
        owner, name = nwo.split("/", 1)
        out_path = OUTPUT_DIR / filename_for(nwo)

        if out_path.exists() and not args.force:
            print(f"[{idx}/{total_repos}] {nwo} (checkpoint encontrado, pulando)")
            continue

        print(f"[{idx}/{total_repos}] {nwo} ...")
        max_repo = args.max_prs_per_repo if args.max_prs_per_repo > 0 else 0
        prs, total_vistos, meta = fetch_prs_for_repo(
            token, owner, name, max_prs_per_repo=max_repo
        )

        payload = {
            "repo": nwo,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "total_prs_vistos": total_vistos,
            "total_prs_filtrados": len(prs),
            "coleta_meta": meta,
            "prs": prs,
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        print(f"   -> {len(prs)} PRs filtrados (de {total_vistos} vistos).")

        # pausa entre repositórios para não sobrecarregar a API
        if idx < total_repos:
            inter_repo_pause = 2.0 + random.uniform(0, 1.5)
            print(f"   (pausa entre repos: {inter_repo_pause:.1f}s)")
            time.sleep(inter_repo_pause)

    print("\nColeta concluída. Arquivos em", OUTPUT_DIR)


if __name__ == "__main__":
    main()

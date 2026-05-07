"""Lab03S01 - coleta de Pull Requests dos repositórios selecionados.

  - state: MERGED ou CLOSED;
  - reviews.totalCount >= 1;
  - (closedAt|mergedAt) - createdAt >= 1 hora.

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
PAGE_SIZE = 30            # listagem leve — pode ser maior, mas 30 é seguro contra 502
DETAILS_BATCH_SIZE = 10   # quantos PRs detalhar por request (batch via aliases)
MIN_REVIEW_HOURS = 1      # filtro de tempo mínimo de revisão
MAX_RETRIES = 10

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
    """Filtros do enunciado: >=1 review e tempo de revisão >= 1h."""
    if pr["reviews"]["totalCount"] < 1:
        return False

    created = parse_iso(pr["createdAt"])
    end = parse_iso(pr.get("mergedAt") or pr.get("closedAt"))
    if not created or not end:
        return False

    delta_hours = (end - created).total_seconds() / 3600
    return delta_hours >= MIN_REVIEW_HOURS


def fetch_pr_details(token, owner, name, numbers):
    """Fase 2: busca campos pesados (additions/deletions/body/...) em batch via aliases."""
    detalhes = []
    for i in range(0, len(numbers), DETAILS_BATCH_SIZE):
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


def fetch_prs_for_repo(token, owner, name):
    """Pagina sobre PRs MERGED/CLOSED (query leve), filtra, depois busca detalhes em batch."""
    aprovados_numbers = []
    total_vistos = 0
    cursor = None
    has_next = True

    # Fase 1: listagem leve + filtragem
    while has_next:
        variables = {
            "owner": owner,
            "name": name,
            "cursor": cursor,
            "first": PAGE_SIZE,
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

        cursor = page_info["endCursor"]
        has_next = page_info["hasNextPage"]

        time.sleep(0.4 + random.uniform(0, 0.3))

    # Fase 2: detalhes só dos aprovados
    print(f"   listagem: {total_vistos} vistos, {len(aprovados_numbers)} aprovados — buscando detalhes...")
    selecionados = fetch_pr_details(token, owner, name, aprovados_numbers)

    return selecionados, total_vistos


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
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Erro: {args.input} não encontrado.", file=sys.stderr)
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
        prs, total_vistos = fetch_prs_for_repo(token, owner, name)

        payload = {
            "repo": nwo,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "total_prs_vistos": total_vistos,
            "total_prs_filtrados": len(prs),
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

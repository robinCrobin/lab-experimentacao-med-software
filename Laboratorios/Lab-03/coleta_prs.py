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
import argparse
from pathlib import Path
from datetime import datetime, timezone

import requests
import pandas as pd
from dotenv import load_dotenv

GRAPHQL_URL = "https://api.github.com/graphql"
TIMEOUT = 60
PAGE_SIZE = 50            # PRs por página (max 100, mas 50 é mais seguro)
MIN_REVIEW_HOURS = 1      # filtro de tempo mínimo de revisão

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


PR_QUERY = """
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
        title
        state
        createdAt
        closedAt
        mergedAt
        additions
        deletions
        changedFiles
        bodyText
        body
        reviews { totalCount }
        comments { totalCount }
        participants { totalCount }
      }
    }
  }
}
"""


def graphql_request(token, variables, max_attempts=6):
    """POST na API GraphQL com retry para erros transientes e rate limit."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"query": PR_QUERY, "variables": variables}

    for attempt in range(max_attempts):
        try:
            resp = requests.post(
                GRAPHQL_URL, json=payload, headers=headers, timeout=TIMEOUT
            )

            # Rate limit secundário
            if resp.status_code == 403 and "rate limit" in resp.text.lower():
                wait = 60 * (attempt + 1)
                print(f"  rate limit atingido. Aguardando {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue

            if resp.status_code in {502, 503, 504}:
                wait = 5 * (attempt + 1)
                print(f"  HTTP {resp.status_code}. Retry em {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue

            if resp.status_code != 200:
                print(f"  HTTP {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
                return None

            data = resp.json()
            if "errors" in data:
                # Pode ser timeout do GraphQL — tenta novamente
                print(f"  Erro GraphQL: {data['errors']}", file=sys.stderr)
                time.sleep(5 * (attempt + 1))
                continue
            return data["data"]

        except requests.RequestException as e:
            print(f"  Erro de conexão: {e}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))

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


def fetch_prs_for_repo(token, owner, name):
    """Pagina sobre todos os PRs MERGED/CLOSED do repo, aplicando os filtros."""
    selecionados = []
    total_vistos = 0
    cursor = None
    has_next = True

    while has_next:
        variables = {
            "owner": owner,
            "name": name,
            "cursor": cursor,
            "first": PAGE_SIZE,
        }
        data = graphql_request(token, variables)
        if data is None or data.get("repository") is None:
            print(f"  falha ao buscar página de {owner}/{name}", file=sys.stderr)
            break

        prs = data["repository"]["pullRequests"]
        nodes = prs["nodes"]
        page_info = prs["pageInfo"]

        for pr in nodes:
            total_vistos += 1
            if passes_filters(pr):
                selecionados.append(pr)

        cursor = page_info["endCursor"]
        has_next = page_info["hasNextPage"]

        # pequena pausa para não estressar a API
        time.sleep(0.3)

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

    print("\nColeta concluída. Arquivos em", OUTPUT_DIR)


if __name__ == "__main__":
    main()

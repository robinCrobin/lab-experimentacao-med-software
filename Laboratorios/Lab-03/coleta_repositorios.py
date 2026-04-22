import os
import sys
import json
import time
import argparse
from pathlib import Path

import requests
import pandas as pd
from dotenv import load_dotenv

GRAPHQL_URL = "https://api.github.com/graphql"
TIMEOUT = 60

TARGET_REPOS = 200
MIN_PRS = 100
PAGE_SIZE = 25

DATA_DIR = Path(__file__).parent / "data"
JSON_PATH = DATA_DIR / "repositorios.json"
CSV_PATH = DATA_DIR / "repositorios.csv"

load_dotenv()


def get_token():
    """Lê o token de acesso do GitHub da variável de ambiente GITHUB_TOKEN."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: defina GITHUB_TOKEN.", file=sys.stderr)
        sys.exit(1)
    return token


def build_query():
    """Query GraphQL: top repositórios por estrelas, contando PRs MERGED e CLOSED."""
    return """
    query TopRepos($cursor: String, $first: Int!) {
      search(
        query: "stars:>10000 sort:stars-desc"
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
            name
            nameWithOwner
            url
            stargazerCount
            primaryLanguage { name }
            mergedPRs: pullRequests(states: MERGED) { totalCount }
            closedPRs: pullRequests(states: CLOSED) { totalCount }
          }
        }
      }
    }
    """


def fetch_page(token, cursor=None, max_attempts=5):
    """Busca uma página da API GraphQL, com retry para erros temporários."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "query": build_query(),
        "variables": {"cursor": cursor, "first": PAGE_SIZE},
    }

    for attempt in range(max_attempts):
        try:
            response = requests.post(
                GRAPHQL_URL, json=payload, headers=headers, timeout=TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    print("Erro GraphQL:", data["errors"], file=sys.stderr)
                    sys.exit(1)
                return data["data"]["search"]

            if response.status_code in {502, 503, 504}:
                wait = 5 * (attempt + 1)
                print(
                    f"Erro {response.status_code}. Tentando novamente em {wait}s...",
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue

            print(
                f"Erro HTTP {response.status_code}: {response.text}", file=sys.stderr
            )
            sys.exit(1)

        except requests.RequestException as e:
            print(f"Erro de conexão: {e}", file=sys.stderr)
            time.sleep(5)

    print("Máximo de tentativas atingido.", file=sys.stderr)
    sys.exit(1)


def fetch_repositories(token, target=TARGET_REPOS, min_prs=MIN_PRS):
    """Coleta repos populares até obter `target` que satisfaçam MERGED+CLOSED >= min_prs."""
    selecionados = []
    descartados = 0
    cursor = None
    has_next = True

    print(f"Coletando até {target} repositórios com >= {min_prs} PRs (MERGED+CLOSED).")

    while has_next and len(selecionados) < target:
        result = fetch_page(token, cursor)
        nodes = result["nodes"]
        page_info = result["pageInfo"]

        for repo in nodes:
            merged = repo.get("mergedPRs", {}).get("totalCount", 0)
            closed = repo.get("closedPRs", {}).get("totalCount", 0)
            total_prs = merged + closed
            repo["mergedPRsCount"] = merged
            repo["closedPRsCount"] = closed
            repo["totalPRs"] = total_prs

            if total_prs >= min_prs:
                selecionados.append(repo)
                if len(selecionados) >= target:
                    break
            else:
                descartados += 1

        cursor = page_info["endCursor"]
        has_next = page_info["hasNextPage"]

        print(
            f"  selecionados={len(selecionados)} | descartados (PRs<{min_prs})={descartados}"
        )

    print(f"\nColeta finalizada. {len(selecionados)} repositórios selecionados.")
    return selecionados


def to_dataframe(repos):
    """Normaliza a lista de repositórios em um DataFrame com as colunas relevantes."""
    df = pd.json_normalize(repos)
    df = df.rename(
        columns={
            "primaryLanguage.name": "primary_language",
            "stargazerCount": "stars",
        }
    )
    cols = [
        "nameWithOwner",
        "name",
        "url",
        "stars",
        "primary_language",
        "mergedPRsCount",
        "closedPRsCount",
        "totalPRs",
    ]
    return df[cols]


def main():
    parser = argparse.ArgumentParser(
        description="Coleta os 200 repositórios mais populares com >=100 PRs (MERGED+CLOSED)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--fetch",
        action="store_true",
        help="Faz a coleta via GitHub API e salva JSON+CSV em data/.",
    )
    group.add_argument(
        "--analyze",
        action="store_true",
        help="Apenas (re)gera o CSV a partir do JSON já existente.",
    )
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if args.fetch:
        token = get_token()
        repos = fetch_repositories(token)
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(repos, f, ensure_ascii=False, indent=2)
        print(f"JSON salvo em {JSON_PATH}")

        df = to_dataframe(repos)
        df.to_csv(CSV_PATH, index=False)
        print(f"CSV salvo em {CSV_PATH}")
        print(df.head().to_string(index=False))

    else:
        if not JSON_PATH.exists():
            print(
                f"Erro: {JSON_PATH} não encontrado. Rode com --fetch primeiro.",
                file=sys.stderr,
            )
            sys.exit(1)
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            repos = json.load(f)
        df = to_dataframe(repos)
        df.to_csv(CSV_PATH, index=False)
        print(f"CSV salvo em {CSV_PATH}")
        print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()

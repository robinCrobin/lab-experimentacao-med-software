import os
import sys
import json
import time
import random
import argparse
from pathlib import Path

import requests
import pandas as pd
from dotenv import load_dotenv

GRAPHQL_URL = "https://api.github.com/graphql"
TIMEOUT = 60

TARGET_REPOS = 200
MIN_PRS = 100
PAGE_SIZE = 100
MAX_RETRIES = 8

DATA_DIR = Path(__file__).parent / "data"
JSON_PATH = DATA_DIR / "repositorios.json"
CSV_PATH = DATA_DIR / "repositorios.csv"

load_dotenv()

TOP_REPOS_QUERY = """
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


def get_token():
    """Lê o token de acesso do GitHub da variável de ambiente GITHUB_TOKEN."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: defina GITHUB_TOKEN.", file=sys.stderr)
        sys.exit(1)
    return token


def fetch_page(token, cursor=None, page_size=PAGE_SIZE, max_attempts=MAX_RETRIES):
    """Busca uma página da API GraphQL, com retry para erros temporários."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "query": TOP_REPOS_QUERY,
        "variables": {"cursor": cursor, "first": page_size},
    }

    for attempt in range(max_attempts):
        try:
            response = requests.post(
                GRAPHQL_URL, json=payload, headers=headers, timeout=TIMEOUT
            )

            remaining = response.headers.get("X-RateLimit-Remaining", "?")
            reset = response.headers.get("X-RateLimit-Reset", "?")
            if remaining == "0":
                reset_time = int(reset) if reset != "?" else 0
                wait = max(reset_time - int(time.time()), 60)
                print(
                    f"Rate limit primário atingido. Aguardando {wait}s...",
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue

            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    error_msg = str(data["errors"]).lower()
                    if "timeout" in error_msg or "deadline exceeded" in error_msg:
                        wait = min(2 ** attempt * 3, 60) + random.uniform(0, 0.3)
                        print(
                            f"Timeout GraphQL. Retry em {wait:.1f}s...",
                            file=sys.stderr,
                        )
                        time.sleep(wait)
                        continue
                    print("Erro GraphQL:", data["errors"], file=sys.stderr)
                    return None
                return data["data"]["search"]

            if response.status_code == 403 and "rate limit" in response.text.lower():
                wait = min(2 ** attempt * 10, 300) + random.uniform(0, 1.0)
                print(
                    f"Rate limit secundário. Retry em {wait:.1f}s...",
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue

            if response.status_code in {502, 503, 504, 429}:
                wait = min(2 ** attempt * 3, 120) + random.uniform(0, 0.5)
                print(
                    f"Erro {response.status_code}. Tentando novamente em {wait:.1f}s...",
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue

            print(
                f"Erro HTTP {response.status_code}: {response.text}", file=sys.stderr
            )
            return None

        except requests.RequestException as e:
            wait = min(2 ** attempt * 3, 60) + random.uniform(0, 0.5)
            print(f"Erro de conexão: {e}. Retry em {wait:.1f}s...", file=sys.stderr)
            time.sleep(wait)

    print("Máximo de tentativas atingido.", file=sys.stderr)
    return None


def fetch_repositories(token, target=TARGET_REPOS, min_prs=MIN_PRS, page_size=PAGE_SIZE):
    """Coleta repos populares até obter `target` que satisfaçam MERGED+CLOSED >= min_prs."""
    selecionados = []
    descartados = 0
    cursor = None
    has_next = True

    print(f"Coletando até {target} repositórios com >= {min_prs} PRs (MERGED+CLOSED).")

    while has_next and len(selecionados) < target:
        result = fetch_page(token, cursor, page_size=page_size)
        if result is None:
            print("Falha ao buscar página de repositórios. Encerrando coleta.", file=sys.stderr)
            break
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
    parser.add_argument(
        "--target",
        type=int,
        default=TARGET_REPOS,
        help=f"Quantidade alvo de repositórios selecionados (padrão: {TARGET_REPOS}).",
    )
    parser.add_argument(
        "--min-prs",
        type=int,
        default=MIN_PRS,
        help=f"Mínimo de PRs (MERGED+CLOSED) por repositório (padrão: {MIN_PRS}).",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=PAGE_SIZE,
        help=f"Tamanho da página na busca GraphQL (1 a 100, padrão: {PAGE_SIZE}).",
    )
    args = parser.parse_args()

    if args.target < 1:
        print("Erro: --target deve ser >= 1.", file=sys.stderr)
        sys.exit(1)
    if args.min_prs < 0:
        print("Erro: --min-prs deve ser >= 0.", file=sys.stderr)
        sys.exit(1)
    if not 1 <= args.page_size <= 100:
        print("Erro: --page-size deve estar entre 1 e 100.", file=sys.stderr)
        sys.exit(1)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if args.fetch:
        token = get_token()
        repos = fetch_repositories(
            token,
            target=args.target,
            min_prs=args.min_prs,
            page_size=args.page_size,
        )
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

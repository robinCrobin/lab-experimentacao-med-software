"""Coleta a lista de objetos experimentais (repositórios populares do GitHub).

Usa a API GraphQL de busca do GitHub para obter os repositórios com mais
estrelas e salva o owner/name de cada um em ``data/repositorios.json``.
Essa lista é a entrada do ``benchmark.py``.

Uso:
    python coletar_repos.py [--n 100]
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

GRAPHQL_URL = "https://api.github.com/graphql"
TIMEOUT = 60
PAGE_SIZE = 50

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
JSON_PATH = DATA_DIR / "repositorios.json"

load_dotenv(ROOT / ".env")


def get_token():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: defina GITHUB_TOKEN (veja .env.example).", file=sys.stderr)
        sys.exit(1)
    return token


SEARCH_QUERY = """
query TopRepos($cursor: String, $first: Int!) {
  search(query: "stars:>10000 sort:stars-desc", type: REPOSITORY, first: $first, after: $cursor) {
    pageInfo { endCursor hasNextPage }
    nodes {
      ... on Repository {
        name
        owner { login }
        nameWithOwner
        stargazerCount
      }
    }
  }
}
"""


def fetch_page(token, cursor=None, max_attempts=5):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"query": SEARCH_QUERY, "variables": {"cursor": cursor, "first": PAGE_SIZE}}
    for attempt in range(max_attempts):
        try:
            resp = requests.post(GRAPHQL_URL, json=payload, headers=headers, timeout=TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                if "errors" in data:
                    print("Erro GraphQL:", data["errors"], file=sys.stderr)
                    sys.exit(1)
                return data["data"]["search"]
            if resp.status_code in {502, 503, 504}:
                wait = 5 * (attempt + 1)
                print(f"Erro {resp.status_code}. Retentando em {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"Erro HTTP {resp.status_code}: {resp.text}", file=sys.stderr)
            sys.exit(1)
        except requests.RequestException as e:
            print(f"Erro de conexão: {e}", file=sys.stderr)
            time.sleep(5)
    print("Máximo de tentativas atingido.", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Coleta repositórios populares (objetos experimentais).")
    parser.add_argument("--n", type=int, default=100, help="Quantidade de repositórios (padrão: 100).")
    args = parser.parse_args()

    token = get_token()
    repos = []
    cursor = None
    has_next = True

    print(f"Coletando até {args.n} repositórios populares...")
    while has_next and len(repos) < args.n:
        result = fetch_page(token, cursor)
        for node in result["nodes"]:
            repos.append(
                {
                    "owner": node["owner"]["login"],
                    "name": node["name"],
                    "nameWithOwner": node["nameWithOwner"],
                    "stargazerCount": node["stargazerCount"],
                }
            )
        cursor = result["pageInfo"]["endCursor"]
        has_next = result["pageInfo"]["hasNextPage"]
        print(f"  coletados: {len(repos)}")

    repos = repos[: args.n]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(repos, f, ensure_ascii=False, indent=2)
    print(f"\n{len(repos)} repositórios salvos em {JSON_PATH}")


if __name__ == "__main__":
    main()

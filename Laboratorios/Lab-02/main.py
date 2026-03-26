import argparse
import csv
import json
import os
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


def main():
    parser = argparse.ArgumentParser(description="Lab 02")
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Executa a extração e salva os Top Java repos em data/top_java_repos.csv",
    )

    args = parser.parse_args()

    if args.extract:
        run_extract()
        return

    parser.print_help()


if __name__ == "__main__":
    main()

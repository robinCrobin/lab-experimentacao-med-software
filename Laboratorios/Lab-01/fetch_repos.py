import os
import sys
import requests
import json
import time
from datetime import datetime, timezone
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import argparse

GRAPHQL_URL = "https://api.github.com/graphql"
TIMEOUT = 60

TARGET_REPOS = 1000
PAGE_SIZE = 10

DATA_DIR = Path(__file__).parent / "data"
JSON_PATH = DATA_DIR / "repositorios.json"

load_dotenv()

def get_token():
    """Lê o token de acesso do GitHub da variável de ambiente GITHUB_TOKEN."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: defina GITHUB_TOKEN.")
        sys.exit(1)
    return token

def build_query():
    """Monta e retorna a query GraphQL usada para buscar os repositórios com mais estrelas."""
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
            createdAt
            pushedAt
            primaryLanguage {
              name
            }
            pullRequests(states: MERGED) {
              totalCount
            }
            releases {
              totalCount
            }
            issues {
              totalCount
            }
            closedIssues: issues(states: CLOSED) {
              totalCount
            }
          }
        }
      }
    }
    """

def fetch_page(token, cursor=None, max_attempts=5):
  """Busca uma página de repositórios na API GraphQL do GitHub usando o cursor informado.
  Implementa retry para erros temporários e tratamento de exceções de rede.
  """

  headers = {"Authorization": f"Bearer {token}"}
  payload = {
    "query": build_query(),
    "variables": {
      "cursor": cursor,
      "first": PAGE_SIZE
    }
  }

  for attempt in range(max_attempts):
    try:
      response = requests.post(
        GRAPHQL_URL,
        json=payload,
        headers=headers,
        timeout=TIMEOUT
      )

      if response.status_code == 200:
        data = response.json()
        if "errors" in data:
          print("Erro GraphQL:", data["errors"], file=sys.stderr)
          sys.exit(1)
        return data["data"]["search"]

      # Tratamento de erros temporários (502, 503, 504)
      if response.status_code in {502, 503, 504}:
        wait = 5 * (attempt + 1)
        print(f"Erro {response.status_code}. Tentando novamente em {wait}s...", file=sys.stderr)
        time.sleep(wait)
        continue
      else:
        print(f"Erro HTTP {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)

    except requests.RequestException as e:
      print(f"Erro de conexão: {e}", file=sys.stderr)
      # aguarda um tempo antes de tentar novamente
      time.sleep(5)

  # Se esgotaram-se as tentativas, aborta com erro
  print("Máximo de tentativas atingido.", file=sys.stderr)
  sys.exit(1)

def analyze_from_json():
    """"Lê o arquivo JSON salvo, normaliza os dados e calcula métricas adicionais como idade do repositório e razão de issues fechadas."""
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        repos = json.load(f)

    df = pd.json_normalize(repos)

    df = df[[
        "name",
        "nameWithOwner",
        "url",
        "createdAt",
        "pushedAt",
        "primaryLanguage.name",
        "pullRequests.totalCount",
        "releases.totalCount",
        "issues.totalCount",
        "closedIssues.totalCount",
    ]]

    df = df.rename(columns={
        "primaryLanguage.name": "primary_language",
        "pullRequests.totalCount": "pull_requests_total",
        "releases.totalCount": "releases_total",
        "issues.totalCount": "issues_total",
        "closedIssues.totalCount": "closed_issues_total",
    })

    df["createdAt"] = pd.to_datetime(df["createdAt"], utc=True)
    df["pushedAt"] = pd.to_datetime(df["pushedAt"], utc=True)

    now = datetime.now(timezone.utc)

    df["repo_age_days"] = (now - df["createdAt"]).dt.days
    df["days_since_last_update"] = (now - df["pushedAt"]).dt.days
    df["closed_issues_ratio"] = df["closed_issues_total"] / df["issues_total"]

    df = df.drop(columns=["createdAt", "pushedAt"])

    return df

def save_processed_csv(df, filename="repositorios_processados.csv"):
        """Salva o DataFrame em CSV dentro de DATA_DIR e retorna o path salvo."""
        processed_path = DATA_DIR / filename
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(processed_path, index=False)
        return processed_path

def main():
    """Opções: --fetch para coletar e salvar; --analyze para apenas analisar o JSON existente."""

    parser = argparse.ArgumentParser(description="Coletar ou analisar repositórios.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fetch", action="store_true", help="Fazer a extração dos dados e salvar em data/repositorios.json")
    group.add_argument("--analyze", action="store_true", help="Apenas analisar o arquivo data/repositorios.json")
    args = parser.parse_args()

    if args.fetch:
      token = get_token()
      all_repos = []
      cursor = None
      has_next = True

      print("Iniciando coleta")

      while has_next and len(all_repos) < TARGET_REPOS:
        result = fetch_page(token, cursor)

        nodes = result["nodes"]
        page_info = result["pageInfo"]

        all_repos.extend(nodes)

        cursor = page_info["endCursor"]
        has_next = page_info["hasNextPage"]

        print(f"Coletados até agora: {len(all_repos)}")

      print("\nColeta finalizada. Total de repositórios coletados:", len(all_repos))

      # Persistir resultados
      DATA_DIR.mkdir(parents=True, exist_ok=True)
      with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_repos[:TARGET_REPOS], f, ensure_ascii=False, indent=2)
      print(f"Dados salvos em {JSON_PATH}")

    elif args.analyze:
      if not JSON_PATH.exists():
        print(f"Erro: arquivo {JSON_PATH} não encontrado. Rode com --fetch primeiro.", file=sys.stderr)
        sys.exit(1)

      df = analyze_from_json()
      processed_path = save_processed_csv(df)
      print(f"Análise concluída. Arquivo de saída: {processed_path}")
      # Mostrar resumo rápido
      print(df.head().to_string(index=False))

if __name__ == "__main__":
    main()
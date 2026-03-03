import os
import sys
import requests
import json
from dotenv import load_dotenv

GRAPHQL_URL = "https://api.github.com/graphql"
TIMEOUT = 30

TARGET_REPOS = 100
PAGE_SIZE = 10

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

def fetch_page(token, cursor=None):
    """Busca uma página de repositórios na API GraphQL do GitHub usando o cursor informado."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "query": build_query(),
        "variables": {
            "cursor": cursor,
            "first": PAGE_SIZE
        }
    }

    response = requests.post(GRAPHQL_URL, json=payload, headers=headers, timeout=TIMEOUT)

    if response.status_code != 200:
        print(f"Erro HTTP {response.status_code}: {response.text}")
        sys.exit(1)

    data = response.json()

    if "errors" in data:
        print("Erro GraphQL:", data["errors"])
        sys.exit(1)

    return data["data"]["search"]


def main():
    """Coleta até 100 repositórios populares e salva os dados em um arquivo JSON na pasta data/."""
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

    # Persistência dos dados coletados
    import os
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    json_path = os.path.join(data_dir, "repositorios.json")
    with open(json_path, "w", encoding="utf-8") as f:
        # Salva apenas os primeiros 100 repositórios
        json.dump(all_repos[:100], f, ensure_ascii=False, indent=2)
    print(f"Dados salvos em {json_path} (100 repositórios)")
    print("\n Operação concluída com sucesso! Os dados dos 100 repositórios mais populares foram salvos em formato JSON na pasta 'data/'.")
    
    # Validação simples de integridade
    with open(json_path, "r", encoding="utf-8") as f:
        repos = json.load(f)
    valid = len(repos) == 100 and all("name" in r and "url" in r for r in repos)
    if valid:
      print("\nValidação: arquivo contém 100 repositórios com campos essenciais.")
    else:
      print("\nValidação: arquivo não está íntegro. Verifique a coleta.")

if __name__ == "__main__":
    main()
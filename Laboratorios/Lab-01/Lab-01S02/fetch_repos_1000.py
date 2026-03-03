import os
import sys
import csv
import time
import requests
from pathlib import Path

# Configurações de Coleta
GRAPHQL_URL = "https://api.github.com/graphql"
TOTAL_REPOS = 1000
# Configurações ultra-estáveis
BATCH_SIZE = 10  # Lote mínimo para garantir estabilidade
PAGES = 100      # 100 páginas de 10 = 1000 repositórios

QUERY = """
query TopRepos($cursor: String, $first: Int) {
  search(
    query: "stars:>1 sort:stars-desc"
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
        primaryLanguage { name }
        pullRequests(states: MERGED) { totalCount }
        releases { totalCount }
        issues { totalCount }
        issuesClosed: issues(states: CLOSED) { totalCount }
      }
    }
  }
}
"""


DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
def get_output_csv_path():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return DATA_DIR / f"repositorios_1000_{timestamp}.csv"
FIELDS = [
    "name", "nameWithOwner", "url", "stargazerCount", "createdAt", "pushedAt",
    "primaryLanguage", "pullRequestsMerged", "releasesTotal", "issuesTotal", "issuesClosed"
]

def get_github_token():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: defina a variável de ambiente GITHUB_TOKEN.", file=sys.stderr)
        sys.exit(1)
    return token

def fetch_page(token, cursor=None, max_retries=5):
    variables = {"cursor": cursor, "first": BATCH_SIZE}
    headers = {"Authorization": f"Bearer {token}"}
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                GRAPHQL_URL, 
                json={"query": QUERY, "variables": variables}, 
                headers=headers, 
                timeout=60 # Timeout estendido
            )
            
            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    print(f"Erro na query: {data['errors'][0]['message']}", file=sys.stderr)
                    return None
                return data
            
            # Tratamento de erros temporários (502, 503, 504)
            if response.status_code in {502, 503, 504}:
                wait = 5 * (attempt + 1)
                print(f"Erro {response.status_code}. Tentando novamente em {wait}s...", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"Erro HTTP {response.status_code}: {response.text}", file=sys.stderr)
                sys.exit(1)
                
        except requests.RequestException as e:
            print(f"Erro de conexão: {e}", file=sys.stderr)
            time.sleep(5)
            
    return None

def parse_node(node):
    return {
        "name": node.get("name"),
        "nameWithOwner": node.get("nameWithOwner"),
        "url": node.get("url"),
        "stargazerCount": node.get("stargazerCount"),
        "createdAt": node.get("createdAt"),
        "pushedAt": node.get("pushedAt"),
        "primaryLanguage": (node.get("primaryLanguage") or {}).get("name"),
        "pullRequestsMerged": (node.get("pullRequests") or {}).get("totalCount"),
        "releasesTotal": (node.get("releases") or {}).get("totalCount"),
        "issuesTotal": (node.get("issues") or {}).get("totalCount"),
        "issuesClosed": (node.get("issuesClosed") or {}).get("totalCount"),
    }

def main():
    token = get_github_token()
    all_repos = []
    cursor = None

    print(f"Iniciando coleta de {TOTAL_REPOS} repositórios (lotes de {BATCH_SIZE})...")

    for page in range(PAGES):
        print(f"Página {page+1}/{PAGES}...", end="\r")
        data = fetch_page(token, cursor)
        
        if not data:
            print(f"\nFalha ao obter a página {page+1}. Encerrando com {len(all_repos)} itens.")
            break

        search = data["data"]["search"]
        for node in search["nodes"]:
            if node: # Garante que o nó não é nulo
                all_repos.append(parse_node(node))
        
        page_info = search["pageInfo"]
        cursor = page_info["endCursor"]
        
        if not page_info["hasNextPage"] or len(all_repos) >= TOTAL_REPOS:
            break
        
        time.sleep(1) # Delay preventivo para rate limit

    # Salva no CSV na pasta data com timestamp
    output_csv = get_output_csv_path()
    with open(output_csv, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(all_repos[:TOTAL_REPOS])

    print(f"\nSucesso! {len(all_repos[:TOTAL_REPOS])} repositórios salvos em: {output_csv}")

if __name__ == "__main__":
    main()

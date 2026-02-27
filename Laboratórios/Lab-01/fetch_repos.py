import os
import sys
import requests
import json
from dotenv import load_dotenv

GRAPHQL_URL = "https://api.github.com/graphql"
TIMEOUT = 30

TARGET_REPOS = 100

load_dotenv()


def get_token():
    """Lê o token de acesso do GitHub da variável de ambiente GITHUB_TOKEN."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: defina GITHUB_TOKEN.")
        sys.exit(1)
    return token


def build_search_query():
    """Monta a query GraphQL para buscar os 100 repositórios mais estrelados (dados básicos)."""
    return """
    query TopRepos($first: Int!) {
      search(
        query: "stars:>10000 sort:stars-desc"
        type: REPOSITORY
        first: $first
      ) {
        nodes {
          ... on Repository {
            name
            nameWithOwner
            url
          }
        }
      }
    }
    """


def build_repo_detail_query():
    """Monta a query GraphQL para buscar os detalhes de um repositório específico."""
    return """
    query RepoDetails($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
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
    """


def graphql_request(token, query, variables):
    """Envia uma requisição GraphQL genérica e trata erros básicos."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"query": query, "variables": variables}

    response = requests.post(GRAPHQL_URL, json=payload, headers=headers, timeout=TIMEOUT)

    if response.status_code != 200:
        print(f"Erro HTTP {response.status_code}: {response.text}")
        sys.exit(1)

    data = response.json()

    if "errors" in data:
        print("Erro GraphQL:", data["errors"])
        sys.exit(1)

    return data["data"]


def fetch_top_repos(token):
    """Busca os 100 repositórios mais populares (apenas campos básicos)."""
    query = build_search_query()
    data = graphql_request(token, query, {"first": TARGET_REPOS})
    nodes = data["search"]["nodes"]
    # Garante que só usaremos no máximo TARGET_REPOS
    return nodes[:TARGET_REPOS]


def fetch_repo_details(token, name_with_owner):
    """Busca os detalhes completos de um repositório a partir de seu nameWithOwner."""
    owner, name = name_with_owner.split("/")
    query = build_repo_detail_query()
    data = graphql_request(token, query, {"owner": owner, "name": name})
    return data["repository"]


def main():
    """Coleta até 100 repositórios populares e salva os dados em um arquivo JSON na pasta data/."""
    token = get_token()

    print("Buscando lista de repositórios populares (dados básicos)...")
    basic_repos = fetch_top_repos(token)
    print(f"Foram obtidos {len(basic_repos)} repositórios básicos.")

    all_repos = []

    print("Buscando detalhes de cada repositório...")
    for idx, repo in enumerate(basic_repos, start=1):
        name_with_owner = repo["nameWithOwner"]
        details = fetch_repo_details(token, name_with_owner)
        all_repos.append(details)
        print(f"[{idx}/{len(basic_repos)}] Detalhes obtidos para {name_with_owner}")

    print("\nColeta finalizada. Total de repositórios coletados:", len(all_repos))

    # Persistência dos dados coletados
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    json_path = os.path.join(data_dir, "repositorios.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_repos[:TARGET_REPOS], f, ensure_ascii=False, indent=2)
    print(f"Dados salvos em {json_path} ({len(all_repos[:TARGET_REPOS])} repositórios)")
    print("\nOperação concluída com sucesso! Os dados dos repositórios mais populares foram salvos em formato JSON na pasta 'data/'.")
    print("Você pode utilizar esse arquivo para análises futuras ou integração com outros experimentos.")

    # Validação simples de integridade
    with open(json_path, "r", encoding="utf-8") as f:
        repos = json.load(f)
    valid = len(repos) == TARGET_REPOS and all("name" in r and "url" in r for r in repos)
    if valid:
        print("\nValidação: arquivo contém 100 repositórios com campos essenciais.")
    else:
        print("\nValidação: arquivo não está íntegro. Verifique a coleta.")


if __name__ == "__main__":
    main()
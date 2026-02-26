import os
import sys
import requests
from dotenv import load_dotenv

GRAPHQL_URL = "https://api.github.com/graphql"
TIMEOUT = 30

TARGET_REPOS = 100
PAGE_SIZE = 10

load_dotenv()

def get_token():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: defina GITHUB_TOKEN.")
        sys.exit(1)
    return token

def build_query():
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
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "query": build_query(),
        "variables": {
            "cursor": cursor,
            "first": PAGE_SIZE
        }
    }

    response = requests.post(GRAPHQL_URL, json=payload, headers=headers)

    if response.status_code != 200:
        print(f"Erro HTTP {response.status_code}: {response.text}")
        sys.exit(1)

    data = response.json()

    if "errors" in data:
        print("Erro GraphQL:", data["errors"])
        sys.exit(1)

    return data["data"]["search"]

def main():
    token = get_token()

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "query":"{ viewer { login } }"
    }

    response = requests.post(
                GRAPHQL_URL,
                json=payload,
                headers=headers,
                timeout=TIMEOUT
    )

    if response.status_code != 200:
                print(f"Erro HTTP {response.status_code}: {response.text}")
                sys.exit(1)

    data = response.json()
    print(data)

if __name__ == "__main__":
    main()
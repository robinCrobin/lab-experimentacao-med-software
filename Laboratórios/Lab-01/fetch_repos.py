import os
import sys
import requests
from dotenv import load_dotenv

GRAPHQL_URL = "https://api.github.com/graphql"
TIMEOUT = 30

load_dotenv()

def get_token():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: defina GITHUB_TOKEN.")
        sys.exit(1)
    return token

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
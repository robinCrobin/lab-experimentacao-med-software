import os
import sys
from dotenv import load_dotenv

load_dotenv()

def get_token():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: defina GITHUB_TOKEN.")
        sys.exit(1)
    return token

def main():
    token = get_token()
    print(token)

if __name__ == "__main__":
    main()
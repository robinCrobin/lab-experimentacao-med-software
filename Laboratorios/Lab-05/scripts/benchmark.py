"""Execução do experimento (Passo 3): aplica os tratamentos REST e GraphQL.

Para cada repositório de ``data/repositorios.json`` aplica os dois tratamentos
(REST e GraphQL) solicitando exatamente os mesmos campos, com uma requisição de
aquecimento (descartada) e ``--rep`` repetições medidas. A ordem dos
tratamentos é intercalada por repetição para mitigar efeitos temporais.

Mede, por requisição:
  - tempo_ms       : latência ponta a ponta (ms)
  - tamanho_bytes  : tamanho do corpo da resposta (bytes)

Saída: ``data/medicoes.csv`` (uma linha por requisição medida).

Uso:
    python benchmark.py [--rep 5] [--limit N] [--pausa 0.2]
"""

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

REST_BASE = "https://api.github.com/repos"
GRAPHQL_URL = "https://api.github.com/graphql"
TIMEOUT = 60

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPOS_PATH = DATA_DIR / "repositorios.json"
OUT_PATH = DATA_DIR / "medicoes.csv"

load_dotenv(ROOT / ".env")

# Query GraphQL que solicita EXATAMENTE os mesmos campos consumidos da resposta
# REST (mesma necessidade de informação), garantindo comparação justa.
GRAPHQL_QUERY = """
query Repo($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    name
    owner { login }
    description
    stargazerCount
    forkCount
    watchers { totalCount }
    issues(states: OPEN) { totalCount }
    primaryLanguage { name }
    createdAt
    updatedAt
    pushedAt
    diskUsage
    licenseInfo { spdxId }
    defaultBranchRef { name }
    homepageUrl
    repositoryTopics(first: 20) { nodes { topic { name } } }
  }
}
"""


def get_token():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Erro: defina GITHUB_TOKEN (veja .env.example).", file=sys.stderr)
        sys.exit(1)
    return token


def medir_rest(session, owner, name):
    """Executa o tratamento REST e retorna (tempo_ms, tamanho_bytes, ok)."""
    url = f"{REST_BASE}/{owner}/{name}"
    t0 = time.perf_counter()
    resp = session.get(url, timeout=TIMEOUT)
    elapsed = (time.perf_counter() - t0) * 1000.0
    ok = resp.status_code == 200
    size = len(resp.content)
    return elapsed, size, ok, resp.status_code


def medir_graphql(session, owner, name):
    """Executa o tratamento GraphQL e retorna (tempo_ms, tamanho_bytes, ok)."""
    payload = {"query": GRAPHQL_QUERY, "variables": {"owner": owner, "name": name}}
    t0 = time.perf_counter()
    resp = session.post(GRAPHQL_URL, json=payload, timeout=TIMEOUT)
    elapsed = (time.perf_counter() - t0) * 1000.0
    body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
    ok = resp.status_code == 200 and "errors" not in body and body.get("data", {}).get("repository") is not None
    size = len(resp.content)
    return elapsed, size, ok, resp.status_code


def main():
    parser = argparse.ArgumentParser(description="Executa o benchmark REST vs GraphQL.")
    parser.add_argument("--rep", type=int, default=5, help="Repetições medidas por (repo, API). Padrão: 5.")
    parser.add_argument("--limit", type=int, default=None, help="Limita a quantidade de repositórios (debug).")
    parser.add_argument("--pausa", type=float, default=0.2, help="Pausa (s) entre requisições. Padrão: 0.2.")
    args = parser.parse_args()

    if not REPOS_PATH.exists():
        print(f"Erro: {REPOS_PATH} não encontrado. Rode coletar_repos.py primeiro.", file=sys.stderr)
        sys.exit(1)

    with open(REPOS_PATH, encoding="utf-8") as f:
        repos = json.load(f)
    if args.limit:
        repos = repos[: args.limit]

    token = get_token()
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "lab05-graphql-vs-rest",
        }
    )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    total = len(repos)
    print(f"Iniciando experimento: {total} repositórios x 2 APIs x {args.rep} repetições.")

    linhas = []
    for i, repo in enumerate(repos, 1):
        owner, name = repo["owner"], repo["name"]
        print(f"[{i}/{total}] {owner}/{name}")

        # Warm-up (descartado) para cada API.
        try:
            medir_rest(session, owner, name)
            medir_graphql(session, owner, name)
        except requests.RequestException as e:
            print(f"  warm-up falhou: {e}", file=sys.stderr)
        time.sleep(args.pausa)

        for r in range(1, args.rep + 1):
            # Intercala a ordem dos tratamentos por repetição.
            ordem = ("REST", "GraphQL") if r % 2 == 1 else ("GraphQL", "REST")
            for api in ordem:
                try:
                    if api == "REST":
                        tempo, tam, ok, status = medir_rest(session, owner, name)
                    else:
                        tempo, tam, ok, status = medir_graphql(session, owner, name)
                except requests.RequestException as e:
                    print(f"  {api} rep{r} erro: {e}", file=sys.stderr)
                    continue
                if not ok:
                    print(f"  {api} rep{r} resposta inesperada (status {status}); ignorada.", file=sys.stderr)
                    continue
                linhas.append(
                    {
                        "repositorio": f"{owner}/{name}",
                        "api": api,
                        "repeticao": r,
                        "tempo_ms": round(tempo, 3),
                        "tamanho_bytes": tam,
                    }
                )
                time.sleep(args.pausa)

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["repositorio", "api", "repeticao", "tempo_ms", "tamanho_bytes"]
        )
        writer.writeheader()
        writer.writerows(linhas)

    print(f"\nConcluído. {len(linhas)} medições salvas em {OUT_PATH}")


if __name__ == "__main__":
    main()

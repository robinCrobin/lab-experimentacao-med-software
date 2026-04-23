"""Lab03S01 - Pessoa 3: extração das métricas dos PRs.

Lê os arquivos JSON gerados pela Pessoa 2 (`data/prs_brutos/*.json`) e
consolida um único `data/dataset_prs.csv` com as métricas exigidas pelas
RQs do enunciado.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "prs_brutos"
OUTPUT_CSV = DATA_DIR / "dataset_prs.csv"


def parse_iso(dt_str):
    if not dt_str:
        return None
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


def pr_to_row(repo, pr):
    """Converte um PR (dict da API) em uma linha do dataset."""
    created = parse_iso(pr["createdAt"])
    end = parse_iso(pr.get("mergedAt") or pr.get("closedAt"))
    analysis_hours = (end - created).total_seconds() / 3600 if created and end else None

    body = pr.get("body") or ""

    return {
        # identificação
        "repo": repo,
        "pr_number": pr["number"],
        "state": pr["state"],                       # MERGED | CLOSED
        "created_at": pr["createdAt"],
        "closed_at": pr.get("closedAt"),
        "merged_at": pr.get("mergedAt"),

        # tamanho
        "files_changed": pr.get("changedFiles"),
        "additions": pr.get("additions"),
        "deletions": pr.get("deletions"),

        # tempo de análise (horas)
        "analysis_time_hours": analysis_hours,

        # descrição (markdown bruto, conforme enunciado)
        "body_length": len(body),

        # interações
        "participants": pr["participants"]["totalCount"],
        "comments": pr["comments"]["totalCount"],

        # número de revisões (alvo das RQs 05–08)
        "reviews_count": pr["reviews"]["totalCount"],
    }


def carrega_prs(input_dir):
    """Itera os JSONs de checkpoint e gera linhas do dataset."""
    arquivos = sorted(input_dir.glob("*.json"))
    if not arquivos:
        print(f"Erro: nenhum JSON encontrado em {input_dir}.", file=sys.stderr)
        sys.exit(1)

    rows = []
    for path in arquivos:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        repo = payload["repo"]
        for pr in payload.get("prs", []):
            rows.append(pr_to_row(repo, pr))
    return rows


def resumo(df):
    print(f"\nDataset: {len(df)} PRs em {df['repo'].nunique()} repositórios.")
    print("\nDistribuição por state:")
    print(df["state"].value_counts().to_string())
    print("\nEstatísticas descritivas:")
    cols = [
        "files_changed",
        "additions",
        "deletions",
        "analysis_time_hours",
        "body_length",
        "participants",
        "comments",
        "reviews_count",
    ]
    print(df[cols].describe().to_string())


def main():
    parser = argparse.ArgumentParser(description="Extrai métricas dos PRs coletados.")
    parser.add_argument("--input-dir", default=str(INPUT_DIR))
    parser.add_argument("--output", default=str(OUTPUT_CSV))
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = carrega_prs(input_dir)
    df = pd.DataFrame(rows)

    # validação mínima: linhas com tempo de análise nulo são suspeitas
    nulos = df["analysis_time_hours"].isna().sum()
    if nulos:
        print(f"Aviso: {nulos} PRs sem analysis_time_hours (descartados).", file=sys.stderr)
        df = df.dropna(subset=["analysis_time_hours"])

    df.to_csv(output_path, index=False)
    print(f"CSV salvo em {output_path}")
    resumo(df)


if __name__ == "__main__":
    main()

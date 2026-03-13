import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"


def main():
    # Carrega os dados já gerados pelo answer_rqs.py
    dist_path = DATA_DIR / "distribuicao_linguagem.csv"
    metrics_path = DATA_DIR / "metricas_por_linguagem.csv"

    dist = pd.read_csv(dist_path)
    metrics = pd.read_csv(metrics_path)

    # Remove linguagem desconhecida
    dist = dist[dist["language"] != "<unknown>"]

    # Pega as TOP 8 linguagens com mais repositórios
    top_langs = (
        dist.sort_values("count", ascending=False)
        .head(8)["language"]
        .tolist()
    )

    metrics_top = metrics[metrics["language"].isin(top_langs)].copy()

    # Garante mesma ordem das linguagens (por popularidade)
    metrics_top["language"] = pd.Categorical(
        metrics_top["language"], categories=top_langs, ordered=True
    )
    metrics_top = metrics_top.sort_values("language")

    # Figura com 3 subplots horizontais
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=False)

    # 1) PRs médios (RQ02)
    axes[0].bar(
        metrics_top["language"],
        metrics_top["mean_pull_requests_total"],
        color="tab:blue",
    )
    axes[0].set_title("RQ02 – PRs mesclados médios por linguagem")
    axes[0].set_xlabel("Linguagem")
    axes[0].set_ylabel("PRs mesclados (média)")
    axes[0].tick_params(axis="x", labelrotation=45)

    # 2) Releases médias (RQ03)
    axes[1].bar(
        metrics_top["language"],
        metrics_top["mean_releases_total"],
        color="tab:orange",
    )
    axes[1].set_title("RQ03 – Releases médias por linguagem")
    axes[1].set_xlabel("Linguagem")
    axes[1].set_ylabel("Releases (média)")
    axes[1].tick_params(axis="x", labelrotation=45)

    # 3) Dias desde última atualização (RQ04)
    axes[2].bar(
        metrics_top["language"],
        metrics_top["mean_days_since_last_update"],
        color="tab:green",
    )
    axes[2].set_title("RQ04 – Dias médios desde a última atualização")
    axes[2].set_xlabel("Linguagem")
    axes[2].set_ylabel("Dias (média)")
    axes[2].tick_params(axis="x", labelrotation=45)

    fig.suptitle("RQ07 – Métricas de atividade por linguagem (Top 8 linguagens)", fontsize=14)
    fig.tight_layout(rect=[0, 0.02, 1, 0.95])

    out_path = DATA_DIR / "rq07_metricas_por_linguagem.png"
    fig.savefig(out_path, dpi=150)
    print(f"Gráfico salvo em: {out_path}")


if __name__ == "__main__":
    main()
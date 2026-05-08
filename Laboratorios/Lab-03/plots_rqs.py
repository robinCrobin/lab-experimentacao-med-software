"""Lab03S03 - Gráficos para as Questões de Pesquisa (RQ 01 a RQ 08).

Lê `data/dataset_prs.csv` (e opcionalmente `data/rqs_correlacoes.csv` para
anotar o rho de Spearman nos títulos) e gera figuras em `figures/`:

  RQ 01-04 (status do PR): boxplots MERGED vs CLOSED para cada métrica.
  RQ 05-08 (nº revisões):  boxplots por faixa de reviews_count para cada métrica.

Métricas com cauda longa (tamanho, tempo, descrição) são plotadas em escala
log no eixo Y para que a comparação visual entre grupos seja legível.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
FIG_DIR = BASE_DIR / "figures"
INPUT_CSV = DATA_DIR / "dataset_prs.csv"
CORR_CSV = DATA_DIR / "rqs_correlacoes.csv"

# (metrica, label, log_scale)
METRICAS_TAMANHO = [
    ("files_changed", "Arquivos alterados", True),
    ("additions",     "Linhas adicionadas", True),
    ("deletions",     "Linhas removidas",   True),
]
METRICAS_TEMPO       = [("analysis_time_hours", "Tempo de análise (horas)", True)]
METRICAS_DESCRICAO   = [("body_length",         "Tamanho da descrição (chars)", True)]
METRICAS_INTERACOES  = [
    ("participants", "Participantes",   False),
    ("comments",     "Comentários",     True),
]

RQS_STATUS = [
    ("RQ01", "Tamanho",          METRICAS_TAMANHO),
    ("RQ02", "Tempo de Análise", METRICAS_TEMPO),
    ("RQ03", "Descrição",        METRICAS_DESCRICAO),
    ("RQ04", "Interações",       METRICAS_INTERACOES),
]
RQS_REVIEWS = [
    ("RQ05", "Tamanho",          METRICAS_TAMANHO),
    ("RQ06", "Tempo de Análise", METRICAS_TEMPO),
    ("RQ07", "Descrição",        METRICAS_DESCRICAO),
    ("RQ08", "Interações",       METRICAS_INTERACOES),
]


def carrega_dataset(path):
    df = pd.read_csv(path)
    df = df.dropna(subset=["state", "reviews_count"])
    df["merged"] = (df["state"] == "MERGED").astype(int)
    df["status_label"] = np.where(df["merged"] == 1, "MERGED", "CLOSED")
    return df


def carrega_correlacoes(path):
    if not path.exists():
        return None
    return pd.read_csv(path)


def rho_de(corr_df, rq, metrica):
    if corr_df is None:
        return None
    sel = corr_df[(corr_df["rq"] == rq) & (corr_df["metrica"] == metrica)]
    if sel.empty:
        return None
    rho = sel.iloc[0]["spearman_rho"]
    p = sel.iloc[0]["p_value"]
    return rho, p


def faixas_reviews(s):
    """Agrupa reviews_count em faixas legíveis para boxplot."""
    bins = [0, 1, 2, 3, 5, 10, np.inf]
    labels = ["1", "2", "3", "4-5", "6-10", "11+"]
    return pd.cut(s, bins=bins, labels=labels, right=True, include_lowest=True)


def plot_status(df, rq, dimensao, metricas, corr_df, out_dir):
    n = len(metricas)
    width = max(7.0, 5.5 * n)
    fig, axes = plt.subplots(1, n, figsize=(width, 5.5), squeeze=False)
    for ax, (col, label, logscale) in zip(axes[0], metricas):
        sub = df[[col, "status_label"]].copy()
        if logscale:
            sub = sub[sub[col] > 0]
        sns.boxplot(
            data=sub, x="status_label", y=col, ax=ax,
            order=["MERGED", "CLOSED"], showfliers=False,
            hue="status_label", legend=False,
            palette={"MERGED": "#4c9f70", "CLOSED": "#c0504d"},
        )
        if logscale:
            ax.set_yscale("log")
        ax.set_xlabel("Status do PR")
        ax.set_ylabel(label)
        info = rho_de(corr_df, rq, col)
        suffix = f"\nρ={info[0]:.3f}  p={info[1]:.2g}" if info else ""
        ax.set_title(f"{label}{suffix}", fontsize=13)
    fig.suptitle(f"{rq} — {dimensao} vs Status do PR", fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    out_path = out_dir / f"{rq.lower()}_{dimensao.lower().replace(' ', '_')}_status.png"
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
    print(f"  -> {out_path.name}")


def plot_reviews(df, rq, dimensao, metricas, corr_df, out_dir):
    df = df.copy()
    df["reviews_faixa"] = faixas_reviews(df["reviews_count"])
    df = df.dropna(subset=["reviews_faixa"])

    n = len(metricas)
    width = max(7.0, 5.5 * n)
    fig, axes = plt.subplots(1, n, figsize=(width, 5.5), squeeze=False)
    for ax, (col, label, logscale) in zip(axes[0], metricas):
        sub = df[[col, "reviews_faixa"]].copy()
        if logscale:
            sub = sub[sub[col] > 0]
        sns.boxplot(
            data=sub, x="reviews_faixa", y=col, ax=ax,
            showfliers=False, color="#4878a6",
        )
        if logscale:
            ax.set_yscale("log")
        ax.set_xlabel("Número de revisões")
        ax.set_ylabel(label)
        info = rho_de(corr_df, rq, col)
        suffix = f"\nρ={info[0]:.3f}  p={info[1]:.2g}" if info else ""
        ax.set_title(f"{label}{suffix}", fontsize=13)
    fig.suptitle(f"{rq} — {dimensao} vs Nº de Revisões", fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    out_path = out_dir / f"{rq.lower()}_{dimensao.lower().replace(' ', '_')}_reviews.png"
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
    print(f"  -> {out_path.name}")


def plot_overview_status(df, out_dir):
    """Gráfico de barras com a contagem de MERGED vs CLOSED."""
    fig, ax = plt.subplots(figsize=(6, 4))
    counts = df["status_label"].value_counts().reindex(["MERGED", "CLOSED"])
    bars = ax.bar(counts.index, counts.values,
                  color=["#4c9f70", "#c0504d"])
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:,}",
                ha="center", va="bottom", fontsize=11)
    ax.set_ylabel("Quantidade de PRs")
    ax.set_title("Distribuição do status final dos PRs")
    fig.tight_layout()
    out_path = out_dir / "overview_status.png"
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
    print(f"  -> {out_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Gráficos das RQs do Lab-03.")
    parser.add_argument("--input", default=str(INPUT_CSV))
    parser.add_argument("--corr",  default=str(CORR_CSV))
    parser.add_argument("--out-dir", default=str(FIG_DIR))
    args = parser.parse_args()

    sns.set_theme(style="whitegrid", context="talk")

    df = carrega_dataset(Path(args.input))
    corr_df = carrega_correlacoes(Path(args.corr))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Dataset: {len(df)} PRs.")
    print("Gerando overview...")
    plot_overview_status(df, out_dir)

    print("Gerando RQ 01-04 (status)...")
    for rq, dim, metricas in RQS_STATUS:
        plot_status(df, rq, dim, metricas, corr_df, out_dir)

    print("Gerando RQ 05-08 (nº revisões)...")
    for rq, dim, metricas in RQS_REVIEWS:
        plot_reviews(df, rq, dim, metricas, corr_df, out_dir)

    print(f"\nFiguras salvas em {out_dir}")


if __name__ == "__main__":
    main()

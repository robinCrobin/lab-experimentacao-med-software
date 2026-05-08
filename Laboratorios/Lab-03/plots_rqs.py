"""Lab03S03 - Gráficos para as Questões de Pesquisa (RQ 01 a RQ 08).

Dois padrões de gráfico, escolhidos pela legibilidade:

  RQ 01-04 (status do PR):
      Boxplot MERGED vs CLOSED para cada métrica (escala log onde aplicável).

  RQ 05-08 (nº de revisões):
      Lineplot da mediana com banda IQR (Q1-Q3) por faixa de reviews_count.

Lê `data/dataset_prs.csv` e (opcional) `data/rqs_correlacoes.csv` para
anotar ρ de Spearman e p-valor nos títulos.
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

PALETTE_STATUS = {"MERGED": "#4c9f70", "CLOSED": "#c0504d"}

# (metrica, label, log_y)
M_TAMANHO = [
    ("files_changed", "Arquivos alterados", True),
    ("additions",     "Linhas adicionadas", True),
    ("deletions",     "Linhas removidas",   True),
]
M_TEMPO       = [("analysis_time_hours", "Tempo de análise (horas)", True)]
M_DESCRICAO   = [("body_length",         "Caracteres na descrição",  True)]
M_INTERACOES  = [
    ("participants", "Participantes", False),
    ("comments",     "Comentários",   True),
]

RQS_STATUS = [
    ("RQ01", "Tamanho",          M_TAMANHO),
    ("RQ02", "Tempo de Análise", M_TEMPO),
    ("RQ03", "Descrição",        M_DESCRICAO),
    ("RQ04", "Interações",       M_INTERACOES),
]
RQS_REVIEWS = [
    ("RQ05", "Tamanho",          M_TAMANHO),
    ("RQ06", "Tempo de Análise", M_TEMPO),
    ("RQ07", "Descrição",        M_DESCRICAO),
    ("RQ08", "Interações",       M_INTERACOES),
]


def carrega_dataset(path):
    df = pd.read_csv(path)
    df = df.dropna(subset=["state", "reviews_count"])
    df["status_label"] = np.where(df["state"] == "MERGED", "MERGED", "CLOSED")
    return df


def carrega_correlacoes(path):
    if not path.exists():
        return None
    return pd.read_csv(path)


def rho_label(corr_df, rq, metrica):
    if corr_df is None:
        return ""
    sel = corr_df[(corr_df["rq"] == rq) & (corr_df["metrica"] == metrica)]
    if sel.empty:
        return ""
    rho = sel.iloc[0]["spearman_rho"]
    p = sel.iloc[0]["p_value"]
    return f"\nρ={rho:.3f}  p={p:.2g}"


def faixas_reviews(s):
    bins = [0, 1, 2, 3, 5, 10, np.inf]
    labels = ["1", "2", "3", "4-5", "6-10", "11+"]
    return pd.cut(s, bins=bins, labels=labels, right=True, include_lowest=True)


def plot_overview_status(df, out_dir):
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    counts = df["status_label"].value_counts().reindex(["MERGED", "CLOSED"])
    bars = ax.bar(counts.index, counts.values,
                  color=[PALETTE_STATUS["MERGED"], PALETTE_STATUS["CLOSED"]])
    total = counts.sum()
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width() / 2, v,
                f"{v:,}\n({v/total:.1%})",
                ha="center", va="bottom", fontsize=11)
    ax.set_ylabel("Quantidade de PRs")
    ax.set_title("Distribuição do status final dos PRs")
    ax.set_ylim(0, counts.max() * 1.18)
    fig.tight_layout()
    out_path = out_dir / "overview_status.png"
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
    print(f"  -> {out_path.name}")


def plot_status(df, rq, dimensao, metricas, corr_df, out_dir):
    n = len(metricas)
    width = max(7.5, 5.8 * n)
    fig, axes = plt.subplots(1, n, figsize=(width, 5.5), squeeze=False)
    for ax, (col, label, logscale) in zip(axes[0], metricas):
        sub = df[[col, "status_label"]].copy()
        if logscale:
            sub = sub[sub[col] > 0]
        sns.boxplot(
            data=sub, x="status_label", y=col, ax=ax,
            order=["MERGED", "CLOSED"], hue="status_label", legend=False,
            palette=PALETTE_STATUS, showfliers=False, width=0.55,
        )
        if logscale:
            ax.set_yscale("log")
        ax.set_xlabel("Status do PR")
        ax.set_ylabel(label)
        ax.set_title(f"{label}{rho_label(corr_df, rq, col)}", fontsize=13)
    fig.suptitle(f"{rq} — {dimensao} vs Status do PR",
                 fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    out = out_dir / f"{rq.lower()}_{dimensao.lower().replace(' ', '_')}_status.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print(f"  -> {out.name}")


def plot_reviews(df, rq, dimensao, metricas, corr_df, out_dir):
    df = df.copy()
    df["faixa"] = faixas_reviews(df["reviews_count"])
    df = df.dropna(subset=["faixa"])

    n = len(metricas)
    width = max(7.5, 5.8 * n)
    fig, axes = plt.subplots(1, n, figsize=(width, 5.5), squeeze=False)
    for ax, (col, label, logscale) in zip(axes[0], metricas):
        agg = (df.groupby("faixa", observed=True)[col]
                 .quantile([0.25, 0.5, 0.75]).unstack())
        agg.columns = ["q25", "q50", "q75"]
        x = np.arange(len(agg))
        ax.fill_between(x, agg["q25"], agg["q75"],
                        alpha=0.3, color="#4878a6", label="IQR (Q1–Q3)")
        ax.plot(x, agg["q50"], "o-", color="#1f3a5f",
                lw=2.5, markersize=8, label="Mediana")
        for xi, m in zip(x, agg["q50"]):
            ax.annotate(f"{m:.0f}", (xi, m),
                        textcoords="offset points", xytext=(0, 9),
                        ha="center", fontsize=9, color="#1f3a5f")
        ax.set_xticks(x)
        ax.set_xticklabels(agg.index)
        if logscale:
            ax.set_yscale("log")
        ax.set_xlabel("Número de revisões")
        ax.set_ylabel(label)
        ax.set_title(f"{label}{rho_label(corr_df, rq, col)}", fontsize=13)
        ax.legend(loc="upper left", fontsize=9)
        ax.grid(True, which="both", alpha=0.3)
    fig.suptitle(f"{rq} — {dimensao} vs Nº de Revisões",
                 fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    out = out_dir / f"{rq.lower()}_{dimensao.lower().replace(' ', '_')}_reviews.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print(f"  -> {out.name}")


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

    print(f"Dataset: {len(df):,} PRs.")
    plot_overview_status(df, out_dir)
    print("Gerando RQ 01-04 (boxplots por status)...")
    for rq, dim, metricas in RQS_STATUS:
        plot_status(df, rq, dim, metricas, corr_df, out_dir)
    print("Gerando RQ 05-08 (mediana + IQR por nº revisões)...")
    for rq, dim, metricas in RQS_REVIEWS:
        plot_reviews(df, rq, dim, metricas, corr_df, out_dir)
    print(f"\nFiguras salvas em {out_dir}")


if __name__ == "__main__":
    main()

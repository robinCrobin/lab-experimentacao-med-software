"""Lab03S03 - Gráficos para as Questões de Pesquisa (RQ 01 a RQ 08).

Para cada RQ usamos a visualização mais adequada à pergunta:

  RQ 01 (Tamanho × Status)        -> violin plot   (compara distribuições completas)
  RQ 02 (Tempo × Status)          -> ECDF          (compara distribuições acumuladas)
  RQ 03 (Descrição × Status)      -> histograma sobreposto + KDE
  RQ 04 (Interações × Status)     -> taxa de merge por faixa (barplot)
  RQ 05 (Tamanho × Nº Revisões)   -> lineplot mediana + banda IQR
  RQ 06 (Tempo × Nº Revisões)     -> hexbin + linha de mediana
  RQ 07 (Descrição × Nº Revisões) -> barplot horizontal das medianas por faixa
  RQ 08 (Interações × Nº Revisões)-> heatmap (participantes × revisões)

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


# ----------------------------- Overview --------------------------------------

def plot_overview_status(df, out_dir):
    fig, ax = plt.subplots(figsize=(6, 4))
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


# ----------------------------- RQ 01: violin ---------------------------------

def plot_rq01_violin(df, corr_df, out_dir):
    metricas = [
        ("files_changed", "Arquivos alterados"),
        ("additions",     "Linhas adicionadas"),
        ("deletions",     "Linhas removidas"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
    for ax, (col, label) in zip(axes, metricas):
        sub = df[[col, "status_label"]].copy()
        sub = sub[sub[col] > 0]
        sub["log"] = np.log10(sub[col])
        sns.violinplot(
            data=sub, x="status_label", y="log", ax=ax,
            order=["MERGED", "CLOSED"], hue="status_label",
            legend=False, palette=PALETTE_STATUS,
            inner="quartile", cut=0,
        )
        ax.set_xlabel("Status do PR")
        ax.set_ylabel(f"log10({label})")
        ax.set_title(f"{label}{rho_label(corr_df, 'RQ01', col)}", fontsize=13)
    fig.suptitle("RQ01 — Tamanho vs Status do PR", fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    out = out_dir / "rq01_tamanho_status.png"
    fig.savefig(out, dpi=130); plt.close(fig); print(f"  -> {out.name}")


# ----------------------------- RQ 02: ECDF -----------------------------------

def plot_rq02_ecdf(df, corr_df, out_dir):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sub = df[df["analysis_time_hours"] > 0].copy()
    for status, color in PALETTE_STATUS.items():
        x = np.sort(sub.loc[sub["status_label"] == status, "analysis_time_hours"].values)
        y = np.arange(1, len(x) + 1) / len(x)
        ax.plot(x, y, label=f"{status} (n={len(x):,})", color=color, lw=2.2)
    ax.set_xscale("log")
    ax.set_xlabel("Tempo de análise (horas, escala log)")
    ax.set_ylabel("Proporção acumulada de PRs")
    ax.set_title(
        f"RQ02 — Tempo de Análise vs Status do PR{rho_label(corr_df, 'RQ02', 'analysis_time_hours')}",
        fontsize=13, fontweight="bold",
    )
    ax.legend(loc="lower right")
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    out = out_dir / "rq02_tempo_de_análise_status.png"
    fig.savefig(out, dpi=130); plt.close(fig); print(f"  -> {out.name}")


# ----------------------------- RQ 03: histograma -----------------------------

def plot_rq03_hist(df, corr_df, out_dir):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sub = df[df["body_length"] > 0].copy()
    sub["log_body"] = np.log10(sub["body_length"])
    for status, color in PALETTE_STATUS.items():
        data = sub.loc[sub["status_label"] == status, "log_body"]
        ax.hist(data, bins=50, density=True, alpha=0.45,
                label=f"{status} (mediana={int(10**data.median())})",
                color=color)
    ax.set_xlabel("log10(caracteres na descrição)")
    ax.set_ylabel("Densidade")
    ax.set_title(
        f"RQ03 — Descrição vs Status do PR{rho_label(corr_df, 'RQ03', 'body_length')}",
        fontsize=13, fontweight="bold",
    )
    ax.legend()
    fig.tight_layout()
    out = out_dir / "rq03_descrição_status.png"
    fig.savefig(out, dpi=130); plt.close(fig); print(f"  -> {out.name}")


# ----------------------------- RQ 04: taxa de merge --------------------------

def plot_rq04_taxa_merge(df, corr_df, out_dir):
    """Taxa de merge por faixa de participantes / comentários."""
    df = df.copy()
    df["merged"] = (df["state"] == "MERGED").astype(int)

    bins_part = [0, 1, 2, 3, 5, 10, np.inf]
    lab_part = ["1", "2", "3", "4-5", "6-10", "11+"]
    df["faixa_part"] = pd.cut(df["participants"], bins=bins_part,
                              labels=lab_part, include_lowest=True)
    df["faixa_com"] = pd.cut(df["comments"], bins=[-1, 0, 1, 3, 5, 10, np.inf],
                             labels=["0", "1", "2-3", "4-5", "6-10", "11+"])

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    for ax, faixa_col, xlabel, rq_metric in [
        (axes[0], "faixa_part", "Nº de participantes",  "participants"),
        (axes[1], "faixa_com",  "Nº de comentários",    "comments"),
    ]:
        agg = df.groupby(faixa_col, observed=True).agg(
            taxa=("merged", "mean"),
            n=("merged", "size"),
        ).reset_index()
        bars = ax.bar(agg[faixa_col].astype(str), agg["taxa"] * 100,
                      color="#4c9f70", edgecolor="white")
        for b, taxa, n in zip(bars, agg["taxa"], agg["n"]):
            ax.text(b.get_x() + b.get_width() / 2, taxa * 100 + 1,
                    f"{taxa:.0%}\n(n={n:,})",
                    ha="center", va="bottom", fontsize=9)
        ax.set_ylim(0, 105)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("% de PRs com MERGE")
        ax.set_title(f"{xlabel}{rho_label(corr_df, 'RQ04', rq_metric)}", fontsize=13)
    fig.suptitle("RQ04 — Interações vs Status do PR (taxa de merge)",
                 fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    out = out_dir / "rq04_interações_status.png"
    fig.savefig(out, dpi=130); plt.close(fig); print(f"  -> {out.name}")


# ----------------------------- RQ 05: linha + IQR ----------------------------

def plot_rq05_linha_iqr(df, corr_df, out_dir):
    df = df.copy()
    df["faixa"] = faixas_reviews(df["reviews_count"])
    df = df.dropna(subset=["faixa"])
    metricas = [
        ("files_changed", "Arquivos alterados"),
        ("additions",     "Linhas adicionadas"),
        ("deletions",     "Linhas removidas"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
    for ax, (col, label) in zip(axes, metricas):
        agg = df.groupby("faixa", observed=True)[col].quantile(
            [0.25, 0.5, 0.75]).unstack()
        agg.columns = ["q25", "q50", "q75"]
        x = np.arange(len(agg))
        ax.fill_between(x, agg["q25"], agg["q75"],
                        alpha=0.3, color="#4878a6", label="IQR (Q1–Q3)")
        ax.plot(x, agg["q50"], "o-", color="#1f3a5f", lw=2.5,
                markersize=8, label="Mediana")
        ax.set_xticks(x)
        ax.set_xticklabels(agg.index)
        ax.set_yscale("log")
        ax.set_xlabel("Número de revisões")
        ax.set_ylabel(label)
        ax.set_title(f"{label}{rho_label(corr_df, 'RQ05', col)}", fontsize=13)
        ax.legend(loc="upper left", fontsize=9)
        ax.grid(True, which="both", alpha=0.3)
    fig.suptitle("RQ05 — Tamanho vs Nº de Revisões",
                 fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    out = out_dir / "rq05_tamanho_reviews.png"
    fig.savefig(out, dpi=130); plt.close(fig); print(f"  -> {out.name}")


# ----------------------------- RQ 06: hexbin ---------------------------------

def plot_rq06_hexbin(df, corr_df, out_dir):
    sub = df[(df["analysis_time_hours"] > 0) & (df["reviews_count"] > 0)].copy()
    sub["log_time"] = np.log10(sub["analysis_time_hours"])
    sub["log_rev"] = np.log10(sub["reviews_count"])

    fig, ax = plt.subplots(figsize=(9, 6))
    hb = ax.hexbin(sub["log_rev"], sub["log_time"],
                   gridsize=40, cmap="viridis", mincnt=1, bins="log")
    cbar = fig.colorbar(hb, ax=ax)
    cbar.set_label("Nº de PRs (escala log)")

    # linha de mediana por faixa
    sub["faixa"] = faixas_reviews(sub["reviews_count"])
    med = sub.groupby("faixa", observed=True).agg(
        x=("log_rev", "median"),
        y=("log_time", "median"),
    ).reset_index()
    ax.plot(med["x"], med["y"], "o-", color="#ff6b35",
            lw=2.5, markersize=9, label="Mediana por faixa")

    ax.set_xlabel("log10(número de revisões)")
    ax.set_ylabel("log10(tempo de análise em horas)")
    ax.set_title(
        f"RQ06 — Tempo de Análise vs Nº de Revisões"
        f"{rho_label(corr_df, 'RQ06', 'analysis_time_hours')}",
        fontsize=13, fontweight="bold",
    )
    ax.legend(loc="upper left")
    fig.tight_layout()
    out = out_dir / "rq06_tempo_de_análise_reviews.png"
    fig.savefig(out, dpi=130); plt.close(fig); print(f"  -> {out.name}")


# ----------------------------- RQ 07: barplot horizontal ---------------------

def plot_rq07_barh(df, corr_df, out_dir):
    df = df.copy()
    df["faixa"] = faixas_reviews(df["reviews_count"])
    df = df.dropna(subset=["faixa"])
    agg = df.groupby("faixa", observed=True)["body_length"].agg(
        mediana="median", media="mean", n="size").reset_index()

    fig, ax = plt.subplots(figsize=(9, 5.5))
    y = np.arange(len(agg))
    h = 0.38
    ax.barh(y - h/2, agg["mediana"], h, label="Mediana",
            color="#4878a6", edgecolor="white")
    ax.barh(y + h/2, agg["media"],   h, label="Média",
            color="#a0c4e0", edgecolor="white")
    for yi, med, mean, n in zip(y, agg["mediana"], agg["media"], agg["n"]):
        ax.text(med, yi - h/2, f" {int(med)}", va="center", fontsize=9)
        ax.text(mean, yi + h/2, f" {int(mean)} (n={n:,})", va="center", fontsize=9)
    ax.set_yticks(y)
    ax.set_yticklabels(agg["faixa"])
    ax.invert_yaxis()
    ax.set_xlabel("Caracteres na descrição")
    ax.set_ylabel("Número de revisões")
    ax.set_title(
        f"RQ07 — Descrição vs Nº de Revisões"
        f"{rho_label(corr_df, 'RQ07', 'body_length')}",
        fontsize=13, fontweight="bold",
    )
    ax.legend(loc="lower right")
    fig.tight_layout()
    out = out_dir / "rq07_descrição_reviews.png"
    fig.savefig(out, dpi=130); plt.close(fig); print(f"  -> {out.name}")


# ----------------------------- RQ 08: heatmap --------------------------------

def plot_rq08_heatmap(df, corr_df, out_dir):
    df = df.copy()
    df["faixa_rev"] = faixas_reviews(df["reviews_count"])
    df["faixa_com"] = pd.cut(df["comments"], bins=[-1, 0, 1, 3, 5, 10, np.inf],
                             labels=["0", "1", "2-3", "4-5", "6-10", "11+"])
    df["faixa_part"] = pd.cut(df["participants"],
                              bins=[0, 1, 2, 3, 5, 10, np.inf],
                              labels=["1", "2", "3", "4-5", "6-10", "11+"],
                              include_lowest=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    for ax, fcol, xlabel, rq_metric in [
        (axes[0], "faixa_part", "Nº de participantes", "participants"),
        (axes[1], "faixa_com",  "Nº de comentários",   "comments"),
    ]:
        ct = pd.crosstab(df[fcol], df["faixa_rev"])
        # normaliza por linha (quanto a faixa de interação se distribui em revisões)
        ct_pct = (ct.div(ct.sum(axis=1), axis=0) * 100).round(1)
        sns.heatmap(ct_pct, annot=True, fmt=".0f", cmap="YlOrRd",
                    cbar_kws={"label": "% de PRs na linha"}, ax=ax,
                    linewidths=0.4, linecolor="white")
        ax.set_xlabel("Número de revisões")
        ax.set_ylabel(xlabel)
        ax.set_title(f"{xlabel}{rho_label(corr_df, 'RQ08', rq_metric)}",
                     fontsize=13)
    fig.suptitle("RQ08 — Interações vs Nº de Revisões",
                 fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    out = out_dir / "rq08_interações_reviews.png"
    fig.savefig(out, dpi=130); plt.close(fig); print(f"  -> {out.name}")


# ----------------------------- main ------------------------------------------

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
    plot_rq01_violin(df, corr_df, out_dir)
    plot_rq02_ecdf(df, corr_df, out_dir)
    plot_rq03_hist(df, corr_df, out_dir)
    plot_rq04_taxa_merge(df, corr_df, out_dir)
    plot_rq05_linha_iqr(df, corr_df, out_dir)
    plot_rq06_hexbin(df, corr_df, out_dir)
    plot_rq07_barh(df, corr_df, out_dir)
    plot_rq08_heatmap(df, corr_df, out_dir)
    print(f"\nFiguras salvas em {out_dir}")


if __name__ == "__main__":
    main()

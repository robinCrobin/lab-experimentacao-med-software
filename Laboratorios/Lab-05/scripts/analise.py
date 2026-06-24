"""Análise de resultados (Passos 4 e 5): valida, resume e testa hipóteses.

Lê ``data/medicoes.csv``, valida as medições, calcula estatísticas descritivas
e aplica o teste de hipótese pareado (Wilcoxon) para RQ1 (tempo) e RQ2
(tamanho). Gera tabelas-resumo em ``data/`` e figuras em ``figures/``.

Uso:
    python analise.py
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
MEDICOES = DATA_DIR / "medicoes.csv"

CORES = {"REST": "#d1495b", "GraphQL": "#30638e"}
sns.set_theme(style="whitegrid")


def cliffs_delta(x, y):
    """Cliff's delta (effect size não-paramétrico) entre amostras x e y."""
    x, y = np.asarray(x), np.asarray(y)
    maior = sum((xi > y).sum() for xi in x)
    menor = sum((xi < y).sum() for xi in x)
    delta = (maior - menor) / (len(x) * len(y))
    a = abs(delta)
    mag = "desprezível" if a < 0.147 else "pequeno" if a < 0.33 else "médio" if a < 0.474 else "grande"
    return delta, mag


def carregar_e_validar():
    if not MEDICOES.exists():
        print(f"Erro: {MEDICOES} não encontrado. Rode benchmark.py primeiro.", file=sys.stderr)
        sys.exit(1)
    df = pd.read_csv(MEDICOES)
    n0 = len(df)
    # Validação: remove medições não-positivas (erros).
    df = df[(df["tempo_ms"] > 0) & (df["tamanho_bytes"] > 0)].copy()
    print(f"Medições carregadas: {n0} | válidas: {len(df)}")
    print(f"Repositórios: {df['repositorio'].nunique()} | APIs: {sorted(df['api'].unique())}")
    return df


def medianas_por_par(df):
    """Reduz as repetições à mediana por (repositório, API)."""
    g = (
        df.groupby(["repositorio", "api"])
        .agg(tempo_ms=("tempo_ms", "median"), tamanho_bytes=("tamanho_bytes", "median"))
        .reset_index()
    )
    return g


def descritivas(df):
    desc = (
        df.groupby("api")
        .agg(
            n=("tempo_ms", "size"),
            tempo_media=("tempo_ms", "mean"),
            tempo_mediana=("tempo_ms", "median"),
            tempo_std=("tempo_ms", "std"),
            tempo_min=("tempo_ms", "min"),
            tempo_max=("tempo_ms", "max"),
            tam_media=("tamanho_bytes", "mean"),
            tam_mediana=("tamanho_bytes", "median"),
            tam_std=("tamanho_bytes", "std"),
            tam_min=("tamanho_bytes", "min"),
            tam_max=("tamanho_bytes", "max"),
        )
        .round(2)
        .reset_index()
    )
    return desc


def teste_pareado(pares, coluna, rotulo):
    """Wilcoxon pareado GraphQL vs REST sobre a coluna indicada."""
    piv = pares.pivot(index="repositorio", columns="api", values=coluna).dropna()
    rest = piv["REST"].values
    gql = piv["GraphQL"].values

    stat, p = stats.wilcoxon(gql, rest)
    delta, mag = cliffs_delta(gql, rest)
    diff_mediana = np.median(gql) - np.median(rest)
    reducao_pct = (1 - np.median(gql) / np.median(rest)) * 100

    return {
        "metrica": rotulo,
        "n_pares": len(piv),
        "mediana_REST": round(float(np.median(rest)), 3),
        "mediana_GraphQL": round(float(np.median(gql)), 3),
        "diff_mediana_GraphQL_menos_REST": round(float(diff_mediana), 3),
        "reducao_GraphQL_pct": round(float(reducao_pct), 2),
        "wilcoxon_stat": round(float(stat), 3),
        "p_valor": float(f"{p:.3e}"),
        "significativo_5pct": bool(p < 0.05),
        "cliffs_delta": round(float(delta), 3),
        "magnitude_efeito": mag,
    }


# ----------------------------- Figuras ------------------------------------

def fig_boxplot(df, coluna, titulo, ylabel, nome, log=False):
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.boxplot(data=df, x="api", y=coluna, hue="api", palette=CORES, ax=ax, legend=False,
                order=["REST", "GraphQL"], showfliers=True)
    if log:
        ax.set_yscale("log")
    ax.set_title(titulo, fontsize=13, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    fig.savefig(FIG_DIR / nome, dpi=140)
    plt.close(fig)


def fig_barras_medias(desc, nome):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    ordem = ["REST", "GraphQL"]
    d = desc.set_index("api").loc[ordem]
    cores = [CORES[a] for a in ordem]

    axes[0].bar(ordem, d["tempo_mediana"], color=cores)
    axes[0].set_title("RQ1 — Tempo de resposta (mediana)", fontweight="bold")
    axes[0].set_ylabel("Tempo (ms)")
    for i, v in enumerate(d["tempo_mediana"]):
        axes[0].text(i, v, f"{v:.0f} ms", ha="center", va="bottom")

    axes[1].bar(ordem, d["tam_mediana"] / 1024, color=cores)
    axes[1].set_title("RQ2 — Tamanho da resposta (mediana)", fontweight="bold")
    axes[1].set_ylabel("Tamanho (KB)")
    for i, v in enumerate(d["tam_mediana"] / 1024):
        axes[1].text(i, v, f"{v:.1f} KB", ha="center", va="bottom")

    fig.tight_layout()
    fig.savefig(FIG_DIR / nome, dpi=140)
    plt.close(fig)


def fig_pareado_scatter(pares, coluna, titulo, label, nome):
    piv = pares.pivot(index="repositorio", columns="api", values=coluna).dropna()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(piv["REST"], piv["GraphQL"], alpha=0.6, color="#5b8c5a", edgecolor="white")
    lim = max(piv["REST"].max(), piv["GraphQL"].max()) * 1.05
    ax.plot([0, lim], [0, lim], "--", color="gray", label="REST = GraphQL")
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_xlabel(f"REST — {label}")
    ax.set_ylabel(f"GraphQL — {label}")
    ax.set_title(titulo, fontweight="bold")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / nome, dpi=140)
    plt.close(fig)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    df = carregar_e_validar()
    pares = medianas_por_par(df)

    # Estatísticas descritivas (sobre as medianas por par).
    desc = descritivas(pares)
    desc.to_csv(DATA_DIR / "resumo_descritivo.csv", index=False)
    print("\n=== Estatísticas descritivas (mediana por repositório) ===")
    print(desc.to_string(index=False))

    # Testes de hipótese.
    t1 = teste_pareado(pares, "tempo_ms", "RQ1 - tempo_ms")
    t2 = teste_pareado(pares, "tamanho_bytes", "RQ2 - tamanho_bytes")
    testes = pd.DataFrame([t1, t2])
    testes.to_csv(DATA_DIR / "testes_estatisticos.csv", index=False)
    print("\n=== Testes de hipótese (Wilcoxon pareado, GraphQL vs REST) ===")
    print(testes.to_string(index=False))

    # Tabela de pares (para o dashboard).
    pares.to_csv(DATA_DIR / "pares.csv", index=False)

    # Figuras.
    fig_boxplot(pares, "tempo_ms", "RQ1 — Distribuição do tempo de resposta", "Tempo (ms)", "rq1_tempo_boxplot.png")
    fig_boxplot(pares, "tamanho_bytes", "RQ2 — Distribuição do tamanho da resposta", "Tamanho (bytes)", "rq2_tamanho_boxplot.png", log=True)
    fig_barras_medias(desc, "comparativo_medianas.png")
    fig_pareado_scatter(pares, "tempo_ms", "RQ1 — Comparação pareada (tempo)", "tempo (ms)", "rq1_tempo_pareado.png")
    fig_pareado_scatter(pares, "tamanho_bytes", "RQ2 — Comparação pareada (tamanho)", "tamanho (bytes)", "rq2_tamanho_pareado.png")
    print(f"\nFiguras salvas em {FIG_DIR}")
    print("Tabelas salvas em data/: resumo_descritivo.csv, testes_estatisticos.csv, pares.csv")


if __name__ == "__main__":
    main()

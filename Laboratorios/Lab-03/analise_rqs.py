"""Lab03S03 - Análise das Questões de Pesquisa (RQ 01 a RQ 08).

Lê `data/dataset_prs.csv` e calcula:
  * Medianas globais e por status (MERGED/CLOSED) para cada métrica.
  * Correlação de Spearman entre cada métrica e:
      - status do PR (MERGED=1, CLOSED=0)  -> RQ 01-04
      - número de revisões (reviews_count) -> RQ 05-08
  * Teste de Mann-Whitney U comparando MERGED vs CLOSED (suporte para RQ 01-04).

Saídas:
  data/rqs_medianas.csv       -> medianas por status + global
  data/rqs_correlacoes.csv    -> Spearman para cada RQ (rho, p-valor, n)
  data/rqs_mannwhitney.csv    -> teste de diferença de distribuição por status

Justificativa do Spearman: as métricas de PR (tamanho, tempo, descrição,
interações) apresentam distribuições fortemente assimétricas e com outliers,
violando os pressupostos de normalidade exigidos por Pearson. Spearman opera
sobre postos (ranks) e mede associação monotônica, sendo robusto a esses
desvios.
"""

import argparse
from pathlib import Path

import pandas as pd
from scipy import stats

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INPUT_CSV = DATA_DIR / "dataset_prs.csv"

METRICAS = {
    "files_changed":       ("Tamanho",         "Número de arquivos alterados"),
    "additions":           ("Tamanho",         "Linhas adicionadas"),
    "deletions":           ("Tamanho",         "Linhas removidas"),
    "analysis_time_hours": ("Tempo de Análise", "Horas entre criação e fechamento"),
    "body_length":         ("Descrição",       "Caracteres na descrição (markdown)"),
    "participants":        ("Interações",      "Número de participantes"),
    "comments":            ("Interações",      "Número de comentários"),
}

# Mapeia métrica -> RQ (status) e RQ (nº revisões)
RQ_STATUS = {
    "Tamanho":          "RQ01",
    "Tempo de Análise": "RQ02",
    "Descrição":        "RQ03",
    "Interações":       "RQ04",
}
RQ_REVIEWS = {
    "Tamanho":          "RQ05",
    "Tempo de Análise": "RQ06",
    "Descrição":        "RQ07",
    "Interações":       "RQ08",
}


def carrega_dataset(path):
    df = pd.read_csv(path)
    # garantia de tipos numéricos
    for col in METRICAS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["reviews_count"] = pd.to_numeric(df["reviews_count"], errors="coerce")
    df = df.dropna(subset=list(METRICAS.keys()) + ["reviews_count", "state"])
    df["merged"] = (df["state"] == "MERGED").astype(int)
    return df


def tabela_medianas(df):
    rows = []
    for col, (dim, desc) in METRICAS.items():
        global_med = df[col].median()
        merged_med = df.loc[df["merged"] == 1, col].median()
        closed_med = df.loc[df["merged"] == 0, col].median()
        rows.append({
            "dimensao": dim,
            "metrica": col,
            "descricao": desc,
            "mediana_global": global_med,
            "mediana_merged": merged_med,
            "mediana_closed": closed_med,
            "media_global": df[col].mean(),
        })
    # mediana de reviews_count também é interessante para o relatório
    rows.append({
        "dimensao": "Revisões",
        "metrica": "reviews_count",
        "descricao": "Número de revisões realizadas",
        "mediana_global": df["reviews_count"].median(),
        "mediana_merged": df.loc[df["merged"] == 1, "reviews_count"].median(),
        "mediana_closed": df.loc[df["merged"] == 0, "reviews_count"].median(),
        "media_global": df["reviews_count"].mean(),
    })
    return pd.DataFrame(rows)


def tabela_correlacoes(df):
    rows = []
    for col, (dim, desc) in METRICAS.items():
        # vs status (RQ 01-04)
        rho_s, p_s = stats.spearmanr(df[col], df["merged"])
        rows.append({
            "rq": RQ_STATUS[dim],
            "alvo": "status (MERGED=1)",
            "dimensao": dim,
            "metrica": col,
            "spearman_rho": rho_s,
            "p_value": p_s,
            "n": len(df),
        })
        # vs nº revisões (RQ 05-08)
        rho_r, p_r = stats.spearmanr(df[col], df["reviews_count"])
        rows.append({
            "rq": RQ_REVIEWS[dim],
            "alvo": "reviews_count",
            "dimensao": dim,
            "metrica": col,
            "spearman_rho": rho_r,
            "p_value": p_r,
            "n": len(df),
        })
    return pd.DataFrame(rows).sort_values(["rq", "metrica"]).reset_index(drop=True)


def tabela_mannwhitney(df):
    """Mann-Whitney U: distribuição da métrica difere entre MERGED e CLOSED?"""
    rows = []
    merged = df[df["merged"] == 1]
    closed = df[df["merged"] == 0]
    for col, (dim, _) in METRICAS.items():
        u, p = stats.mannwhitneyu(merged[col], closed[col], alternative="two-sided")
        rows.append({
            "rq": RQ_STATUS[dim],
            "dimensao": dim,
            "metrica": col,
            "U": u,
            "p_value": p,
            "n_merged": len(merged),
            "n_closed": len(closed),
        })
    return pd.DataFrame(rows)


def imprime_resumo(med_df, corr_df, mw_df):
    print("\n=== Medianas (global, MERGED, CLOSED) ===")
    print(med_df.to_string(index=False))

    print("\n=== Correlações de Spearman ===")
    cols = ["rq", "dimensao", "metrica", "alvo", "spearman_rho", "p_value"]
    print(corr_df[cols].to_string(index=False))

    print("\n=== Mann-Whitney U (MERGED vs CLOSED) ===")
    print(mw_df.to_string(index=False))


def main():
    parser = argparse.ArgumentParser(description="Análise das RQs do Lab-03.")
    parser.add_argument("--input", default=str(INPUT_CSV))
    parser.add_argument("--out-dir", default=str(DATA_DIR))
    args = parser.parse_args()

    df = carrega_dataset(Path(args.input))
    print(f"Dataset carregado: {len(df)} PRs em {df['repo'].nunique()} repositórios.")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    med_df = tabela_medianas(df)
    corr_df = tabela_correlacoes(df)
    mw_df = tabela_mannwhitney(df)

    med_df.to_csv(out_dir / "rqs_medianas.csv", index=False)
    corr_df.to_csv(out_dir / "rqs_correlacoes.csv", index=False)
    mw_df.to_csv(out_dir / "rqs_mannwhitney.csv", index=False)

    imprime_resumo(med_df, corr_df, mw_df)
    print(f"\nArquivos salvos em {out_dir}")


if __name__ == "__main__":
    main()

"""
Lab-02 - agregacao de metricas CK em um unico CSV.

Le os arquivos `class.csv` gerados pela ferramenta CK em
`data/ck_results/<owner>__<repo>/class.csv`, calcula metricas
agregadas por repositorio e cruza com `data/top_java_repos.csv`
para compor o arquivo consolidado usado pelas analises (RQs).

Saida:
- data/metrics_consolidated.csv

Colunas geradas:
- name_with_owner, stargazers, created_at, releases_count, n_classes,
  cbo_mean, dit_mean, lcom_mean, loc, comment_lines
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

LAB_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = LAB_DIR / "data"
CK_RESULTS_DIR = DATA_DIR / "ck_results"
REPOS_CSV = DATA_DIR / "top_java_repos.csv"
EXCLUDED_CSV = DATA_DIR / "ck_excluded.csv"
OUTPUT_CSV = DATA_DIR / "metrics_consolidated.csv"


def _safe_mean(series: pd.Series) -> float:
    series = pd.to_numeric(series, errors="coerce").dropna()
    return float(series.mean()) if len(series) > 0 else float("nan")


def _safe_sum(series: pd.Series) -> float:
    series = pd.to_numeric(series, errors="coerce").dropna()
    return float(series.sum()) if len(series) > 0 else float("nan")


def aggregate_repo(class_csv: Path) -> dict[str, float] | None:
    try:
        df = pd.read_csv(class_csv)
    except Exception as exc:
        print(f"[warn] falha ao ler {class_csv}: {exc}")
        return None

    if df.empty:
        return None

    return {
        "n_classes": int(len(df)),
        "cbo_mean": _safe_mean(df.get("cbo", pd.Series(dtype=float))),
        "dit_mean": _safe_mean(df.get("dit", pd.Series(dtype=float))),
        "lcom_mean": _safe_mean(df.get("lcom", pd.Series(dtype=float))),
        "loc": _safe_sum(df.get("loc", pd.Series(dtype=float))),
        # CK class.csv nao expressa "comment_lines" diretamente; quando
        # ausente, deixamos NaN para que as RQs que dependem disso pulem.
        "comment_lines": _safe_sum(df.get("comment_lines", pd.Series(dtype=float))),
    }


def main() -> None:
    if not CK_RESULTS_DIR.exists():
        raise SystemExit(f"Diretorio nao encontrado: {CK_RESULTS_DIR}")

    # Conjunto de repos excluidos (CK falhou) para nao serem considerados
    excluded: set[str] = set()
    if EXCLUDED_CSV.exists():
        excluded_df = pd.read_csv(EXCLUDED_CSV)
        excluded = set(excluded_df["name_with_owner"].astype(str).tolist())
        print(f"Ignorando {len(excluded)} repositorios listados em {EXCLUDED_CSV.name}")

    # Mapa nameWithOwner -> metadados do GraphQL (stars, createdAt, releases)
    repo_meta: dict[str, dict] = {}
    if REPOS_CSV.exists():
        repos_df = pd.read_csv(REPOS_CSV)
        for _, row in repos_df.iterrows():
            repo_meta[str(row["nameWithOwner"])] = {
                "stargazers": row.get("stargazerCount"),
                "created_at": row.get("createdAt"),
                "releases_count": row.get("releasesCount"),
            }
    else:
        print(f"[warn] {REPOS_CSV} ausente: metadados ficarao NaN")

    rows: list[dict] = []
    repo_dirs = sorted(p for p in CK_RESULTS_DIR.iterdir() if p.is_dir())
    print(f"Agregando metricas de {len(repo_dirs)} repositorios...")

    for repo_dir in repo_dirs:
        class_csv = repo_dir / "class.csv"
        if not class_csv.exists() or class_csv.stat().st_size == 0:
            continue

        # owner__repo -> owner/repo
        name_with_owner = repo_dir.name.replace("__", "/", 1)
        if name_with_owner in excluded:
            continue

        agg = aggregate_repo(class_csv)
        if agg is None:
            continue

        meta = repo_meta.get(name_with_owner, {})
        rows.append(
            {
                "name_with_owner": name_with_owner,
                "stargazers": meta.get("stargazers", float("nan")),
                "created_at": meta.get("created_at"),
                "releases_count": meta.get("releases_count", float("nan")),
                **agg,
            }
        )

    if not rows:
        raise SystemExit("Nenhum repositorio com class.csv valido encontrado.")

    out_df = pd.DataFrame(rows)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUTPUT_CSV, index=False)
    print(f"OK: {len(out_df)} repositorios -> {OUTPUT_CSV}")


if __name__ == "__main__":
    main()

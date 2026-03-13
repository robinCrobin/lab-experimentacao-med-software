from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
CSV_REPOS_PATH = DATA_DIR / "repositorios_processados.csv"
CSV_LANG_DIST_PATH = DATA_DIR / "distribuicao_linguagem.csv"
CSV_METRICAS_LANG_PATH = DATA_DIR / "metricas_por_linguagem.csv"
OUTPUT_DIR = Path(__file__).parent / "figures"


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_repos_df() -> pd.DataFrame:
    df = pd.read_csv(CSV_REPOS_PATH)
    return df


def plot_rq01_repo_age(df: pd.DataFrame) -> None:
    """RQ01 — Idade dos repositórios: histograma da idade em anos com faixas mais detalhadas."""

    ensure_output_dir()

    df_valid = df[df["repo_age_days"].notna()].copy()
    df_valid["repo_age_years"] = df_valid["repo_age_days"] / 365.25

    # Faixas mais específicas: [0,1], (1,3], (3,5], (5,8], (8,12], (12, max]
    max_years = df_valid["repo_age_years"].max()
    upper = max(max_years, 12)
    bins = [0, 1, 3, 5, 8, 12, upper]
    labels = ["[0,1]", "(1,3]", "(3,5]", "(5,8]", "(8,12]", f"(12,{upper:.1f}]"]

    plt.figure(figsize=(8, 5))
    plt.hist(df_valid["repo_age_years"], bins=bins, edgecolor="black")
    tick_positions = [(bins[i] + bins[i + 1]) / 2 for i in range(len(bins) - 1)]
    plt.xticks(tick_positions, labels, rotation=30)
    plt.xlabel("Idade do repositório (anos)")
    plt.ylabel("Número de repositórios")
    plt.title("RQ01 — Distribuição da idade dos repositórios")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "rq01_repo_age_hist.png", dpi=300)
    plt.close()


def _count_in_bins(serie, edges):
    """Conta elementos de `serie` em intervalos definidos por `edges`.

    edges: lista de limites [e0, e1, e2, ...]. Retorna lista de contagens de
    tamanho len(edges) - 1.
    """

    counts = []
    for low, high in zip(edges[:-1], edges[1:]):
        if high == edges[-1]:
            # último intervalo inclui o limite superior
            mask = (serie >= low) & (serie <= high)
        else:
            mask = (serie >= low) & (serie < high)
        counts.append(mask.sum())
    return counts


def plot_rq02_pull_requests(df: pd.DataFrame) -> None:
    """RQ02 — Pull Requests aceitas: boxplot + barras em faixas mais específicas."""

    ensure_output_dir()

    serie = df["pull_requests_total"].fillna(0)

    # Boxplot
    plt.figure(figsize=(6, 4))
    plt.boxplot(serie, vert=True, showfliers=True)
    plt.ylabel("Total de pull requests")
    plt.title("RQ02 — Distribuição de pull requests (boxplot)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "rq02_pull_requests_boxplot.png", dpi=300)
    plt.close()

    # Faixas mais específicas para PRs: [0,50], (50,200], (200,1000], (1000,5000], (5000, +inf]
    edges = [0, 50, 200, 1000, 5000, 10**9]
    labels = ["[0,50]", "(50,200]", "(200,1000]", "(1000,5000]", "(5000,+∞)"]
    counts = _count_in_bins(serie, edges)

    plt.figure(figsize=(9, 5))
    plt.bar(labels, counts, color="steelblue", edgecolor="black")
    plt.xlabel("Total de pull requests")
    plt.ylabel("Número de repositórios")
    plt.title("RQ02 — Distribuição de pull requests")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "rq02_pull_requests_bar.png", dpi=300)
    plt.close()


def plot_rq03_releases(df: pd.DataFrame) -> None:
    """RQ03 — Número de releases: barras em faixas mais específicas."""

    ensure_output_dir()

    serie = df["releases_total"].fillna(0)

    # Faixas: [0,0], (0,5], (5,20], (20,100], (100,+inf]
    edges = [0, 1, 5, 20, 100, 10**6]
    labels = ["[0,0]", "(0,5]", "(5,20]", "(20,100]", "(100,+∞)"]
    counts = _count_in_bins(serie, edges)

    plt.figure(figsize=(9, 5))
    plt.bar(labels, counts, color="steelblue", edgecolor="black")
    plt.xlabel("Total de releases")
    plt.ylabel("Número de repositórios")
    plt.title("RQ03 — Distribuição de releases")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "rq03_releases_bar.png", dpi=300)
    plt.close()


def plot_rq04_days_since_update(df: pd.DataFrame) -> None:
    """RQ04 — Tempo desde última atualização: barras em faixas mais específicas."""

    ensure_output_dir()

    serie = df["days_since_last_update"].fillna(0)

    # Faixas: [0,3], (3,7], (7,30], (30,90], (90,365], (365,+inf]
    edges = [0, 3, 7, 30, 90, 365, 10**5]
    labels = ["[0,3]", "(3,7]", "(7,30]", "(30,90]", "(90,365]", "(365,+∞)"]
    counts = _count_in_bins(serie, edges)

    plt.figure(figsize=(10, 5))
    plt.bar(labels, counts, color="steelblue", edgecolor="black")
    plt.xlabel("Dias desde a última atualização")
    plt.ylabel("Número de repositórios")
    plt.title("RQ04 — Distribuição do tempo desde a última atualização")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "rq04_days_since_update_bar.png", dpi=300)
    plt.close()


def plot_rq05_primary_language() -> None:
    """RQ05 — Linguagem principal: gráfico de barras da contagem de repositórios."""

    ensure_output_dir()

    df_lang = pd.read_csv(CSV_LANG_DIST_PATH)

    plt.figure(figsize=(10, 6))
    plt.bar(df_lang["language"], df_lang["count"], color="steelblue")
    plt.xticks(rotation=90)
    plt.xlabel("Linguagem principal")
    plt.ylabel("Número de repositórios")
    plt.title("RQ05 — Distribuição de linguagens principais")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "rq05_primary_language_bar.png", dpi=300)
    plt.close()


def plot_rq06_closed_issues_ratio(df: pd.DataFrame) -> None:
    """RQ06 — Taxa de issues fechadas: boxplot + histograma em faixas."""

    ensure_output_dir()

    serie = df["closed_issues_ratio"].dropna()

    # Boxplot
    plt.figure(figsize=(6, 4))
    plt.boxplot(serie, vert=True, showfliers=True)
    plt.ylabel("Taxa de issues fechadas")
    plt.title("RQ06 — Taxa de issues fechadas (boxplot)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "rq06_closed_issues_ratio_boxplot.png", dpi=300)
    plt.close()

    # Histograma em faixas
    bins = [0.0, 0.25, 0.5, 0.75, 1.0]
    labels = ["0–0.25", "0.25–0.5", "0.5–0.75", "0.75–1"]

    plt.figure(figsize=(8, 5))
    plt.hist(serie, bins=bins, edgecolor="black")
    plt.xticks([(bins[i] + bins[i + 1]) / 2 for i in range(len(bins) - 1)], labels)
    plt.xlabel("Taxa de issues fechadas")
    plt.ylabel("Número de repositórios")
    plt.title("RQ06 — Distribuição da taxa de issues fechadas (histograma)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "rq06_closed_issues_ratio_hist.png", dpi=300)
    plt.close()


def main() -> None:
    df = load_repos_df()

    plot_rq01_repo_age(df)
    plot_rq02_pull_requests(df)
    plot_rq03_releases(df)
    plot_rq04_days_since_update(df)
    plot_rq05_primary_language()
    plot_rq06_closed_issues_ratio(df)

    print(f"Figuras salvas em {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()

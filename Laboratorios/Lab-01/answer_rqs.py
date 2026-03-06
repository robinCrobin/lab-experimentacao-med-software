import json
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
JSON_PATH = DATA_DIR / "repositorios.json"


def load_repos(path=JSON_PATH):
    if not path.exists():
        raise FileNotFoundError(f"Arquivo JSON não encontrado: {path}")

    with open(path, "r", encoding="utf-8") as f:
        repos = json.load(f)
    return repos


def compute_metrics(repos):
    # Normalizar para DataFrame
    df = pd.json_normalize(repos)

    # selecionar colunas de interesse com nomes seguros
    df = df.rename(columns={
        "primaryLanguage.name": "primary_language",
        "pullRequests.totalCount": "pull_requests_total",
        "releases.totalCount": "releases_total",
        "createdAt": "created_at",
        "pushedAt": "pushed_at",
    })

    # garantir colunas existem
    for col in ["created_at", "pushed_at", "pull_requests_total", "releases_total", "primary_language"]:
        if col not in df.columns:
            df[col] = pd.NA

    # converter datas
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce")
    df["pushed_at"] = pd.to_datetime(df["pushed_at"], utc=True, errors="coerce")

    now = datetime.now(timezone.utc)
    df["repo_age_days"] = (now - df["created_at"]).dt.total_seconds() / (60 * 60 * 24)
    df["days_since_last_update"] = (now - df["pushed_at"]).dt.total_seconds() / (60 * 60 * 24)

    # converter contadores para numeric (alguns podem ser nulos)
    df["pull_requests_total"] = pd.to_numeric(df["pull_requests_total"], errors="coerce").fillna(0)
    df["releases_total"] = pd.to_numeric(df["releases_total"], errors="coerce").fillna(0)

    # Calcular médias (ignorar valores NaN onde apropriado)
    metrics = {
        "RQ01_mean_repo_age_days": df["repo_age_days"].dropna().mean(),
        "RQ02_mean_merged_pull_requests": df["pull_requests_total"].mean(),
        "RQ03_mean_releases_total": df["releases_total"].mean(),
        "RQ04_mean_days_since_last_update": df["days_since_last_update"].dropna().mean(),
    }

    # Linguagem primária: distribuição (counts + percent)
    lang_series = df["primary_language"].fillna("<unknown>")
    lang_counts = lang_series.value_counts(dropna=False)
    lang_pct = (lang_counts / len(df)) * 100

    lang_df = pd.DataFrame({
        "language": lang_counts.index,
        "count": lang_counts.values,
        "percentage": lang_pct.values
    })

    return metrics, lang_df


def save_results(metrics, lang_df, out_summary="rqs_summary.csv", out_langs="language_distribution.csv"):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # salvar summary (métricas numéricas)
    summary_items = [(k, float(v) if pd.notna(v) else None) for k, v in metrics.items()]
    summary_df = pd.DataFrame(summary_items, columns=["metric", "value"])
    summary_path = DATA_DIR / out_summary
    summary_df.to_csv(summary_path, index=False)

    # salvar distribuição de linguagens
    lang_path = DATA_DIR / out_langs
    lang_df.to_csv(lang_path, index=False)

    return summary_path, lang_path


def main():
    repos = load_repos()
    metrics, lang_df = compute_metrics(repos)
    summary_path, lang_path = save_results(metrics, lang_df)

    print("Métricas calculadas:")
    for k, v in metrics.items():
        if v is None or pd.isna(v):
            print(f"  {k}: N/A")
        else:
            # formatar arredondando quando faz sentido
            if "days" in k or "age" in k:
                print(f"  {k}: {v:.2f} dias")
            else:
                print(f"  {k}: {v:.2f}")

    print(f"\nArquivo resumo salvo em: {summary_path}")
    print(f"Distribuição de linguagens salva em: {lang_path}")


if __name__ == "__main__":
    main()

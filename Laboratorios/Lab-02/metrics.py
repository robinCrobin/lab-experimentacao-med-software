"""Geração de gráficos para responder às RQs do Lab-02.

Lê o arquivo `data/metrics_consolidated.csv` (gerado por
`analysis/build_metrics.py`) e produz gráficos de dispersão que
relacionam métricas de processo com métricas de qualidade.

RQs cobertas:

RQ 01. Popularidade (número de estrelas) x qualidade (CBO, DIT, LCOM)
RQ 02. Maturidade (idade do repositório, em anos) x qualidade
RQ 03. Atividade (número de releases) x qualidade
RQ 04. Tamanho (número de classes, LOC, linhas de comentário) x qualidade

Saída: arquivos PNG em `analysis/plots/`.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


LAB_DIR = Path(__file__).resolve().parent
DATA_CSV = LAB_DIR / "data" / "metrics_consolidated.csv"
PLOTS_DIR = LAB_DIR / "analysis" / "plots"


def _load_data() -> pd.DataFrame:
	"""Carrega o CSV consolidado e deriva coluna de idade em anos.

	Espera as colunas (ver `analysis/build_metrics.py`):
	- name_with_owner, stargazers, created_at, releases_count,
	  n_classes, cbo_mean, dit_mean, lcom_mean, loc, comment_lines
	"""

	if not DATA_CSV.exists():
		raise SystemExit(
			f"Arquivo de métricas não encontrado: {DATA_CSV}. "
			"Gere-o primeiro executando `analysis/build_metrics.py`."
		)

	df = pd.read_csv(DATA_CSV, parse_dates=["created_at"], infer_datetime_format=True)

	# Maturidade: idade em anos desde a data de criação até hoje
	today = pd.Timestamp.today(tz=df["created_at"].dt.tz)
	df["age_years"] = (today - df["created_at"]).dt.days / 365.25

	return df


def _spearman_corr(x: pd.Series, y: pd.Series) -> float:
	"""Calcula correlação de Spearman sem depender de SciPy.

	Implementa Spearman como correlação de Pearson entre os ranks.
	"""

	xr = x.rank()
	yr = y.rank()
	return xr.corr(yr, method="pearson")


def _scatter_with_corr(
	df: pd.DataFrame,
	x: str,
	y: str,
	*,
	title: str,
	xlabel: str,
	ylabel: str,
	filename: str,
) -> None:
	"""Gera gráfico de dispersão com linha de tendência e correlações.

	- Remove linhas com NaN nas colunas x ou y
	- Desenha regressão linear simples (quando possível)
	- Calcula correlação de Pearson e Spearman e exibe no título
	"""

	sub = df[[x, y]].dropna()
	if sub.empty:
		print(f"[warn] Sem dados numéricos suficientes para {x} x {y}")
		return

	PLOTS_DIR.mkdir(parents=True, exist_ok=True)

	plt.figure(figsize=(7, 4.5))
	# Pontos um pouco maiores para facilitar a visualização da densidade
	plt.scatter(sub[x], sub[y], alpha=0.5, s=25)

	# Linha de tendência (regressão linear)
	try:
		x_vals = sub[x].to_numpy(dtype=float)
		y_vals = sub[y].to_numpy(dtype=float)
		coeffs = np.polyfit(x_vals, y_vals, deg=1)
		x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
		y_line = coeffs[0] * x_line + coeffs[1]
		plt.plot(x_line, y_line, color="red", linewidth=1)
	except Exception as exc:  # pragma: no cover - proteção extra
		print(f"[warn] Não foi possível ajustar regressão para {x} x {y}: {exc}")

	# Usamos apenas Spearman, conforme solicitado no enunciado
	spearman = _spearman_corr(sub[x], sub[y])

	plt.title(f"{title}\nSpearman={spearman:.3f}")
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.tight_layout()

	out_path = PLOTS_DIR / filename
	plt.savefig(out_path, dpi=150)
	plt.close()

	print(f"[ok] {x} x {y} -> {out_path} (Spearman={spearman:.3f})")


def gerar_rq01(df: pd.DataFrame) -> None:
	"""RQ 01. Popularidade x características de qualidade."""

	x = "stargazers"
	pares = [
		("cbo_mean", "CBO médio"),
		("dit_mean", "DIT médio"),
		("lcom_mean", "LCOM médio"),
	]

	for metric, label in pares:
		_scatter_with_corr(
			df,
			x,
			metric,
			title=f"RQ01: Popularidade x {label}",
			xlabel="Popularidade (número de estrelas)",
			ylabel=label,
			filename=f"rq01_{metric}.png",
		)


def gerar_rq02(df: pd.DataFrame) -> None:
	"""RQ 02. Maturidade (idade em anos) x características de qualidade."""

	x = "age_years"
	pares = [
		("cbo_mean", "CBO médio"),
		("dit_mean", "DIT médio"),
		("lcom_mean", "LCOM médio"),
	]

	for metric, label in pares:
		_scatter_with_corr(
			df,
			x,
			metric,
			title=f"RQ02: Maturidade x {label}",
			xlabel="Maturidade (idade do repositório em anos)",
			ylabel=label,
			filename=f"rq02_{metric}.png",
		)


def gerar_rq03(df: pd.DataFrame) -> None:
	"""RQ 03. Atividade (número de releases) x características de qualidade."""

	x = "releases_count"
	pares = [
		("cbo_mean", "CBO médio"),
		("dit_mean", "DIT médio"),
		("lcom_mean", "LCOM médio"),
	]

	for metric, label in pares:
		_scatter_with_corr(
			df,
			x,
			metric,
			title=f"RQ03: Atividade (releases) x {label}",
			xlabel="Atividade (número de releases)",
			ylabel=label,
			filename=f"rq03_{metric}.png",
		)


def gerar_rq04(df: pd.DataFrame) -> None:
	"""RQ 04. Tamanho x características de qualidade.

	Usa como proxies de tamanho:
	- n_classes: número de classes
	- loc: linhas de código
	- comment_lines: linhas de comentário (quando disponível)
	"""

	tamanhos = [
		("n_classes", "Número de classes"),
		("loc", "Linhas de código (LOC)"),
		("comment_lines", "Linhas de comentário"),
	]
	qualidades = [
		("cbo_mean", "CBO médio"),
		("dit_mean", "DIT médio"),
		("lcom_mean", "LCOM médio"),
	]

	for size_col, size_label in tamanhos:
		# Pode haver colunas inteiras como NaN (ex: comment_lines); nesse caso,
		# os helpers vão simplesmente pular os gráficos vazios.
		for metric, qual_label in qualidades:
			_scatter_with_corr(
				df,
				size_col,
				metric,
				title=f"RQ04: {size_label} x {qual_label}",
				xlabel=size_label,
				ylabel=qual_label,
				filename=f"rq04_{size_col}_{metric}.png",
			)


def main() -> None:
	df = _load_data()
	print(f"{len(df)} repositórios carregados de {DATA_CSV}")

	gerar_rq01(df)
	gerar_rq02(df)
	gerar_rq03(df)
	gerar_rq04(df)


if __name__ == "__main__":
	main()


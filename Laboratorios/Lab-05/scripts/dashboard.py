"""Dashboard de visualização (Passo 6 — Sprint Lab05S03).

Importa os dados resultantes do experimento (tabelas e figuras geradas por
``analise.py``) e monta um dashboard HTML autocontido (figuras embutidas em
base64) com as tabelas e gráficos que respondem RQ1 e RQ2.

Uso:
    python dashboard.py
Saída: dashboard/dashboard_lab05.html
"""

import base64
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
OUT_DIR = ROOT / "dashboard"
OUT_HTML = OUT_DIR / "dashboard_lab05.html"


def img_b64(nome):
    p = FIG_DIR / nome
    if not p.exists():
        return ""
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


def df_to_html(df, fmt=None):
    return df.to_html(index=False, border=0, classes="tbl", float_format=fmt)


def card_metrica(titulo, valor, sub):
    return f"""
    <div class="card">
      <div class="card-title">{titulo}</div>
      <div class="card-value">{valor}</div>
      <div class="card-sub">{sub}</div>
    </div>"""


def resposta_rq(teste):
    """Texto de resposta da RQ a partir da linha de teste."""
    sig = teste["significativo_5pct"]
    red = teste["reducao_GraphQL_pct"]
    if not sig:
        return "Não há diferença estatisticamente significativa (p ≥ 0,05)."
    if red > 0:
        return f"Sim — GraphQL é menor/mais rápido, com redução mediana de {red:.1f}% (p &lt; 0,05)."
    return f"Não — GraphQL é maior/mais lento ({abs(red):.1f}% acima do REST, p &lt; 0,05)."


def main():
    for f in ["resumo_descritivo.csv", "testes_estatisticos.csv"]:
        if not (DATA_DIR / f).exists():
            print(f"Erro: {DATA_DIR / f} não encontrado. Rode analise.py primeiro.", file=sys.stderr)
            sys.exit(1)

    desc = pd.read_csv(DATA_DIR / "resumo_descritivo.csv")
    testes = pd.read_csv(DATA_DIR / "testes_estatisticos.csv")
    t_rq1 = testes[testes["metrica"].str.startswith("RQ1")].iloc[0]
    t_rq2 = testes[testes["metrica"].str.startswith("RQ2")].iloc[0]

    n_repos = int(desc["n"].max())

    cards = (
        card_metrica("Objetos experimentais", f"{n_repos}", "repositórios populares")
        + card_metrica("RQ1 — Tempo (mediana)",
                       f'{t_rq1["mediana_GraphQL"]:.0f} vs {t_rq1["mediana_REST"]:.0f} ms',
                       f'GraphQL vs REST · p={t_rq1["p_valor"]:.2e}')
        + card_metrica("RQ2 — Tamanho (mediana)",
                       f'{t_rq2["mediana_GraphQL"]/1024:.1f} vs {t_rq2["mediana_REST"]/1024:.1f} KB',
                       f'GraphQL vs REST · p={t_rq2["p_valor"]:.2e}')
    )

    desc_fmt = desc.copy()
    html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lab 05 — GraphQL vs REST · Dashboard</title>
<style>
  :root {{ --rest:#d1495b; --gql:#30638e; --bg:#f5f6f8; --card:#fff; --ink:#1d2733; }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif; margin:0; background:var(--bg); color:var(--ink); }}
  header {{ background:linear-gradient(120deg,#30638e,#1d2733); color:#fff; padding:32px 40px; }}
  header h1 {{ margin:0 0 6px; font-size:26px; }}
  header p {{ margin:0; opacity:.85; }}
  main {{ max-width:1100px; margin:0 auto; padding:28px 24px 60px; }}
  .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; margin-bottom:28px; }}
  .card {{ background:var(--card); border-radius:12px; padding:18px 20px; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
  .card-title {{ font-size:13px; color:#667; text-transform:uppercase; letter-spacing:.04em; }}
  .card-value {{ font-size:24px; font-weight:700; margin:6px 0 2px; }}
  .card-sub {{ font-size:12px; color:#889; }}
  section {{ background:var(--card); border-radius:12px; padding:24px; margin-bottom:24px; box-shadow:0 1px 3px rgba(0,0,0,.06); }}
  section h2 {{ margin-top:0; border-left:4px solid var(--gql); padding-left:10px; }}
  .answer {{ background:#eef4f8; border-radius:8px; padding:12px 16px; font-weight:600; margin:14px 0; }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
  img {{ max-width:100%; border-radius:8px; }}
  table.tbl {{ border-collapse:collapse; width:100%; font-size:13px; }}
  table.tbl th, table.tbl td {{ padding:8px 10px; text-align:right; border-bottom:1px solid #eee; }}
  table.tbl th:first-child, table.tbl td:first-child {{ text-align:left; }}
  table.tbl thead th {{ background:#f0f2f5; }}
  footer {{ text-align:center; color:#889; font-size:12px; padding:20px; }}
  @media(max-width:720px) {{ .grid2 {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<header>
  <h1>GraphQL vs REST — Um experimento controlado</h1>
  <p>Lab 05 · Dashboard de resultados · API pública do GitHub · {n_repos} repositórios</p>
</header>
<main>
  <div class="cards">{cards}</div>

  <section>
    <h2>Comparativo geral</h2>
    <img src="{img_b64('comparativo_medianas.png')}" alt="Comparativo de medianas">
  </section>

  <section>
    <h2>RQ1 — Respostas GraphQL são mais rápidas que REST?</h2>
    <div class="answer">{resposta_rq(t_rq1)}</div>
    <div class="grid2">
      <img src="{img_b64('rq1_tempo_boxplot.png')}" alt="Boxplot tempo">
      <img src="{img_b64('rq1_tempo_pareado.png')}" alt="Dispersão pareada tempo">
    </div>
  </section>

  <section>
    <h2>RQ2 — Respostas GraphQL têm tamanho menor que REST?</h2>
    <div class="answer">{resposta_rq(t_rq2)}</div>
    <div class="grid2">
      <img src="{img_b64('rq2_tamanho_boxplot.png')}" alt="Boxplot tamanho">
      <img src="{img_b64('rq2_tamanho_pareado.png')}" alt="Dispersão pareada tamanho">
    </div>
  </section>

  <section>
    <h2>Estatísticas descritivas</h2>
    {df_to_html(desc_fmt)}
  </section>

  <section>
    <h2>Testes de hipótese (Wilcoxon pareado)</h2>
    {df_to_html(testes)}
    <p style="font-size:12px;color:#889;margin-top:10px;">
      Teste não-paramétrico de Wilcoxon para amostras pareadas (GraphQL vs REST por repositório).
      <em>cliffs_delta</em> indica o tamanho do efeito. p &lt; 0,05 rejeita a hipótese nula.
    </p>
  </section>
</main>
<footer>Lab 05 — Laboratório de Experimentação de Software · gerado por dashboard.py</footer>
</body>
</html>"""

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Dashboard gerado em {OUT_HTML}")


if __name__ == "__main__":
    main()

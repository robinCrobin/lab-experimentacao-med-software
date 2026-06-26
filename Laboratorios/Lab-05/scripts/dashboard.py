"""Dashboard de visualização (Passo 6 — Sprint Lab05S03).

Monta um dashboard HTML interativo e autocontido a partir dos dados do
experimento (``data/*.csv`` gerados por ``analise.py``). Em vez de imagens
estáticas empilhadas, os dados são embutidos como JSON e os gráficos são
renderizados em tempo real (Chart.js) com uma barra de filtros: métrica
(tempo/tamanho), recorte por vencedor, Top-N por popularidade e busca por
repositório. Todos os números e gráficos reagem aos filtros.

Uso:
    python dashboard.py
Saída: dashboard/dashboard_lab05.html
"""

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "dashboard"
OUT_HTML = OUT_DIR / "dashboard_lab05.html"


def carregar_dados():
    """Monta a lista de pares por repositório (tempo e tamanho, REST e GraphQL)
    enriquecida com a contagem de estrelas."""
    pares = pd.read_csv(DATA_DIR / "pares.csv")
    wide = pares.pivot_table(
        index="repositorio", columns="api",
        values=["tempo_ms", "tamanho_bytes"], aggfunc="first",
    )
    wide.columns = [f"{a}_{b}" for a, b in wide.columns]
    wide = wide.reset_index()

    estrelas = {}
    repos_json = DATA_DIR / "repositorios.json"
    if repos_json.exists():
        for r in json.loads(repos_json.read_text(encoding="utf-8")):
            estrelas[r["nameWithOwner"]] = r.get("stargazerCount", 0)

    registros = []
    for _, row in wide.iterrows():
        registros.append({
            "repo": row["repositorio"],
            "stars": int(estrelas.get(row["repositorio"], 0)),
            "tempo_REST": round(float(row["tempo_ms_REST"]), 1),
            "tempo_GraphQL": round(float(row["tempo_ms_GraphQL"]), 1),
            "tam_REST": int(row["tamanho_bytes_REST"]),
            "tam_GraphQL": int(row["tamanho_bytes_GraphQL"]),
        })
    registros.sort(key=lambda d: d["stars"], reverse=True)
    return registros


def main():
    for f in ["pares.csv", "resumo_descritivo.csv", "testes_estatisticos.csv"]:
        if not (DATA_DIR / f).exists():
            print(f"Erro: {DATA_DIR / f} não encontrado. Rode analise.py primeiro.", file=sys.stderr)
            sys.exit(1)

    registros = carregar_dados()
    testes = pd.read_csv(DATA_DIR / "testes_estatisticos.csv")
    desc = pd.read_csv(DATA_DIR / "resumo_descritivo.csv")

    t_rq1 = testes[testes["metrica"].str.startswith("RQ1")].iloc[0]
    t_rq2 = testes[testes["metrica"].str.startswith("RQ2")].iloc[0]
    meta = {
        "tempo": {"p": float(t_rq1["p_valor"]), "delta": float(t_rq1["cliffs_delta"]),
                  "mag": str(t_rq1["magnitude_efeito"])},
        "tamanho": {"p": float(t_rq2["p_valor"]), "delta": float(t_rq2["cliffs_delta"]),
                    "mag": str(t_rq2["magnitude_efeito"])},
    }

    dados_json = json.dumps(registros, ensure_ascii=False)
    meta_json = json.dumps(meta, ensure_ascii=False)
    desc_html = desc.to_html(index=False, border=0, classes="tbl")
    testes_html = testes.to_html(index=False, border=0, classes="tbl")
    n_repos = len(registros)

    html = TEMPLATE.format(
        n_repos=n_repos,
        dados_json=dados_json,
        meta_json=meta_json,
        desc_html=desc_html,
        testes_html=testes_html,
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Dashboard gerado em {OUT_HTML}")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lab 05 — GraphQL vs REST · Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --rest:#d1495b; --gql:#30638e; --bg:#eef1f5; --card:#fff; --ink:#1d2733;
    --muted:#6b7785; --line:#e6e9ee;
  }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif; margin:0;
         background:var(--bg); color:var(--ink); }}
  header {{ background:linear-gradient(120deg,#30638e,#1d2733); color:#fff; padding:26px 32px; }}
  header h1 {{ margin:0 0 4px; font-size:24px; }}
  header p {{ margin:0; opacity:.85; font-size:14px; }}
  main {{ max-width:1280px; margin:0 auto; padding:22px 22px 60px; }}

  /* Barra de filtros */
  .filters {{ position:sticky; top:0; z-index:10; background:rgba(255,255,255,.92);
    backdrop-filter:blur(6px); border:1px solid var(--line); border-radius:14px;
    padding:14px 18px; margin-bottom:22px; display:flex; flex-wrap:wrap; gap:18px;
    align-items:flex-end; box-shadow:0 2px 8px rgba(0,0,0,.05); }}
  .fgroup {{ display:flex; flex-direction:column; gap:6px; }}
  .fgroup > label {{ font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--muted); font-weight:600; }}
  .seg {{ display:inline-flex; background:#eef1f5; border-radius:9px; padding:3px; }}
  .seg button {{ border:0; background:transparent; padding:7px 14px; border-radius:7px;
    font-size:13px; cursor:pointer; color:var(--muted); font-weight:600; }}
  .seg button.active {{ background:#fff; color:var(--ink); box-shadow:0 1px 3px rgba(0,0,0,.12); }}
  select, input[type=search] {{ border:1px solid var(--line); border-radius:9px; padding:8px 10px;
    font-size:13px; background:#fff; color:var(--ink); min-width:150px; }}
  .filters .spacer {{ flex:1; }}
  .reset {{ border:1px solid var(--line); background:#fff; border-radius:9px; padding:8px 14px;
    font-size:13px; cursor:pointer; color:var(--muted); }}
  .reset:hover {{ color:var(--ink); }}

  /* KPIs */
  .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin-bottom:22px; }}
  .card {{ background:var(--card); border-radius:14px; padding:16px 18px; box-shadow:0 1px 3px rgba(0,0,0,.07);
    border:1px solid var(--line); }}
  .card-title {{ font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.04em; }}
  .card-value {{ font-size:23px; font-weight:700; margin:6px 0 2px; }}
  .card-sub {{ font-size:12px; color:var(--muted); }}
  .pill {{ display:inline-block; font-size:11px; font-weight:700; padding:2px 8px; border-radius:20px; }}
  .pill.gql {{ background:rgba(48,99,142,.12); color:var(--gql); }}
  .pill.rest {{ background:rgba(209,73,91,.12); color:var(--rest); }}

  /* Layout horizontal de gráficos */
  .grid {{ display:grid; grid-template-columns:repeat(12,1fr); gap:18px; }}
  .panel {{ background:var(--card); border-radius:14px; padding:18px 20px; border:1px solid var(--line);
    box-shadow:0 1px 3px rgba(0,0,0,.06); }}
  .panel h2 {{ margin:0 0 4px; font-size:15px; }}
  .panel .hint {{ margin:0 0 14px; font-size:12px; color:var(--muted); }}
  .col-4 {{ grid-column:span 4; }} .col-6 {{ grid-column:span 6; }}
  .col-8 {{ grid-column:span 8; }} .col-12 {{ grid-column:span 12; }}
  .chart-box {{ position:relative; height:300px; }}
  .chart-tall {{ height:420px; }}
  .bar-scroll {{ max-height:520px; overflow-y:auto; padding-right:6px; }}
  #barWrap {{ position:relative; }}
  @media(max-width:980px) {{ .col-4,.col-6,.col-8 {{ grid-column:span 12; }} }}

  /* Tabela */
  .tbl-wrap {{ overflow:auto; max-height:460px; border-radius:10px; border:1px solid var(--line); }}
  table.tbl {{ border-collapse:collapse; width:100%; font-size:13px; }}
  table.tbl th, table.tbl td {{ padding:8px 12px; text-align:right; border-bottom:1px solid var(--line); white-space:nowrap; }}
  table.tbl th:first-child, table.tbl td:first-child {{ text-align:left; }}
  table.tbl thead th {{ background:#f0f2f5; position:sticky; top:0; cursor:pointer; user-select:none; }}
  table.tbl thead th:hover {{ background:#e6eaf0; }}
  .win-gql {{ color:var(--gql); font-weight:600; }} .win-rest {{ color:var(--rest); font-weight:600; }}
  details {{ margin-top:22px; }}
  details summary {{ cursor:pointer; font-weight:600; padding:8px 0; }}
  footer {{ text-align:center; color:var(--muted); font-size:12px; padding:28px 0 0; }}
</style>
</head>
<body>
<header>
  <h1>GraphQL vs REST — Um experimento controlado</h1>
  <p>Lab 05 · Dashboard interativo · API pública do GitHub · {n_repos} repositórios pareados</p>
</header>
<main>
  <div class="filters">
    <div class="fgroup">
      <label>Métrica</label>
      <div class="seg" id="seg-metric">
        <button data-v="tempo" class="active">⏱ Tempo (ms)</button>
        <button data-v="tamanho">📦 Tamanho (bytes)</button>
      </div>
    </div>
    <div class="fgroup">
      <label>Vencedor</label>
      <div class="seg" id="seg-winner">
        <button data-v="all" class="active">Todos</button>
        <button data-v="gql">GraphQL vence</button>
        <button data-v="rest">REST vence</button>
      </div>
    </div>
    <div class="fgroup">
      <label>Recorte (popularidade)</label>
      <select id="topn">
        <option value="10">Top 10 ★</option>
        <option value="25" selected>Top 25 ★</option>
        <option value="50">Top 50 ★</option>
        <option value="100000">Todos</option>
      </select>
    </div>
    <div class="fgroup" style="flex:1;min-width:180px;">
      <label>Buscar repositório</label>
      <input type="search" id="search" placeholder="ex.: facebook/react">
    </div>
    <button class="reset" id="reset">Limpar filtros</button>
  </div>

  <div class="cards" id="cards"></div>

  <div class="grid">
    <section class="panel col-8" id="barPanel">
      <h2 id="t-bar">Comparação por repositório</h2>
      <div class="bar-scroll"><div id="barWrap"><canvas id="barChart"></canvas></div></div>
    </section>
    <section class="panel col-4" id="donutPanel">
      <h2>Quem vence?</h2>
      <div class="chart-box"><canvas id="donutChart"></canvas></div>
      <div id="winsummary" style="font-size:13px;color:var(--muted);margin-top:10px;"></div>
    </section>

    <section class="panel col-6">
      <h2>Dispersão pareada (REST × GraphQL)</h2>
      <p class="hint">Cada ponto é um repositório. Abaixo da diagonal → GraphQL é menor/mais rápido.</p>
      <div class="chart-box"><canvas id="scatterChart"></canvas></div>
    </section>
    <section class="panel col-6">
      <h2>Distribuição</h2>
      <div class="chart-box"><canvas id="histChart"></canvas></div>
    </section>

    <section class="panel col-12">
      <h2>Dados por repositório</h2>
      <p class="hint">Clique nos cabeçalhos para ordenar. <span id="rowcount"></span></p>
      <div class="tbl-wrap">
        <table class="tbl" id="dataTable">
          <thead><tr>
            <th data-k="repo">Repositório</th>
            <th data-k="stars">★ Stars</th>
            <th data-k="rest">REST</th>
            <th data-k="gql">GraphQL</th>
            <th data-k="diff">Δ (GraphQL−REST)</th>
            <th data-k="winner">Vencedor</th>
          </tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </section>
  </div>

  <details>
    <summary>Estatísticas descritivas e testes de hipótese (Wilcoxon pareado)</summary>
    <div class="grid" style="margin-top:14px;">
      <section class="panel col-6"><h2>Estatísticas descritivas</h2><div class="tbl-wrap">{desc_html}</div></section>
      <section class="panel col-6"><h2>Testes de hipótese</h2><div class="tbl-wrap">{testes_html}</div>
        <p style="font-size:12px;color:var(--muted);margin-top:10px;">Wilcoxon pareado (GraphQL vs REST por repositório). <em>cliffs_delta</em> = tamanho do efeito; p &lt; 0,05 rejeita H₀.</p>
      </section>
    </div>
  </details>

  <footer>Lab 05 — Laboratório de Experimentação de Software · dashboard interativo gerado por dashboard.py</footer>
</main>

<script>
const DADOS = {dados_json};
const META  = {meta_json};
const fmt = new Intl.NumberFormat('pt-BR');
const C = {{ rest:'#d1495b', gql:'#30638e' }};

const state = {{ metric:'tempo', winner:'all', topn:25, search:'', sortK:'stars', sortDir:-1 }};

function starsCompact(n) {{
  if (n >= 1000) return (n/1000).toFixed(n>=10000?0:1).replace('.',',')+'k';
  return ''+n;
}}
function field(d, api) {{ return state.metric === 'tempo' ? d['tempo_'+api] : d['tam_'+api]; }}
function unidade() {{ return state.metric === 'tempo' ? 'ms' : 'bytes'; }}
function winnerOf(d) {{ return field(d,'GraphQL') < field(d,'REST') ? 'gql' : 'rest'; }}

function filtrar() {{
  let rows = DADOS.slice().sort((a,b)=>b.stars-a.stars).slice(0, state.topn);
  if (state.winner !== 'all') rows = rows.filter(d => winnerOf(d) === state.winner);
  if (state.search) {{ const q = state.search.toLowerCase(); rows = rows.filter(d => d.repo.toLowerCase().includes(q)); }}
  return rows;
}}

function mediana(arr) {{
  if (!arr.length) return 0;
  const s = arr.slice().sort((a,b)=>a-b), m = Math.floor(s.length/2);
  return s.length%2 ? s[m] : (s[m-1]+s[m])/2;
}}

let barChart, donutChart, scatterChart, histChart;

function renderCards(rows) {{
  const gql = rows.map(d=>field(d,'GraphQL')), rest = rows.map(d=>field(d,'REST'));
  const mG = mediana(gql), mR = mediana(rest);
  const red = mR ? (1 - mG/mR)*100 : 0;
  const wins = rows.filter(d=>winnerOf(d)==='gql').length;
  const m = META[state.metric];
  const u = unidade();
  const cards = [
    ['Repositórios no recorte', fmt.format(rows.length), 'após filtros'],
    ['Mediana GraphQL', fmt.format(Math.round(mG))+' '+u, '<span class="pill gql">GraphQL</span>'],
    ['Mediana REST', fmt.format(Math.round(mR))+' '+u, '<span class="pill rest">REST</span>'],
    ['Diferença mediana', (red>=0?'−':'+')+Math.abs(red).toFixed(1)+'%',
       red>=0 ? 'GraphQL menor/mais rápido' : 'GraphQL maior/mais lento'],
    ['GraphQL vence em', wins+'/'+rows.length, 'p='+m.p.toExponential(1)+' · efeito '+m.mag],
  ];
  document.getElementById('cards').innerHTML = cards.map(c=>`
    <div class="card"><div class="card-title">${{c[0]}}</div>
      <div class="card-value">${{c[1]}}</div><div class="card-sub">${{c[2]}}</div></div>`).join('');
}}

function renderBar(rows) {{
  const u = unidade();
  document.getElementById('t-bar').textContent =
    `Comparação por repositório — ${{state.metric==='tempo'?'Tempo (ms)':'Tamanho (bytes)'}} · ↓ mais populares no topo`;
  // Altura dinâmica: cada repositório recebe espaço fixo para os rótulos não se sobreporem.
  document.getElementById('barWrap').style.height = Math.max(280, rows.length*32 + 60) + 'px';
  // Rótulo em duas linhas: nome + estrelas, tornando a ordenação por popularidade explícita.
  const labels = rows.map(d=>{{
    const nome = d.repo.length>28 ? d.repo.slice(0,27)+'…' : d.repo;
    return [nome, '★ '+starsCompact(d.stars)];
  }});
  const ds = [
    {{ label:'REST', data:rows.map(d=>field(d,'REST')), backgroundColor:C.rest }},
    {{ label:'GraphQL', data:rows.map(d=>field(d,'GraphQL')), backgroundColor:C.gql }},
  ];
  const cfg = {{
    type:'bar',
    data:{{ labels, datasets:ds }},
    options:{{ indexAxis:'y', responsive:true, maintainAspectRatio:false,
      plugins:{{ legend:{{position:'top'}}, tooltip:{{callbacks:{{label:c=>c.dataset.label+': '+fmt.format(c.parsed.x)+' '+u}}}} }},
      scales:{{ x:{{ title:{{display:true,text:u}} }}, y:{{ ticks:{{autoSkip:false,font:{{size:10}}}} }} }} }}
  }};
  if (barChart) barChart.destroy();
  barChart = new Chart(document.getElementById('barChart'), cfg);
}}

function renderDonut(rows) {{
  const wG = rows.filter(d=>winnerOf(d)==='gql').length, wR = rows.length - wG;
  if (donutChart) donutChart.destroy();
  donutChart = new Chart(document.getElementById('donutChart'), {{
    type:'doughnut',
    data:{{ labels:['GraphQL vence','REST vence'], datasets:[{{ data:[wG,wR], backgroundColor:[C.gql,C.rest] }}] }},
    options:{{ responsive:true, maintainAspectRatio:false, cutout:'62%', plugins:{{legend:{{position:'bottom'}}}} }}
  }});
  const pct = rows.length ? (wG/rows.length*100).toFixed(0) : 0;
  document.getElementById('winsummary').innerHTML =
    `<b>${{pct}}%</b> dos repositórios favorecem <span class="pill gql">GraphQL</span> nesta métrica.`;
}}

function renderScatter(rows) {{
  const u = unidade();
  const pts = rows.map(d=>({{x:field(d,'REST'), y:field(d,'GraphQL'), repo:d.repo}}));
  const max = Math.max(1, ...pts.flatMap(p=>[p.x,p.y]));
  if (scatterChart) scatterChart.destroy();
  scatterChart = new Chart(document.getElementById('scatterChart'), {{
    type:'scatter',
    data:{{ datasets:[
      {{ label:'Repositórios', data:pts, backgroundColor:'rgba(48,99,142,.6)' }},
      {{ type:'line', label:'igualdade', data:[{{x:0,y:0}},{{x:max,y:max}}], borderColor:'#bbb',
         borderDash:[6,5], pointRadius:0, fill:false }}
    ] }},
    options:{{ responsive:true, maintainAspectRatio:false,
      plugins:{{ legend:{{display:false}},
        tooltip:{{callbacks:{{label:c=>c.raw.repo?`${{c.raw.repo}} — REST ${{fmt.format(c.raw.x)}} / GQL ${{fmt.format(c.raw.y)}}`:''}}}} }},
      scales:{{ x:{{title:{{display:true,text:'REST ('+u+')'}}}}, y:{{title:{{display:true,text:'GraphQL ('+u+')'}}}} }} }}
  }});
}}

function renderHist(rows) {{
  const u = unidade();
  const all = rows.flatMap(d=>[field(d,'REST'),field(d,'GraphQL')]);
  const lo = Math.min(...all), hi = Math.max(...all), bins = 12, w = (hi-lo)/bins || 1;
  const labels = [], gB = Array(bins).fill(0), rB = Array(bins).fill(0);
  for (let i=0;i<bins;i++) labels.push(fmt.format(Math.round(lo+i*w)));
  rows.forEach(d=>{{
    let gi = Math.min(bins-1, Math.floor((field(d,'GraphQL')-lo)/w));
    let ri = Math.min(bins-1, Math.floor((field(d,'REST')-lo)/w));
    gB[gi]++; rB[ri]++;
  }});
  if (histChart) histChart.destroy();
  histChart = new Chart(document.getElementById('histChart'), {{
    type:'bar',
    data:{{ labels, datasets:[
      {{label:'REST', data:rB, backgroundColor:'rgba(209,73,91,.65)'}},
      {{label:'GraphQL', data:gB, backgroundColor:'rgba(48,99,142,.65)'}} ]}},
    options:{{ responsive:true, maintainAspectRatio:false, plugins:{{legend:{{position:'top'}}}},
      scales:{{ x:{{title:{{display:true,text:u}},stacked:false}}, y:{{title:{{display:true,text:'nº de repositórios'}}}} }} }}
  }});
}}

function renderTable(rows) {{
  const sorted = rows.slice().sort((a,b)=>{{
    let va, vb;
    switch(state.sortK) {{
      case 'repo': va=a.repo; vb=b.repo; return state.sortDir*va.localeCompare(vb);
      case 'stars': va=a.stars; vb=b.stars; break;
      case 'rest': va=field(a,'REST'); vb=field(b,'REST'); break;
      case 'gql': va=field(a,'GraphQL'); vb=field(b,'GraphQL'); break;
      case 'diff': va=field(a,'GraphQL')-field(a,'REST'); vb=field(b,'GraphQL')-field(b,'REST'); break;
      case 'winner': va=winnerOf(a); vb=winnerOf(b); return state.sortDir*va.localeCompare(vb);
      default: va=a.stars; vb=b.stars;
    }}
    return state.sortDir*(va-vb);
  }});
  const u = unidade();
  document.querySelector('#dataTable tbody').innerHTML = sorted.map(d=>{{
    const r=field(d,'REST'), g=field(d,'GraphQL'), diff=g-r, w=winnerOf(d);
    return `<tr>
      <td>${{d.repo}}</td><td>${{fmt.format(d.stars)}}</td>
      <td>${{fmt.format(r)}} ${{u}}</td><td>${{fmt.format(g)}} ${{u}}</td>
      <td>${{(diff>=0?'+':'')+fmt.format(Math.round(diff))}} ${{u}}</td>
      <td class="${{w==='gql'?'win-gql':'win-rest'}}">${{w==='gql'?'GraphQL':'REST'}}</td>
    </tr>`;
  }}).join('');
  document.getElementById('rowcount').textContent = `${{sorted.length}} repositórios exibidos`;
}}

function render() {{
  const rows = filtrar();
  // O donut "quem vence?" perde o sentido sob o filtro de vencedor (vira sempre 100%).
  // Nesse caso ocultamos o painel e o gráfico de barras ocupa a largura total.
  const mostraDonut = state.winner === 'all';
  document.getElementById('donutPanel').style.display = mostraDonut ? '' : 'none';
  document.getElementById('barPanel').classList.toggle('col-8', mostraDonut);
  document.getElementById('barPanel').classList.toggle('col-12', !mostraDonut);

  renderCards(rows); renderBar(rows);
  if (mostraDonut) renderDonut(rows);
  renderScatter(rows); renderHist(rows); renderTable(rows);
}}

// Eventos
function segHandler(id, key) {{
  document.querySelectorAll('#'+id+' button').forEach(b=>b.addEventListener('click',()=>{{
    document.querySelectorAll('#'+id+' button').forEach(x=>x.classList.remove('active'));
    b.classList.add('active'); state[key]=b.dataset.v; render();
  }}));
}}
segHandler('seg-metric','metric'); segHandler('seg-winner','winner');
document.getElementById('topn').addEventListener('change', e=>{{ state.topn=+e.target.value; render(); }});
document.getElementById('search').addEventListener('input', e=>{{ state.search=e.target.value.trim(); render(); }});
document.querySelectorAll('#dataTable thead th').forEach(th=>th.addEventListener('click',()=>{{
  const k=th.dataset.k; state.sortDir = (state.sortK===k) ? -state.sortDir : -1; state.sortK=k; render();
}}));
document.getElementById('reset').addEventListener('click', ()=>{{
  state.winner='all'; state.topn=25; state.search='';
  document.getElementById('topn').value='25'; document.getElementById('search').value='';
  document.querySelectorAll('#seg-winner button').forEach((b,i)=>b.classList.toggle('active',i===0));
  render();
}});

render();
</script>
</body>
</html>"""


if __name__ == "__main__":
    main()

# Guia de Montagem do Dashboard — Power BI (LAB04)

Dashboard de BI para o artigo **"Análise do Impacto do Tamanho Médio dos Commits na
Manutenibilidade de Sistemas de Software em Python"** (TIS 6).

Este guia mapeia **cada CSV** desta pasta para **cada visual** do dashboard, com tipo de
gráfico, eixos, medida de tendência central e o texto narrativo que deve acompanhar a
visualização (o dashboard precisa ser **auto-explicativo**, conforme o enunciado do
laboratório).

> **Estrutura recomendada:** 4 páginas (abas) no relatório Power BI —
> `0 · Caracterização`, `1 · Q1 Bugs`, `2 · Q2 Revisão`, `3 · Q3 Manutenibilidade`.

---

## 0. Importação dos dados

1. **Obter dados → Texto/CSV** e importe **todos** os `*.csv` desta pasta.
   - Encoding: **65001: Unicode (UTF-8)** (preserva os acentos e os símbolos `≤ → χ²`).
   - Confira os tipos: colunas `*_pct`, `*_loc`, `taxa_*`, `media_*`, `mediana_*` como
     **Número decimal**; `n_*`, `loc`, `arquivos`, `comentarios_total` como **Número inteiro**.
2. As tabelas-resumo (`02_q1_taxa...`, `03_q2_resumo...`, `04_q3_resumo...`) já estão
   **pré-agregadas**: arraste os campos direto, **sem** medidas de agregação extras
   (use *"Não resumir"* / *Don't summarize* nos eixos categóricos).
3. Para ordenar as classes corretamente (Pequeno → Médio → Grande), os campos
   `classe_tamanho` / `categoria_tamanho` já vêm prefixados com `1.`, `2.`, `3.`.
   Use **Classificar por coluna** se quiser esconder o prefixo numérico.

---

## Página 0 · Caracterização do Dataset

Conta o que é o dataset: **500 repositórios Python populares do GitHub**, selecionados por
linguagem principal, janela de 5 anos, > 4 contribuidores, ≥ 100 commits e atividade no
último ano (Seção 3.2 do artigo).

| # | Visual | Tipo | Campos | Fonte |
|---|--------|------|--------|-------|
| 0.1 | **KPIs do dataset** | 3 Cartões | `total` de cada métrica | `01b_caracterizacao_resumo.csv` |
| 0.2 | **Distribuição de estrelas** | Gráfico de colunas | Eixo X: `faixa_stars` · Eixo Y: `Contagem de repo_full` | `01_caracterizacao_repositorios.csv` |
| 0.3 | **Distribuição de contribuidores** | Gráfico de colunas | Eixo X: `faixa_contributors` · Y: contagem de repos | `01_caracterizacao_repositorios.csv` |
| 0.4 | **Distribuição de commits (5 anos)** | Gráfico de colunas | Eixo X: `faixa_commits` · Y: contagem de repos | `01_caracterizacao_repositorios.csv` |
| 0.5 | **Top 15 repositórios por estrelas** | Barras horizontais | Eixo Y: `repo_full` · X: `stars` (Top N = 15 por stars) | `01_caracterizacao_repositorios.csv` |
| 0.6 | **Subgrupos: commits por classe de tamanho** | Rosca / Treemap | Legenda: `classe_tamanho` · Valor: `n_commits` | `01c_caracterizacao_commits_por_classe.csv` |

- **Medida de tendência central:** nos cartões 0.1, mostre **mediana** *e* **média**
  (a coluna existe nas duas formas) — as distribuições de stars/commits são bem
  assimétricas, então deixe claro qual está sendo usada no rótulo.
- **Texto narrativo (caixa de texto no topo):**
  *"O estudo analisa 500 repositórios Python populares do GitHub (mediana de 23.174
  estrelas e 1.234 commits no período). Como as análises particionam os dados por classe
  de tamanho (Hattori & Lanza, 2008), apresentamos também a composição do universo de
  1.675.148 commits: 51,4% pequenos, 37,1% médios e 11,4% grandes."*

> **Subgrupos (exigência do enunciado):** o visual 0.6 cumpre o requisito de caracterizar
> também os subgrupos usados nas comparações. A partição por **classe de tamanho de
> commit/PR** é a característica que segmenta todas as RQs.

---

## Página 1 · Q1 — Tamanho do commit × ocorrência de bugs

> **Pergunta (caixa de texto):** *"Q1 — Qual a relação entre o tamanho do commit e a
> ocorrência de bugs?"*

| # | Visual | Tipo | Campos | Fonte |
|---|--------|------|--------|-------|
| 1.1 | **Taxa de BICs por classe de tamanho** | Colunas + rótulo de dados | X: `classe_tamanho` · Y: `taxa_bic_pct` | `02_q1_taxa_bic_por_classe.csv` |
| 1.2 | **Composição das classes: BIC vs não-BIC** | Colunas 100% empilhadas | X: `grupo` · Y: `pct_dentro_grupo` · Legenda: `classe_tamanho` | `02_q1_distribuicao_classes_por_grupo.csv` |
| 1.3 | **Correlação por repositório** | Dispersão (scatter) | X: `pct_grande` · Y: `taxa_bic_pct` · Detalhe: `repo_full` · Tamanho: `n_commits` | `02_q1_por_repositorio.csv` |
| 1.4 | **Testes estatísticos** | Tabela / Cartões | `analise`, `estatistica`, `p_valor`, `significativo` | `02_q1_testes_estatisticos.csv` |

- **Medida:** taxa de BICs = **proporção** (`n_bic / n_commits`), já calculada em
  `taxa_bic_pct`. Para o tooltip do 1.1, adicione `loc_mediana` e `arquivos_mediana`
  (use **mediana**, pois LOC é fortemente assimétrico).
- No 1.1, ative o **intervalo de confiança** como barras de erro usando
  `ic95_inf_pct` / `ic95_sup_pct` (Analytics → Error bars; ou tooltip).
- No 1.3, adicione uma **linha de tendência** (Analytics → Trend line) para evidenciar o
  ρ = 0,10.
- **Narrativa de fechamento:**
  *"A taxa de BICs cresce monotonicamente de 0,82% (pequenos) → 2,90% (médios) → 6,98%
  (grandes): ~8,5× entre os extremos (Cochran-Armitage Z=163,5; p<1e-50). Entre os BICs,
  34,8% são commits grandes; entre os não-BICs, apenas 10,9%. **Hipótese comprovada.**"*

---

## Página 2 · Q2 — Tamanho do PR × complexidade da revisão

> **Pergunta:** *"Q2 — O tamanho do pull request influencia a complexidade da revisão de
> código?"*

| # | Visual | Tipo | Campos | Fonte |
|---|--------|------|--------|-------|
| 2.1 | **Volume médio de comentários por categoria** | Colunas | X: `categoria_tamanho` · Y: `media_comentarios_M2_3` | `03_q2_resumo_categoria.csv` |
| 2.2 | **Densidade de comentários por LOC** | Colunas | X: `categoria_tamanho` · Y: `mediana_coment_por_loc_M2_3l` | `03_q2_resumo_categoria.csv` |
| 2.3 | **Tempo até o fechamento por faixa de LOC** | Colunas | X: `faixa_loc` · Y: `mediana_horas_fechamento` | `03_q2_fechamento_por_faixa_loc.csv` |
| 2.4 | **Testes estatísticos** | Tabela | `analise`, `estatistica`, `p_valor`, `significativo` | `03_q2_testes_estatisticos.csv` |
| 2.5 | *(opcional, exploratório)* **Dispersão LOC × comentários** | Scatter | X: `loc` · Y: `comentarios_total` · Legenda: `categoria_tamanho` | `03_q2_pr_classificado.csv` |

- **Medida:** comentários médios = **média** (M2.3); densidade e tempos = **mediana**
  (M2.3′/M2.4/M2.5), pois são distribuições com cauda longa. Os nomes das colunas já
  trazem o código da métrica (M2.x) — mantenha-os no rótulo do eixo.
- **2.5** usa a base bruta `03_q2_pr_classificado.csv` (1 linha por PR). No eixo X aplique
  **escala logarítmica** (formatação do eixo) para reproduzir o `log1p(LOC)` do artigo.
  Filtre `loc > 0`.
- **Narrativa:**
  *"PRs grandes recebem mais comentários no agregado (1,58 → 2,45 → 5,67) e levam mais
  tempo até o fechamento (3,95h → 12,70h por faixa de LOC). Porém, a densidade de
  comentários por linha **cai** (0,125 → 0,024 → 0,004): a revisão de mudanças extensas é
  proporcionalmente mais superficial (Spearman ρ=−0,50 em S3). **Hipótese comprovada de
  forma parcial e qualificada.**"*

> ⚠️ **Nota de consistência (Q2):** as tabelas-resumo 2.1–2.3 reproduzem os números
> **publicados no artigo** (base curada de 69.615 PRs). A base bruta `03_q2_pr_classificado.csv`
> contém **102.265 PRs** (todos os coletados, sem a curadoria final do Q2, cujo script não
> está versionado). As tendências e medianas são praticamente idênticas — ex.: densidade
> mediana 0,125 / 0,024 / 0,004 bate exatamente. Use as tabelas-resumo para os cartões/barras
> oficiais e a base bruta apenas para o scatter exploratório 2.5. Se for usar a base bruta nos
> números oficiais, alinhe antes o filtro de curadoria com quem rodou a análise do Q2.

---

## Página 3 · Q3 — Tamanho do commit × manutenibilidade

> **Pergunta:** *"Q3 — Qual a relação do tamanho dos commits com a manutenibilidade do
> código?"*

| # | Visual | Tipo | Campos | Fonte |
|---|--------|------|--------|-------|
| 3.1 | **Densidade de complexidade ciclomática (CC/LOC)** | Colunas | X: `categoria_tamanho` · Y: `cc_por_loc_M3_2` | `04_q3_resumo_categoria.csv` |
| 3.2 | **Taxa de reverts por categoria** | Colunas | X: `categoria_tamanho` · Y: `taxa_revert_pct_M3_3` | `04_q3_resumo_categoria.csv` |
| 3.3 | **Taxa de bug fixes por categoria** | Colunas | X: `categoria_tamanho` · Y: `taxa_bugfix_pct` | `04_q3_resumo_categoria.csv` |
| 3.4 | **Indicadores por categoria** | Tabela | todas as colunas | `04_q3_resumo_categoria.csv` |
| 3.5 | **Leitura dos resultados** | Tabela | `analise`, `estatistica`, `interpretacao` | `04_q3_testes_estatisticos.csv` |

- **Medida:** todas as colunas já são **médias/taxas por categoria** (560.667 commits).
  No tooltip do 3.1–3.3, inclua `media_loc_M3_1` (média de LOC) para contextualizar o
  tamanho de cada classe.
- **Narrativa:**
  *"Quanto maior o commit, menor a densidade lógica (CC/LOC 1,96 → 0,16 → 0,04) e maior a
  taxa de reverts (1,26% → 1,99% → 3,56%, ~2,8×). A taxa de bug fixes também cai
  (36,2% → 31,2%). Commits menores favorecem correções atômicas e um ciclo de manutenção
  mais ágil. **Hipótese comprovada.**"*

---

## Medidas DAX úteis (opcionais)

Caso prefira calcular dinamicamente em vez de usar as colunas pré-agregadas:

```DAX
-- Taxa de BIC por repositório (se usar base bruta de commits)
Taxa BIC % = DIVIDE(SUM('commits'[is_bic]), COUNTROWS('commits')) * 100

-- Comentários por LOC (base 03_q2_pr_classificado, mediana)
Mediana Coment/LOC = MEDIANX(FILTER('03_q2_pr_classificado', '03_q2_pr_classificado'[loc] > 0),
                              '03_q2_pr_classificado'[comentarios_por_loc])

-- % de PRs grandes por repositório
% PRs Grandes = DIVIDE(
    CALCULATE(COUNTROWS('03_q2_pr_classificado'), '03_q2_pr_classificado'[categoria_tamanho] = "3. Grande"),
    COUNTROWS('03_q2_pr_classificado')) * 100
```

---

## Paleta sugerida (consistência visual entre páginas)

Use a mesma cor por classe de tamanho em **todas** as páginas:

| Classe | Cor sugerida (hex) |
|--------|--------------------|
| Pequeno | `#2E7D32` (verde — desejável) |
| Médio | `#F9A825` (amarelo) |
| Grande | `#C62828` (vermelho — risco) |

---

## Exportação final (entrega)

1. **Arquivo → Exportar → PDF** (entrega o dashboard em PDF, exigência do LAB04).
2. Inserir as figuras no artigo `Artigo/relatorio.tex`:
   - **Caracterização (Página 0)** → Seção 3 (Metodologia).
   - **Q1/Q2/Q3 (Páginas 1–3)** → Seção 4 (Resultados).
   - Cada figura deve ser **citada e explicada** no texto.

---

## Mapa rápido CSV → visual

| CSV | Página | Visual(is) |
|-----|--------|-----------|
| `01_caracterizacao_repositorios.csv` | 0 | 0.2, 0.3, 0.4, 0.5 |
| `01b_caracterizacao_resumo.csv` | 0 | 0.1 (KPIs) |
| `01c_caracterizacao_commits_por_classe.csv` | 0 | 0.6 |
| `02_q1_taxa_bic_por_classe.csv` | 1 | 1.1 |
| `02_q1_distribuicao_classes_por_grupo.csv` | 1 | 1.2 |
| `02_q1_por_repositorio.csv` | 1 | 1.3 |
| `02_q1_testes_estatisticos.csv` | 1 | 1.4 |
| `03_q2_resumo_categoria.csv` | 2 | 2.1, 2.2 |
| `03_q2_fechamento_por_faixa_loc.csv` | 2 | 2.3 |
| `03_q2_testes_estatisticos.csv` | 2 | 2.4 |
| `03_q2_pr_classificado.csv` | 2 | 2.5 (exploratório) |
| `04_q3_resumo_categoria.csv` | 3 | 3.1, 3.2, 3.3, 3.4 |
| `04_q3_testes_estatisticos.csv` | 3 | 3.5 |

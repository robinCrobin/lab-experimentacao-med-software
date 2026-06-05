# Dashboard Power BI — LAB04

CSVs prontos para montar o dashboard do artigo **"Análise do Impacto do Tamanho Médio dos
Commits na Manutenibilidade de Sistemas de Software em Python"** (TIS 6 + LAB04).

## Conteúdo

- **12 CSVs** (UTF-8, ~16 MB) — um para cada seção do dashboard.
- **GUIA_DASHBOARD_POWERBI.md** — instruções passo a passo para montar cada visual em Power BI.

## Estrutura do dashboard (4 páginas)

### 0 · Caracterização do dataset
Apresenta os 500 repositórios Python populares (distribuições de stars, contribuidores,
commits) e os subgrupos por classe de tamanho (Hattori & Lanza, 2008).

**CSVs:**
- `01_caracterizacao_repositorios.csv` — repositórios com faixas pré-binadas
- `01b_caracterizacao_resumo.csv` — KPIs (mediana, média)
- `01c_caracterizacao_commits_por_classe.csv` — universo de 1,67M commits por classe

### 1 · Q1 — Tamanho do commit × ocorrência de bugs
Tamanho está associado a 8,5× maior taxa de BIC (pequeno 0,82% → grande 6,98%).

**CSVs:**
- `02_q1_taxa_bic_por_classe.csv` — taxa com IC95%
- `02_q1_distribuicao_classes_por_grupo.csv` — composição BIC vs não-BIC
- `02_q1_por_repositorio.csv` — 395 repos (scatter)
- `02_q1_testes_estatisticos.csv` — Cochran-Armitage, Qui-quadrado, Cramer's V, Spearman

### 2 · Q2 — Tamanho do PR × complexidade da revisão
PRs maiores têm mais comentários (1,58 → 5,67) mas **menor densidade** (0,125 → 0,004),
levam mais tempo até fechamento (3,95h → 12,70h).

**CSVs:**
- `03_q2_resumo_categoria.csv` — Tabela 1 (69.615 PRs, exatos do artigo)
- `03_q2_pr_classificado.csv` — 69.615 PRs (por-entidade, para scatter/box)
- `03_q2_fechamento_por_faixa_loc.csv` — Figura 6 (tempo × LOC)
- `03_q2_testes_estatisticos.csv` — Spearman ρ, Mann-Whitney

### 3 · Q3 — Tamanho do commit × manutenibilidade
Commits maiores têm menor densidade ciclomática (CC/LOC 1,96 → 0,04), maior taxa de
reverts (1,26% → 3,56%).

**CSVs:**
- `04_q3_resumo_categoria.csv` — Tabela 2 (LOC, CC/LOC, reverts, bug fixes)
- `04_q3_testes_estatisticos.csv` — leitura dos resultados

## Como usar

1. Abra Power BI Desktop.
2. **Obter dados → Texto/CSV** e importe **todos** os CSVs da pasta.
   - Encoding: **UTF-8 (65001)**.
3. Segue a **GUIA_DASHBOARD_POWERBI.md** para montar os 4 painéis.
4. Exportar como **PDF** (entrega do LAB04).
5. Inserir figuras no `Artigo/relatorio.tex` (Seção 3 = Metodologia, Seção 4 = Resultados).

## Notas

- Os **números da Tabela 1 (Q2)** reproduzem exatamente o artigo publicado (base de 69.615 PRs curada).
- O arquivo `03_q2_pr_classificado.csv` contém os mesmos 69.615 PRs, permitindo visuals exploratórios (scatter, box plots, histogramas) no Power BI.
- Todas as colunas de classe (`classe_tamanho`, `categoria_tamanho`) estão prefixadas com `1./2./3.` para ordenação automática correta.

---

**Gerado por:** `Instrumentos/Codigos/gerar_dados_dashboard.py`  
**Data:** 2026-06-05

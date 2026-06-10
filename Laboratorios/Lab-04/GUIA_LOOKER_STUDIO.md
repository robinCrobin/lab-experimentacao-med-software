# Guia de Montagem do Dashboard — Google Looker Studio (LAB04)

Dashboard de BI para o artigo **"Análise do Impacto do Tamanho Médio dos Commits na
Manutenibilidade de Sistemas de Software em Python"** (TIS 6).

Ferramenta: **Google Looker Studio** (antigo Data Studio) — grátis, roda no navegador
(funciona no Mac), importa CSV e exporta PDF. Atende ao requisito do enunciado de usar
*Power BI, Tableau **ou** Google Data Studio*.

> **Estrutura:** 4 páginas no relatório —
> `0 · Caracterização`, `1 · Q1 Bugs`, `2 · Q2 Revisão`, `3 · Q3 Manutenibilidade`.
> O dashboard precisa ser **auto-explicativo**: cada página começa com a pergunta e os
> textos narrativos abaixo.

---

## 0. Importação dos dados

1. Acesse **https://lookerstudio.google.com** e clique em **Criar → Relatório**.
2. Conector **"Upload de arquivo" (File Upload)** → arraste os CSVs **desta pasta**
   (`dados_looker/`). Cada CSV vira uma **fonte de dados** separada.
3. Após subir cada arquivo, confira os **tipos** no painel da fonte de dados:
   - Campos `*_pct`, `*_loc`, `taxa_*`, `media_*`, `mediana_*`, `cc_*`, `n_*` → **Número**
     (ícone 123). Se algum vier como texto (Aa), clique e troque o tipo.
   - Campos `classe_tamanho`, `categoria_tamanho`, `faixa_*`, `grupo`, `repo_full`,
     `metrica`, `analise` → **Texto**.
4. **Ordenação das classes:** os valores já vêm prefixados (`1. Pequeno`, `2. Médio`,
   `3. Grande`). Em cada gráfico, ordene pela própria dimensão **crescente** para obter
   Pequeno → Médio → Grande. (Para esconder o `1.`/`2.`/`3.` na exibição, crie um campo
   calculado opcional — ver fim do guia.)
5. **Agregação:** as tabelas-resumo já estão pré-agregadas (1 linha por classe). Ao usar
   uma métrica dessas, troque a agregação do campo para **Máximo** (ou Média) — assim o
   Looker mostra o valor da linha, sem somar.

### Mapa rápido CSV → página
| CSV | Página | Visuais |
|-----|--------|---------|
| `01b_caracterizacao_resumo.csv` | 0 | 0.1 (KPIs) |
| `caracterizacao_distribuicoes.csv` | 0 | 0.2 (distribuições) |
| `01_caracterizacao_repositorios.csv` | 0 | 0.3 (Top 15) |
| `01c_caracterizacao_commits_por_classe.csv` | 0 | 0.4 (rosca) |
| `q1_taxa_bic_ic.csv` | 1 | 1.1 |
| `02_q1_distribuicao_classes_por_grupo.csv` | 1 | 1.2 |
| `02_q1_por_repositorio.csv` | 1 | 1.3 |
| `02_q1_testes_estatisticos.csv` | 1 | 1.4 |
| `03_q2_resumo_categoria.csv` | 2 | 2.1, 2.2 |
| `03_q2_fechamento_por_faixa_loc.csv` | 2 | 2.3 |
| `03_q2_testes_estatisticos.csv` | 2 | 2.4 |
| `04_q3_resumo_categoria.csv` | 3 | 3.1, 3.2, 3.3, 3.4 |
| `04_q3_testes_estatisticos.csv` | 3 | 3.5 |

---

## Página 0 · Caracterização do Dataset

**Caixa de texto (topo):**
> *"O estudo analisa 500 repositórios Python populares do GitHub (mediana de 23.174
> estrelas e 1.234 commits no período). Como as análises particionam os dados por classe
> de tamanho de commit (Hattori & Lanza, 2008), apresentamos também a composição do
> universo de 1.675.148 commits: 51,4% pequenos, 37,1% médios e 11,4% grandes."*

| # | Visual | Tipo no Looker | Configuração |
|---|--------|----------------|--------------|
| 0.1 | **KPIs do dataset** | 3× **Scorecard** | Fonte `01b...resumo`. Cada scorecard: métrica = `mediana` (agreg. **Máximo**) + **filtro** `metrica` = *Estrelas (stars)* / *Contribuidores* / *Commits (5 anos)*. Renomeie o rótulo. |
| 0.2 | **Distribuições** | **Gráfico de colunas** + **controle** | Fonte `caracterizacao_distribuicoes`. Dimensão = `faixa`; Métrica = `n_repositorios` (Soma). Adicione um **Controle de lista suspensa** com a dimensão `dimensao` para alternar Estrelas/Contribuidores/Commits. |
| 0.3 | **Top 15 repositórios por estrelas** | **Barras horizontais** | Fonte `01_caracterizacao_repositorios`. Dimensão = `repo_full`; Métrica = `stars` (Máx); ordenar `stars` desc.; **Linhas por página = 15**. |
| 0.4 | **Commits por classe de tamanho** | **Rosca (Donut)** | Fonte `01c...commits_por_classe`. Dimensão = `classe_tamanho`; Métrica = `n_commits`. Aplique as cores da paleta (abaixo). |

- **Tendência central:** nos KPIs use **mediana** (stars/commits são assimétricos). Se
  quiser mostrar média também, duplique o scorecard usando o campo `media`.
- **Subgrupos (exigência do enunciado):** o visual 0.4 cumpre o requisito de caracterizar
  os subgrupos (classes de tamanho) que segmentam todas as RQs.

---

## Página 1 · Q1 — Tamanho do commit × ocorrência de bugs

**Caixa de texto:** *"Q1 — Qual a relação entre o tamanho do commit e a ocorrência de bugs?"*

| # | Visual | Tipo | Configuração |
|---|--------|------|--------------|
| 1.1 | **Taxa de BICs por classe** | **Colunas** | Fonte `q1_taxa_bic_ic`. Dimensão = `classe_tamanho`; Métrica = `taxa_bic_pct` (Máx). Rótulo de dados ON. *(O Looker não tem barra de erro nativa: mostre o IC95 no **tooltip** adicionando `ic95_inf_pct` e `ic95_sup_pct`, ou cite no texto.)* |
| 1.2 | **BIC vs não-BIC** | **Colunas 100% empilhadas** | Fonte `02_q1_distribuicao_classes_por_grupo`. Dimensão = `grupo`; Detalhamento (breakdown) = `classe_tamanho`; Métrica = `pct_dentro_grupo` (Máx); empilhamento **100%**. |
| 1.3 | **Correlação por repositório** | **Dispersão (Scatter)** | Fonte `02_q1_por_repositorio`. Dim. = `repo_full`; X = `pct_grande`; Y = `taxa_bic_pct`; Tamanho da bolha = `n_commits`. Ative **Linha de tendência** (aba Estilo → Tendência → Linear) para evidenciar ρ=0,10. |
| 1.4 | **Testes estatísticos** | **Tabela** | Fonte `02_q1_testes_estatisticos`. Colunas: `analise`, `estatistica`, `p_valor`, `significativo`, `interpretacao`. |

**Eixos:** rotule Y de 1.1 como **"Taxa de BICs (%)"** e X de 1.3 como **"% de commits grandes no repositório"**.

**Narrativa de fechamento:**
> *"A taxa de BICs cresce monotonicamente: 0,82% (pequenos) → 2,90% (médios) → 6,98%
> (grandes), ~8,5× entre os extremos (Cochran-Armitage Z=163,5; p<1e-50). Entre os BICs,
> 34,8% são commits grandes; entre os não-BICs, apenas 10,9%. **Hipótese comprovada.**"*

---

## Página 2 · Q2 — Tamanho do PR × complexidade da revisão

**Caixa de texto:** *"Q2 — O tamanho do pull request influencia a complexidade da revisão de código?"*

| # | Visual | Tipo | Configuração |
|---|--------|------|--------------|
| 2.1 | **Comentários médios por categoria** | **Colunas** | Fonte `03_q2_resumo_categoria`. Dim. = `categoria_tamanho`; Métrica = `media_comentarios_M2_3` (Máx). |
| 2.2 | **Densidade de comentários por LOC** | **Colunas** | Mesma fonte. Métrica = `mediana_coment_por_loc_M2_3l` (Máx). Formate o número com **3 casas decimais**. |
| 2.3 | **Tempo até o fechamento por faixa de LOC** | **Colunas** | Fonte `03_q2_fechamento_por_faixa_loc`. Dim. = `faixa_loc`; Métrica = `mediana_horas_fechamento` (Máx). |
| 2.4 | **Testes estatísticos** | **Tabela** | Fonte `03_q2_testes_estatisticos`. |

**Eixos:** Y de 2.1 = **"Média de comentários (M2.3)"**; Y de 2.2 = **"Comentários por LOC — mediana (M2.3′)"**; Y de 2.3 = **"Horas até o fechamento (mediana)"**.

**Medida:** comentários médios = **média**; densidade e tempos = **mediana** (cauda longa).

**Narrativa:**
> *"PRs grandes recebem mais comentários no agregado (1,58 → 2,45 → 5,67) e levam mais
> tempo até o fechamento (3,95h → 12,70h por faixa de LOC). Porém, a densidade de
> comentários por linha **cai** (0,125 → 0,024 → 0,004): a revisão de mudanças extensas é
> proporcionalmente mais superficial (Spearman ρ=−0,50). **Hipótese comprovada de forma
> parcial.**"*

---

## Página 3 · Q3 — Tamanho do commit × manutenibilidade

**Caixa de texto:** *"Q3 — Qual a relação do tamanho dos commits com a manutenibilidade do código?"*

| # | Visual | Tipo | Configuração |
|---|--------|------|--------------|
| 3.1 | **Densidade de complexidade (CC/LOC)** | **Colunas** | Fonte `04_q3_resumo_categoria`. Dim. = `categoria_tamanho`; Métrica = `cc_por_loc_M3_2` (Máx). |
| 3.2 | **Taxa de reverts** | **Colunas** | Mesma fonte. Métrica = `taxa_revert_pct_M3_3` (Máx). |
| 3.3 | **Taxa de bug fixes** | **Colunas** | Mesma fonte. Métrica = `taxa_bugfix_pct` (Máx). |
| 3.4 | **Indicadores por categoria** | **Tabela** | Mesma fonte; todas as colunas. |
| 3.5 | **Leitura dos resultados** | **Tabela** | Fonte `04_q3_testes_estatisticos`. |

**Eixos:** Y de 3.1 = **"CC / LOC"**; 3.2 = **"Taxa de reverts (%)"**; 3.3 = **"Taxa de bug fixes (%)"**.

**Narrativa:**
> *"Quanto maior o commit, menor a densidade lógica (CC/LOC 1,96 → 0,16 → 0,04) e maior a
> taxa de reverts (1,26% → 1,99% → 3,56%, ~2,8×). A taxa de bug fixes também cai
> (36,2% → 31,2%). Commits menores favorecem correções atômicas e manutenção mais ágil.
> **Hipótese comprovada.**"*

---

## Paleta (use a mesma cor por classe em TODAS as páginas)

Em cada gráfico com classe/categoria, vá em **Estilo → Cores por dimensão** e fixe:

| Classe | Hex |
|--------|-----|
| `1. Pequeno` | `#2E7D32` (verde — desejável) |
| `2. Médio` | `#F9A825` (amarelo) |
| `3. Grande` | `#C62828` (vermelho — risco) |

---

## (Opcional) Esconder o prefixo "1." / "2." / "3."

Mantém a ordenação correta mas exibe o rótulo limpo. Em **Adicionar campo calculado**:

```
REGEXP_REPLACE(classe_tamanho, '^[0-9]+\\. ', '')
```

Use o campo original (`classe_tamanho`) para **Ordenar por** e o campo calculado para exibir.
(O Looker não permite ordenar por outro campo diretamente em todos os gráficos; se der
conflito, mantenha o prefixo — é aceitável.)

---

## Exportação final (entrega)

1. Canto superior direito → **Compartilhar → Fazer download** (ou **Arquivo → Download**)
   → **PDF**. Marque "todas as páginas". Esse PDF é a entrega do dashboard (LAB04).
2. Também **Compartilhe o link** (Compartilhar → qualquer pessoa com o link pode ver) e
   coloque no README do Lab-04.
3. Insira as figuras no artigo de TIS 6:
   - **Caracterização (Página 0)** → Seção 3 (Metodologia).
   - **Q1/Q2/Q3 (Páginas 1–3)** → Seção 4 (Resultados).
   - Cada figura deve ser **citada e explicada** no texto.

---

## Checklist de requisitos do enunciado

- [ ] Dashboard feito em ferramenta de BI nomeada (Looker Studio) ✔ ao concluir este guia
- [ ] Caracterização do dataset **completo** (KPIs, distribuições, Top 15)
- [ ] Caracterização dos **subgrupos** (classes de tamanho — visual 0.4)
- [ ] Uma+ visualização por RQ (Q1, Q2, Q3) com **todas as métricas**
- [ ] Dashboard **auto-explicativo** (pergunta + narrativa em cada página)
- [ ] **Medidas de tendência central** adequadas (mediana p/ assimétricos) e **labels claras**
- [ ] Dashboard exportado em **PDF**
- [ ] Artigo de TIS 6 atualizado com os gráficos (citados e explicados)

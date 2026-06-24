# Lab 05 — Desenho do Experimento (Sprint Lab05S01)

## GraphQL vs REST — Um experimento controlado

Este documento descreve o **desenho** (Passo 1) e a **preparação** (Passo 2) do
experimento controlado proposto no Lab 05. O objetivo é avaliar
quantitativamente os benefícios de uma API **GraphQL** em comparação a uma API
**REST**, respondendo às duas perguntas de pesquisa:

- **RQ1.** Respostas às consultas GraphQL são mais rápidas que respostas às
  consultas REST?
- **RQ2.** Respostas às consultas GraphQL têm tamanho menor que respostas às
  consultas REST?

Como sistema-alvo usamos a **API pública do GitHub**, que oferece *as duas*
abordagens sobre o mesmo backend de dados:

- REST: `https://api.github.com/repos/{owner}/{repo}`
- GraphQL: `https://api.github.com/graphql`

Isso permite uma comparação justa: as duas APIs consultam **a mesma base** e
retornam **a mesma informação lógica** sobre um repositório (nome, dono,
estrelas, forks, watchers, issues abertas, linguagem, datas, licença, etc.).

---

## 1. Desenho do Experimento

### A. Hipóteses

Para cada pergunta de pesquisa definimos uma hipótese nula (H0) e uma
alternativa (H1). Os testes são **bicaudais** na verificação de diferença e a
direção (GraphQL menor/mais rápido) é avaliada pelo sinal das diferenças.

**RQ1 — Tempo de resposta**

- **H0₁:** Não há diferença no tempo de resposta entre GraphQL e REST
  (`mediana(tempo_GraphQL) = mediana(tempo_REST)`).
- **H1₁:** Há diferença no tempo de resposta entre GraphQL e REST
  (`mediana(tempo_GraphQL) ≠ mediana(tempo_REST)`).

**RQ2 — Tamanho da resposta**

- **H0₂:** Não há diferença no tamanho da resposta entre GraphQL e REST
  (`mediana(tamanho_GraphQL) = mediana(tamanho_REST)`).
- **H1₂:** Há diferença no tamanho da resposta entre GraphQL e REST
  (`mediana(tamanho_GraphQL) ≠ mediana(tamanho_REST)`).

### B. Variáveis Dependentes (medidas)

1. **Tempo de resposta** (`tempo_ms`): latência de ponta a ponta da requisição
   HTTP, em milissegundos (do envio da requisição ao recebimento completo do
   corpo da resposta).
2. **Tamanho da resposta** (`tamanho_bytes`): número de bytes do corpo da
   resposta HTTP (payload), medido sobre o conteúdo recebido.

### C. Variáveis Independentes (fatores)

- **Tipo de API** (`api`): fator principal, com dois níveis — `REST` e
  `GraphQL`. É a variável manipulada pelos tratamentos.

Variáveis de contexto registradas (não manipuladas, usadas para caracterização):
o repositório consultado e o número da repetição.

### D. Tratamentos

Dois tratamentos, aplicados ao **mesmo objeto experimental** (cada repositório):

- **T1 — REST:** uma requisição `GET /repos/{owner}/{repo}`, que retorna o
  objeto completo do repositório.
- **T2 — GraphQL:** uma requisição `POST /graphql` com uma *query* que solicita
  **exatamente os mesmos campos** consumidos da resposta REST — nem mais, nem
  menos.

A equivalência dos campos garante que comparamos a mesma necessidade de
informação sob as duas abordagens.

### E. Objetos Experimentais

Amostra de **repositórios públicos populares do GitHub** (ordenados por número
de estrelas), coletados via API GraphQL de busca. Tamanho-alvo padrão:
**100 repositórios** distintos. Cada repositório é submetido aos dois
tratamentos, caracterizando um desenho pareado.

### F. Tipo de Projeto Experimental

**Projeto pareado / em blocos (paired / within-subject design):** cada
repositório (bloco) recebe os dois tratamentos. Isso controla a variabilidade
entre objetos (tamanho/popularidade do repositório), pois cada par REST×GraphQL
refere-se ao mesmo repositório. A ordem de aplicação dos tratamentos é
**alternada/intercalada** por repetição para mitigar efeitos de aquecimento de
cache e variações temporais de rede.

### G. Quantidade de Medições

- **100 repositórios** × **2 tratamentos** × **5 repetições** = **1.000
  requisições medidas**.
- Para cada par (repositório, API) usamos a **mediana das 5 repetições** como
  valor representativo, reduzindo o ruído de rede. Os testes estatísticos são
  aplicados sobre esses 100 pares pareados.
- Uma requisição de **aquecimento** (warm-up) é descartada antes das repetições
  medidas, e há uma pequena pausa entre requisições para não saturar a rede nem
  o rate limit.

### H. Ameaças à Validade

**Validade interna**
- *Variação de rede e cache:* mitigada por repetições, uso da mediana,
  intercalação da ordem dos tratamentos e warm-up.
- *Rate limiting / throttling do GitHub:* mitigado por autenticação via token
  (5.000 req/h) e pausas entre requisições.
- *Carga do servidor variável ao longo do tempo:* mitigada pela execução
  pareada e intercalada (REST e GraphQL medidos próximos no tempo).

**Validade externa**
- *Generalização:* a amostra são repositórios muito populares; resultados podem
  não se generalizar para outras APIs/domínios. O experimento é específico do
  GitHub.
- *Uma única necessidade de informação:* avaliamos a leitura de metadados de um
  repositório; outras consultas (listas, agregações, escrita) podem se comportar
  de forma diferente.

**Validade de construção**
- *Definição de "tamanho":* usamos o tamanho do payload do corpo da resposta
  (bytes), sem cabeçalhos HTTP nem compressão imposta artificialmente.
- *Definição de "tempo":* latência ponta a ponta do cliente, que inclui rede;
  é a métrica percebida pelo consumidor da API.

**Validade de conclusão**
- *Distribuição não-normal das latências:* por isso usamos o teste
  não-paramétrico de **Wilcoxon (pareado)** em vez do teste t pareado.
- *Tamanho de amostra:* 100 pares oferecem poder estatístico razoável; o
  *effect size* (Cliff's delta / diferença mediana) é reportado para
  contextualizar a significância prática.

---

## 2. Preparação do Experimento

O cenário experimental é implementado pelos scripts em `scripts/`:

| Script | Função |
|--------|--------|
| `coletar_repos.py` | Coleta a lista de objetos experimentais (repositórios populares) via GraphQL e salva em `data/repositorios.json`. |
| `benchmark.py` | Aplica os dois tratamentos a cada repositório, com warm-up e repetições, medindo tempo e tamanho. Gera `data/medicoes.csv`. |
| `analise.py` | Valida os dados, calcula estatísticas descritivas e os testes de hipótese (Wilcoxon pareado), gera figuras e tabelas de resumo. |
| `dashboard.py` | Gera o dashboard HTML com tabelas e gráficos comparativos (Sprint Lab05S03). |

Consulte o `README.md` para instruções de execução.

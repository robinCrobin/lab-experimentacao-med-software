# Laboratório 05 — GraphQL vs REST: Um Experimento Controlado

João Guilherme Falante Araújo  
Roberta Sophia Carvalho Silva  
Mauricio Fernandes Leite  

Laboratório de Experimentação de Software — PUC Minas

---

## Sumário

1. Introdução

1.1 Conceitos e termos-chave

2. Metodologia e descrição da base

2.1 Origem dos dados

2.2 Recorte experimental (seleção dos repositórios)

2.3 Particionamento (subgrupos)

2.4 Medidas de tendência central e testes

2.5 Construção do dashboard

3. Página 0 — Caracterização do dataset

4. Resultados

4.1 RQ1 — Tempo de resposta: GraphQL é mais rápido que REST?

4.2 RQ2 — Tamanho da resposta: GraphQL retorna payload menor que REST?

5. Discussão dos resultados

5.1 Observações principais

5.2 Ameaças à validade

6. Mapeamento dashboard ↔ dados (reprodutibilidade)

7. Referências

---

## 1. Introdução

GraphQL e REST são duas abordagens amplamente utilizadas para construção e consumo de APIs Web. Em APIs REST, o cliente acessa recursos por meio de endpoints específicos, que normalmente retornam uma representação pré-definida do recurso solicitado. Já em GraphQL, o cliente envia uma consulta declarando exatamente quais campos deseja receber, permitindo maior controle sobre o formato e o volume da resposta.

Apesar de GraphQL ser frequentemente apresentado como uma alternativa mais flexível e eficiente que REST, seus benefícios práticos dependem do cenário de uso. Em consultas simples, uma API REST bem otimizada pode apresentar menor latência; em consultas com muitos relacionamentos ou campos desnecessários, GraphQL pode reduzir o volume de dados trafegados e evitar múltiplas requisições.

Este laboratório realiza um experimento controlado comparando REST e GraphQL a partir da API pública do GitHub, que disponibiliza as duas abordagens sobre uma mesma base de dados. O objetivo é avaliar quantitativamente duas dimensões relevantes para consumidores de APIs: tempo de resposta e tamanho do payload retornado.

As perguntas de pesquisa são:

- RQ1: Respostas GraphQL são mais rápidas que respostas REST?
- RQ2: Respostas GraphQL têm tamanho menor que respostas REST?

Para cada pergunta, foram formuladas hipóteses estatísticas:

RQ1 — Tempo de resposta:

- H0₁: não há diferença entre as medianas de tempo de resposta de GraphQL e REST.
- H1₁: há diferença entre as medianas de tempo de resposta de GraphQL e REST.

RQ2 — Tamanho da resposta:

- H0₂: não há diferença entre as medianas de tamanho da resposta de GraphQL e REST.
- H1₂: há diferença entre as medianas de tamanho da resposta de GraphQL e REST.

Os testes foram conduzidos de forma bicaudal, verificando se existe diferença estatisticamente significativa entre as abordagens. A direção do efeito foi interpretada a partir das medianas observadas.

## 1.1 Conceitos e termos-chave

API REST: estilo arquitetural no qual recursos são acessados por URLs e operações HTTP, como GET, POST, PUT e DELETE. No experimento, a API REST do GitHub foi consultada pelo endpoint `GET /repos/{owner}/{repo}`.

GraphQL: linguagem de consulta para APIs em que o cliente especifica os campos desejados. No experimento, a API GraphQL do GitHub foi consultada por meio de uma query sobre o objeto `repository(owner, name)`.

Payload: corpo da resposta HTTP retornado pela API. Neste experimento, o tamanho do payload foi medido em bytes.

Tempo de resposta: latência ponta a ponta da requisição HTTP, medida em milissegundos, desde o envio da requisição até o recebimento completo da resposta.

Over-fetching: situação em que a API retorna mais dados do que o cliente realmente precisa. Esse fenômeno é comum em endpoints REST que retornam objetos completos.

Experimento pareado: desenho experimental em que o mesmo objeto recebe todos os tratamentos. Neste caso, cada repositório foi consultado tanto via REST quanto via GraphQL.

Teste de Wilcoxon pareado: teste estatístico não-paramétrico usado para comparar duas amostras relacionadas quando não se assume normalidade dos dados.

Cliff's delta: medida de tamanho de efeito que indica a magnitude e a direção da diferença entre dois grupos.

## 2. Metodologia e descrição da base

O experimento foi estruturado como um projeto pareado, no qual cada repositório público do GitHub foi submetido aos dois tratamentos: consulta via REST e consulta via GraphQL. Essa escolha reduz a influência de diferenças entre repositórios, pois a comparação é feita sempre dentro do mesmo objeto experimental.

A variável independente do experimento é o tipo de API, com dois níveis:

- REST;
- GraphQL.

As variáveis dependentes são:

- tempo de resposta, em milissegundos;
- tamanho do payload, em bytes.

As duas consultas foram configuradas para representar a mesma necessidade de informação: obter metadados de um repositório, como nome, dono, descrição, número de estrelas, forks, watchers, issues abertas, linguagem principal, datas, tamanho em disco, licença, branch padrão, homepage e tópicos.

No tratamento REST, foi utilizado o endpoint:

`GET https://api.github.com/repos/{owner}/{repo}`

No tratamento GraphQL, foi utilizada a API:

`POST https://api.github.com/graphql`

com uma query solicitando os mesmos campos consumidos da resposta REST.

## 2.1 Origem dos dados

Os dados foram coletados da API pública do GitHub. A lista de objetos experimentais foi formada por repositórios públicos populares, selecionados por número de estrelas.

A coleta dos repositórios foi realizada pelo script `scripts/coletar_repos.py`, que utiliza a API GraphQL de busca do GitHub com o critério:

`stars:>10000 sort:stars-desc`

O resultado dessa etapa foi salvo em `data/repositorios.json`.

Em seguida, o script `scripts/benchmark.py` executou as consultas REST e GraphQL para cada repositório selecionado, registrando tempo de resposta e tamanho do payload em `data/medicoes.csv`.

## 2.2 Recorte experimental (seleção dos repositórios)

O recorte experimental foi composto por 100 repositórios públicos populares do GitHub. A amostra contém repositórios com grande número de estrelas, variando de 107.036 a 518.860 estrelas no momento da coleta.

Os cinco primeiros repositórios da amostra, ordenados por popularidade, foram:

| Repositório | Estrelas |
|---|---:|
| codecrafters-io/build-your-own-x | 518.860 |
| sindresorhus/awesome | 478.239 |
| freeCodeCamp/freeCodeCamp | 450.348 |
| public-apis/public-apis | 443.741 |
| EbookFoundation/free-programming-books | 390.682 |

Cada repositório foi consultado pelas duas APIs, permitindo comparação pareada entre REST e GraphQL.

## 2.3 Particionamento (subgrupos)

O particionamento principal dos dados foi feito pelo tratamento aplicado:

- grupo REST;
- grupo GraphQL.

Como o experimento é pareado, cada repositório aparece nos dois grupos. A unidade final de análise não é uma requisição individual, mas sim a mediana das repetições para cada combinação de repositório e API.

Foram planejadas 1.000 medições válidas:

100 repositórios × 2 APIs × 5 repetições = 1.000 requisições medidas.

Ao final, foram obtidas 999 medições válidas, pois uma requisição isolada falhou e foi descartada. Ainda assim, todos os 100 repositórios permaneceram com dados suficientes para compor os pares de comparação.

Distribuição das medições:

| API | Medições válidas |
|---|---:|
| REST | 499 |
| GraphQL | 500 |
| Total | 999 |

## 2.4 Medidas de tendência central e testes

Para reduzir o impacto de ruído de rede e variações temporais, cada consulta foi repetida cinco vezes por API e por repositório. Antes das repetições medidas, foi executada uma requisição de aquecimento, descartada da análise.

Para cada par repositório/API, utilizou-se a mediana das repetições como valor representativo. A mediana foi escolhida por ser menos sensível a outliers do que a média, especialmente em medições de latência.

Como o desenho experimental é pareado e não se assume normalidade nas latências, foi aplicado o teste não-paramétrico de Wilcoxon pareado, com nível de significância de 5%.

Também foi calculado o Cliff's delta para avaliar o tamanho do efeito observado.

## 2.5 Construção do dashboard

Além dos arquivos de dados e do relatório textual, foi construído um dashboard local em HTML para apoiar a visualização dos resultados.

O dashboard foi gerado pelo script `scripts/dashboard.py`, a partir dos arquivos processados:

- `data/resumo_descritivo.csv`;
- `data/testes_estatisticos.csv`;
- `data/pares.csv`;
- imagens geradas na pasta `figures/`.

O arquivo final está em:

`dashboard/dashboard_lab05.html`

O dashboard apresenta cartões-resumo, tabelas estatísticas, gráficos de distribuição e gráficos pareados, permitindo verificar visualmente as diferenças entre REST e GraphQL.

## 3. Página 0 — Caracterização do dataset

O dataset final do experimento é composto por medições de tempo e tamanho de resposta para 100 repositórios públicos do GitHub, comparando duas APIs distintas sobre a mesma necessidade de informação.

Resumo do dataset:

| Item | Valor |
|---|---:|
| Repositórios analisados | 100 |
| APIs comparadas | 2 |
| Repetições planejadas por API/repositório | 5 |
| Medições planejadas | 1.000 |
| Medições válidas | 999 |
| Pares finais para análise estatística | 100 |

As estatísticas descritivas calculadas sobre a mediana por repositório são:

| API | Tempo médio (ms) | Tempo mediano (ms) | Desvio padrão tempo (ms) | Tamanho médio (bytes) | Tamanho mediano (bytes) | Desvio padrão tamanho (bytes) |
|---|---:|---:|---:|---:|---:|---:|
| REST | 366,99 | 361,02 | 50,58 | 6.287,30 | 6.343,0 | 620,58 |
| GraphQL | 462,78 | 461,81 | 52,21 | 840,31 | 787,5 | 206,82 |

Esses valores mostram uma primeira tendência: REST apresentou menor tempo mediano, enquanto GraphQL apresentou payload muito menor.

## 4. Resultados

Os resultados foram organizados de acordo com as duas perguntas de pesquisa do experimento.

## 4.1 RQ1 — Respostas GraphQL são mais rápidas que respostas REST?

Para a métrica de tempo de resposta, REST apresentou mediana de 361,02 ms, enquanto GraphQL apresentou mediana de 461,81 ms.

| Métrica | Valor |
|---|---:|
| Mediana REST | 361,02 ms |
| Mediana GraphQL | 461,81 ms |
| Diferença GraphQL − REST | +100,79 ms |
| Variação da mediana GraphQL vs REST | +27,9% |
| Estatística de Wilcoxon | 54,0 |
| p-valor | 1,961 × 10⁻¹⁷ |
| Significativo a 5%? | Sim |
| Cliff's delta | 0,802 |
| Magnitude do efeito | Grande |

O p-valor é menor que 0,05, portanto rejeita-se H0₁. Há diferença estatisticamente significativa entre os tempos de resposta das duas APIs.

No entanto, a direção da diferença mostra que GraphQL não foi mais rápido. Pelo contrário, GraphQL foi aproximadamente 27,9% mais lento que REST na mediana. Em 93 dos 100 pares analisados, a mediana de tempo de GraphQL foi maior que a mediana de tempo de REST.

Assim, para esta consulta específica, a hipótese prática de que GraphQL teria menor tempo de resposta não foi confirmada.

## 4.2 RQ2 — Respostas GraphQL têm tamanho menor que respostas REST?

Para a métrica de tamanho da resposta, REST apresentou mediana de 6.343,0 bytes, enquanto GraphQL apresentou mediana de 787,5 bytes.

| Métrica | Valor |
|---|---:|
| Mediana REST | 6.343,0 bytes |
| Mediana GraphQL | 787,5 bytes |
| Diferença GraphQL − REST | −5.555,5 bytes |
| Redução da mediana GraphQL vs REST | 87,6% |
| Estatística de Wilcoxon | 0,0 |
| p-valor | 3,896 × 10⁻¹⁸ |
| Significativo a 5%? | Sim |
| Cliff's delta | −1,000 |
| Magnitude do efeito | Grande/máxima |

O p-valor é menor que 0,05, portanto rejeita-se H0₂. Há diferença estatisticamente significativa entre os tamanhos das respostas das duas APIs.

Neste caso, a direção do efeito confirma a expectativa: GraphQL produziu respostas muito menores que REST. A redução mediana foi de 87,6%, e em todos os 100 pares analisados o payload GraphQL foi menor que o payload REST.

O Cliff's delta igual a −1,000 indica efeito máximo em favor de GraphQL para a redução do tamanho da resposta.

## 5. Discussão dos resultados

Os resultados mostram que os benefícios de GraphQL não são universais. A abordagem apresentou ganho expressivo em tamanho de resposta, mas não apresentou ganho de tempo no cenário analisado.

Para RQ1, GraphQL foi mais lento que REST. Uma explicação provável é que a consulta analisada envolve a leitura de um único recurso: os metadados de um repositório. Nesse cenário, o endpoint REST do GitHub é direto, altamente otimizado e possivelmente favorecido por mecanismos de cache. Já GraphQL exige o processamento da query, resolução dos campos solicitados e montagem dinâmica da resposta.

Além disso, o principal ponto forte de GraphQL aparece com mais clareza em cenários com dados aninhados ou quando REST exigiria múltiplas requisições. Como este experimento usou uma necessidade de informação que cabia em uma única chamada REST, GraphQL não conseguiu compensar seu custo adicional de processamento.

Para RQ2, GraphQL confirmou fortemente sua vantagem. Como o cliente especifica exatamente os campos desejados, a resposta contém apenas os dados necessários. Já o endpoint REST retorna um objeto completo do repositório, incluindo diversos campos, links e metadados adicionais que não eram necessários para a comparação.

Portanto, a principal evidência do experimento é que GraphQL reduz drasticamente o volume de dados trafegados, mas pode apresentar maior latência em consultas simples a um único recurso.

## 5.1 Observações principais

- REST foi mais rápido na consulta avaliada.
- GraphQL foi aproximadamente 27,9% mais lento em termos de tempo mediano.
- GraphQL foi muito mais eficiente em tamanho de resposta.
- A redução mediana do payload com GraphQL foi de 87,6%.
- Em todos os 100 pares, GraphQL retornou payload menor que REST.
- Em 93 dos 100 pares, GraphQL teve tempo de resposta maior que REST.
- A escolha entre REST e GraphQL deve considerar o padrão de acesso da aplicação, e não apenas a tecnologia em si.

## 5.2 Ameaças à validade

Validade interna: medições de tempo em APIs públicas sofrem influência de rede, carga do servidor, cache e variações temporais. Para mitigar esses fatores, foram usadas repetições, mediana, requisição de aquecimento e intercalação da ordem dos tratamentos.

Validade externa: o experimento foi realizado apenas com a API do GitHub e com repositórios populares. Os resultados podem não se generalizar para outras APIs, outros domínios ou sistemas privados.

Validade de construção: o tamanho considerado foi apenas o corpo da resposta HTTP, sem contabilizar cabeçalhos. O tempo medido corresponde à latência percebida pelo cliente, incluindo rede, e não apenas ao tempo interno de processamento do servidor.

Validade de conclusão: foi utilizado teste de Wilcoxon pareado, adequado ao desenho experimental e à natureza das medições. Ainda assim, os resultados representam o cenário específico analisado: leitura de metadados de um único repositório.

## 6. Mapeamento dashboard ↔ dados (reprodutibilidade)

A reprodutibilidade do experimento é apoiada pelos scripts, dados intermediários e artefatos finais presentes na pasta do laboratório.

| Artefato | Função |
|---|---|
| `scripts/coletar_repos.py` | Coleta os repositórios públicos populares do GitHub e gera `data/repositorios.json`. |
| `scripts/benchmark.py` | Executa as consultas REST e GraphQL, medindo tempo e tamanho, e gera `data/medicoes.csv`. |
| `scripts/analise.py` | Calcula estatísticas descritivas, testes estatísticos e figuras. |
| `scripts/dashboard.py` | Gera o dashboard final em HTML. |
| `data/repositorios.json` | Lista de repositórios analisados. |
| `data/medicoes.csv` | Medições brutas válidas. |
| `data/pares.csv` | Medianas pareadas por repositório e API. |
| `data/resumo_descritivo.csv` | Estatísticas descritivas por API. |
| `data/testes_estatisticos.csv` | Resultados dos testes de hipótese. |
| `figures/` | Gráficos usados no relatório e no dashboard. |
| `dashboard/dashboard_lab05.html` | Dashboard visual do experimento. |

Pipeline de execução:

1. Coletar repositórios:

`python scripts/coletar_repos.py --n 100`

2. Executar benchmark:

`python scripts/benchmark.py --rep 5`

3. Analisar resultados:

`python scripts/analise.py`

4. Gerar dashboard:

`python scripts/dashboard.py`

## 7. Referências

FIELDING, Roy Thomas. Architectural Styles and the Design of Network-based Software Architectures. Tese de doutorado, University of California, Irvine, 2000.

GITHUB. REST API documentation. Disponível em: https://docs.github.com/en/rest

GITHUB. GraphQL API documentation. Disponível em: https://docs.github.com/en/graphql

GRAPHQL FOUNDATION. GraphQL Specification. Disponível em: https://spec.graphql.org/

WILCOXON, Frank. Individual comparisons by ranking methods. Biometrics Bulletin, 1945.

CLIFF, Norman. Dominance statistics: Ordinal analyses to answer ordinal questions. Psychological Bulletin, 1993.

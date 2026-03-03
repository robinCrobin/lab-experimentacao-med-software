
# Laboratório de Medição e Experimentação de Software

Este repositório reúne os desenvolvimentos realizados na disciplina de **Laboratório de Medição e Experimentação de Software** do curso de Engenharia de Software.
DISCIPLINA:
LABORATÓRIO DE
EXPERIMENTAÇÃO DE SOFTWARE

## Informações do Projeto

**Professor:** Danilo de Quadros Maia Filho

**Alunos participantes:**
- João Guilherme Falante Araújo
- Mauricio Fernandes Leite
- Roberta Sophia Carvalho Silva

## Objetivo

Estudar, por meio de experimentação prática, as principais características de sistemas populares open-source, utilizando métodos de coleta, análise e discussão de métricas extraídas de repositórios do GitHub. As atividades são organizadas em laboratórios sequenciais, cada um com entregas e objetivos específicos.



## Descrição dos Laboratórios

### Lab01S01 – Coleta inicial de repositórios populares
**Objetivo:** Coletar dados dos repositórios populares do GitHub utilizando consulta GraphQL e exportar para JSON.

**Execução:** Script automatizado (`fetch_repos.py`) coleta e salva os dados em `data/repositorios.json`.

**Documentação:** Detalhes do funcionamento do script em `docs/FUNCIONALIDADES-fetch_repos.md`.

---

### Lab01S02 – Paginação e análise de 1000 repositórios
**Objetivo:** Coletar dados dos 1.000 repositórios com mais estrelas no GitHub, exportar para CSV e preparar a primeira versão do relatório com hipóteses informais.

**Execução:** Script `fetch_repos_1000.py` coleta e exporta os dados para `data/repositorios_1000.csv`. Relatório inicial em `data/RelatorioAnaliseInicialRepos.md`.

---

### Lab01S03 – Análise e visualização dos dados
**Objetivo:** Analisar e visualizar os dados coletados dos 1.000 repositórios, elaborando o relatório final.

**Execução:** Utilização dos dados CSV para análise estatística e geração de gráficos, com discussão dos resultados e hipóteses.

---

### Lab 02 – Estudo das características de qualidade de sistemas Java
**Objetivo:** Analisar características de qualidade em projetos Java, utilizando métricas e conceitos estudados em artigos e fichamentos.

**Conteúdo:** Planejamento, código de análise de métricas, dados e relatórios.

**Material de apoio:** Fichamentos sobre métricas CK, design flaws, code smells, DPy, etc.

---

### Lab 03 – Caracterizando a atividade de code review no GitHub
**Objetivo:** Estudar e caracterizar a atividade de code review em projetos do GitHub, utilizando dados de pull requests e revisões.

**Conteúdo:** Planejamento, scripts de coleta, dados e relatórios.

**Material de apoio:** Fichamentos sobre GitHub API, estudos de caso e evidências empíricas.

---

### Lab 04 – Visualização de dados utilizando BI
**Objetivo:** Visualizar dados dos laboratórios anteriores utilizando uma ferramenta de Business Intelligence (BI).

**Conteúdo:** Planejamento, dashboards/relatórios, datasets e documentação.

**Material de apoio:** Dados e visualizações dos labs anteriores.

---

### Lab 05 – GraphQL vs REST: Um experimento controlado
**Objetivo:** Realizar um experimento controlado comparando as abordagens GraphQL e REST para consumo de dados.

**Conteúdo:** Planejamento do experimento, protocolo, scripts (GraphQL e REST), dados coletados e relatório comparativo.

**Material de apoio:** Scripts e queries do Lab 01 como base para comparação.

---

## Questões de Pesquisa

Questões de Pesquisa:
```
```
RQ 01. Sistemas populares são maduros/antigos?
Métrica: idade do repositório (calculado a partir da data de sua criação)
```
```
RQ 02. Sistemas populares recebem muita contribuição externa?
Métrica: total de pull requests aceitas
```
```
RQ 03. Sistemas populares lançam releases com frequência?
Métrica: total de releases
```
```
RQ 04. Sistemas populares são atualizados com frequência?
Métrica: tempo até a última atualização (calculado a partir da data de última
atualização)
```
```
RQ 05. Sistemas populares são escritos nas linguagens mais populares?
Métrica: linguagem primária de cada um desses repositórios
```
```
RQ 06. Sistemas populares possuem um alto percentual de issues fechadas?
Métrica: razão entre número de issues fechadas pelo total de issues
```

---




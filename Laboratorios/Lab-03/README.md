# Lab 03 – Caracterizando a atividade de code review no GitHub

**Sprint 3** da disciplina Laboratório de Experimentação de Software.

## Enunciado

O enunciado oficial está no repositório da disciplina:

- [LABORATÓRIO 03 - Caracterizando a atividade de code review no github.pdf](https://github.com/joaopauloaramuni/laboratorio-de-experimentacao-de-software/blob/main/LABORATORIOS/LABORAT%C3%93RIO%2003%20-%20Caracterizando%20a%20atividade%20de%20code%20review%20no%20github.pdf)

## Conteúdo desta pasta

Aqui serão colocados o planejamento, scripts de coleta (ex.: API do GitHub para PRs e reviews), dados e relatórios do Lab 03.

## Material de apoio

Os fichamentos em `Artigos/Fichamentos/` (GitHub API, estudos de caso, evidência empírica) e o uso da API no Lab 01 podem apoiar este laboratório.

## Lab03S01 — Sprint 1

### 1. Coleta dos repositórios (`coleta_repositorios.py`)

Seleciona os 200 repositórios mais populares do GitHub que possuem no mínimo
100 PRs (MERGED + CLOSED). A saída são dois arquivos em `data/`:

- `repositorios.json` — payload bruto da API GraphQL.
- `repositorios.csv` — versão tabular com `nameWithOwner`, `stars`,
  `primary_language`, `mergedPRsCount`, `closedPRsCount` e `totalPRs`.

**Pré-requisitos**

```bash
pip install -r requirements.txt
export GITHUB_TOKEN=seu_token_aqui   # ou em um arquivo .env
```

**Como rodar**

```bash
# coleta via API
python coleta_repositorios.py --fetch

# regenera o CSV a partir do JSON já salvo
python coleta_repositorios.py --analyze
```

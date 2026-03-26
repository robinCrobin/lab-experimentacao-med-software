# Lab 02 — Extração (estado atual)

Este documento descreve **o que foi implementado até agora** no Lab-02 e **como executar** a extração.

## O que temos até agora

Nesta etapa, foi implementada **apenas a extração** dos **Top-1.000 repositórios Java mais populares do GitHub**, sendo popularidade definida por **número de estrelas**.

- Script: `main.py`
- API: GitHub GraphQL (`https://api.github.com/graphql`)
- Query: `language:Java sort:stars-desc`
- Paginação: via `endCursor`/`hasNextPage`

## Pré-requisitos

- Python 3
- Dependências Python:
  - `requests`
  - `python-dotenv`

## Configurar o token (`GITHUB_TOKEN`)

O script autentica na API do GitHub usando a variável `GITHUB_TOKEN`.

Você pode configurar de duas formas:

### Opção A) Variável de ambiente (recomendado)

No macOS/zsh:

- `export GITHUB_TOKEN=SEU_TOKEN_AQUI`

### Opção B) Arquivo `.env`

Crie/edite um arquivo `.env` na pasta `Laboratorios/Lab-02/` com:

- `GITHUB_TOKEN=SEU_TOKEN_AQUI`

Dica: evite commitar o `.env` (token é segredo).

## Como rodar a extração

1) Abra um terminal e vá para a pasta do Lab-02:

- `cd experimentacao-med-software/Laboratorios/Lab-02`

2) Execute a extração:

- `python3 main.py --extract`

Durante a execução, o script imprime progresso do tipo "Coletados até agora: N".

## Saídas geradas

Os arquivos serão criados dentro de `Laboratorios/Lab-02/data/`:

- `top_java_repos.csv` (**principal**)
  - colunas: `nameWithOwner`, `url`, `stargazerCount`
- `top_java_repos.json` (**apoio/debug**)
  - lista completa (JSON) com os mesmos campos retornados pela query

## Problemas comuns

### Erro HTTP 401 (Bad credentials)

- Token inválido/revogado/expirado, ou variável não está sendo lida corretamente.
- Verifique se `GITHUB_TOKEN` está definido e se você copiou o token completo.
- Evite aspas no `.env` (use `GITHUB_TOKEN=...`).

### Rate limit / erros temporários

O script tenta novamente em erros temporários (ex.: 502/503/504).
Se persistir, aguarde e tente novamente.


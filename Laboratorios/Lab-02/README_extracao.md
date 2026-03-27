# Lab 02 — Extração e Coleta de Métricas (estado atual)

Este documento descreve **o que foi implementado até agora** no Lab-02 e **como executar**:

- a extração dos Top-1.000 repositórios Java; e
- o script de **automação de clone e coleta de métricas com CK** (Lab02S01).

## O que temos até agora

1. Extração dos **Top-1.000 repositórios Java mais populares do GitHub**, sendo popularidade definida por **número de estrelas**.

- Script: `main.py`
- API: GitHub GraphQL (`https://api.github.com/graphql`)
- Query: `language:Java sort:stars-desc`
- Paginação: via `endCursor`/`hasNextPage`

2. **Script de automação de clone e coleta de métricas (CK)**:

- Clonagem automática de repositórios listados em `data/top_java_repos.csv`.
- Execução da ferramenta **CK** em um repositório específico, gerando arquivos `.csv` de métricas.
- Atende ao requisito da Lab02S01 de **"Script de Automação de clone e Coleta de Métricas + Arquivo .csv com o resultado das medições de 1 repositório"**.

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

Adicionalmente, o script de clone/métricas usa:

- `data/repos/` — repositórios clonados.
- `data/ck_results/` — resultados da ferramenta CK.

## Script de Automação de Clone e Coleta de Métricas (CK)

### 1) Preparar a ferramenta CK

1. Instale o **Java 8+** na sua máquina.
2. Baixe o JAR da ferramenta CK no repositório oficial:
   - <https://github.com/mauricioaniche/ck>
3. Gere ou baixe o JAR "com dependências" (por exemplo `ck-x.x.x-SNAPSHOT-jar-with-dependencies.jar`).
4. Copie esse arquivo para a pasta `Laboratorios/Lab-02/` e **renomeie para** `ck.jar`.

> O script assume que o arquivo está em `Laboratorios/Lab-02/ck.jar`.

### 2) Clonar repositórios (opcional para Lab02S01)

Para clonar alguns repositórios da lista (por exemplo, os 10 primeiros):

- `python3 main.py --clone --limit 10`

Os repositórios serão clonados em `Laboratorios/Lab-02/data/repos/`, em subpastas com o padrão `owner__repo`.

> Observação: para clonar **todos os 1.000** repositórios, use `--limit 1000` (vai demorar e ocupar bastante espaço).

### 3) Gerar métricas CK para **1 repositório** (Lab02S01)

Para atender ao requisito de **"Arquivo .csv com o resultado das medições de 1 repositório"**:

1. Garanta que você já tenha o `top_java_repos.csv` (rodou `--extract`).
2. Garanta que o `ck.jar` esteja na pasta do Lab-02 (como descrito acima).
3. No terminal, rode, por exemplo:

- `python3 main.py --measure-one 1`

Isso fará:

- Ler o repositório na **posição 1** do `top_java_repos.csv` (mais popular).
- Clonar o repositório em `data/repos/owner__repo/` (se ainda não estiver clonado).
- Executar a ferramenta **CK** nesse repositório.
- Gerar os arquivos de métricas (por exemplo, `class.csv`, `method.csv`, `variable.csv`) em:

  - `Laboratorios/Lab-02/data/ck_results/owner__repo/`

Você pode usar, por exemplo, o arquivo `class.csv` gerado pelo CK como **o arquivo de resultado das medições de 1 repositório** para entregar na Lab02S01.

## Problemas comuns

### Erro HTTP 401 (Bad credentials)

- Token inválido/revogado/expirado, ou variável não está sendo lida corretamente.
- Verifique se `GITHUB_TOKEN` está definido e se você copiou o token completo.
- Evite aspas no `.env` (use `GITHUB_TOKEN=...`).

### Rate limit / erros temporários

O script tenta novamente em erros temporários (ex.: 502/503/504).
Se persistir, aguarde e tente novamente.


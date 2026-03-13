# Lab-01 – Coleta e análise de repositórios populares do GitHub

## Objetivo

Coletar dados de repositórios populares do GitHub utilizando a API GraphQL, salvar os dados em JSON e, a partir desse arquivo, produzir um CSV processado com métricas derivadas para análise.

## Estrutura desta pasta

| Item | Descrição |
|------|-----------|
| `README.md` | Este arquivo |
| `fetch_repos.py` | Script principal de coleta **e** análise |
| `requirements.txt` | Dependências do projeto |
| `.env.example` | Exemplo de configuração de variáveis de ambiente (token GitHub) |
| `data/` | Subpasta para dados coletados e processados |
| `data/repositorios.json` | Dados brutos coletados via GraphQL (gerado com `--fetch`) |
| `data/repositorios_processados.csv` | Dados processados com métricas derivadas (gerado com `--analyze`) |

## O que o `fetch_repos.py` faz

O script `fetch_repos.py` possui **duas funcionalidades principais**, controladas por flags de linha de comando:

1. **Coleta de dados (`--fetch`)**
   - Usa a API GraphQL do GitHub (`https://api.github.com/graphql`).
   - Consulta repositórios ordenados por número de estrelas (`stars:>10000 sort:stars-desc`).
   - Faz paginação em lotes de `PAGE_SIZE` (padrão: 10), até coletar até `TARGET_REPOS` repositórios (padrão: 1000).
   - Para cada repositório, coleta informações como:
     - `name`, `nameWithOwner`, `url`;
     - `stargazerCount` (número de estrelas);
     - `createdAt` (data de criação);
     - `pushedAt` (data da última atualização);
     - linguagem principal (`primaryLanguage.name`);
     - total de *pull requests* mesclados (`pullRequests.totalCount`);
     - total de *releases* (`releases.totalCount`);
     - total de *issues* (`issues.totalCount`);
     - total de *issues* fechadas (`closedIssues.totalCount`).
   - Implementa *retry* para erros temporários (códigos HTTP 502, 503, 504 e falhas de conexão).
   - Salva os dados em `data/repositorios.json`.

2. **Análise e processamento (`--analyze`)**
   - Lê o arquivo `data/repositorios.json` gerado pela fase de coleta.
   - Normaliza os dados em um `DataFrame` (usando `pandas`).
   - Seleciona e renomeia colunas para nomes em inglês, por exemplo:
     - `primary_language`, `pull_requests_total`, `releases_total`,
       `issues_total`, `closed_issues_total`.
   - Converte campos de data para tipo datetime.
   - Calcula métricas derivadas:
     - `repo_age_days`: idade do repositório em dias (a partir de `createdAt`);
     - `days_since_last_update`: dias desde a última atualização (`pushedAt`);
     - `closed_issues_ratio`: razão entre issues fechadas e total de issues.
   - Remove campos de data originais, mantendo apenas as colunas derivadas e demais atributos relevantes.
   - Salva o resultado em `data/repositorios_processados.csv`.
   - Exibe um resumo das primeiras linhas no terminal.

## Como gerar os dados para análise das RQs

Os dados utilizados para responder às RQs (resumo das métricas, distribuição de linguagens e métricas por linguagem) são gerados pelo script `answer_rqs.py`.

### Passos para execução
1. Abra um terminal na pasta raiz do repositório (onde está a pasta `Laboratorios/`).
2. Vá até a pasta do laboratório 01:
   ```bash
   cd Laboratorios/Lab-01
   ```
3. Execute o script que calcula as métricas:
   ```bash
   python answer_rqs.py
   ```

### Arquivos gerados
Após a execução, serão criados/atualizados os seguintes arquivos na pasta `Laboratorios/Lab-01/data/`:
- `resumo.csv`: métricas agregadas para RQ01, RQ02, RQ03, RQ04 e RQ06.
- `distribuicao_linguagem.csv`: distribuição das linguagens (RQ05).
- `metricas_por_linguagem.csv`: métricas de RQ02, RQ03 e RQ04 agrupadas por linguagem (RQ07).

## Pré-requisitos

- Python 3 instalado.
- Dependências do projeto instaladas (ver `requirements.txt`).
- Um token de acesso do GitHub (Personal Access Token) com permissão para acessar a API GraphQL, configurado na variável de ambiente `GITHUB_TOKEN` (ou via `.env`, conforme `.env.example`).

## Como executar

### 1. Instalar dependências

Na pasta `Laboratorios/Lab-01/`:

```zsh
pip install -r requirements.txt
```

### 2. Configurar o token do GitHub

Crie um arquivo `.env` baseado em `.env.example` ou exporte a variável de ambiente diretamente no shell:

```zsh
export GITHUB_TOKEN="seu_token_aqui"
```

### 3. Coletar os dados (fase de fetch)

```zsh
python fetch_repos.py --fetch
```

Ao final, o arquivo `data/repositorios.json` será criado/atualizado com até `TARGET_REPOS` repositórios.

### 4. Analisar e gerar CSV processado (fase de analyze)

```zsh
python fetch_repos.py --analyze
```

Se o `data/repositorios.json` existir, o script irá:
- carregar os dados,
- calcular as métricas derivadas,
- salvar o resultado em `data/repositorios_processados.csv`,
- e mostrar um *preview* das primeiras linhas no terminal.

## Observações

- As duas fases são independentes: você pode coletar uma vez (`--fetch`) e rodar várias análises depois (`--analyze`) reutilizando o mesmo JSON.
- Os nomes das colunas derivadas na saída CSV são mantidos em inglês para facilitar análises e integração com outras ferramentas.

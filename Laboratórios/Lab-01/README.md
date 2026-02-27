**Sprint 1** da disciplina Laboratório de Experimentação de Software.

## O que o código faz (`fetch_repos.py`)

O script `fetch_repos.py` acessa a API GraphQL do GitHub para:
- Buscar os repositórios públicos com mais estrelas (consulta `stars:>10000 sort:stars-desc`).
- Paginar os resultados até coletar **100 repositórios**.
- Para cada repositório, salva informações como:
  - `name` e `nameWithOwner`
  - `url`
  - `stargazerCount` (número de estrelas)
  - `createdAt` e `pushedAt`
  - linguagem principal (`primaryLanguage.name`)
  - quantidade de *pull requests* mesclados (`pullRequests.totalCount`)
  - quantidade de *releases* (`releases.totalCount`)
  - quantidade total de *issues* abertas e fechadas (`issues.totalCount` e `closedIssues.totalCount`)
- Salva os dados coletados no arquivo `data/repositorios.json` (máx. 100 repositórios).
- Faz uma validação simples, garantindo que o arquivo tenha 100 repositórios com campos essenciais.

## Pré‑requisitos

- Python 3 instalado.
- Dependências listadas em `requirements.txt` instaladas.
- Um token de acesso do GitHub (Personal Access Token) com permissão para acessar a API GraphQL.

## Como configurar o ambiente

1. Criar (opcional) e ativar um ambiente virtual Python.
2. Instalar as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Definir a variável de ambiente `GITHUB_TOKEN` com o seu token do GitHub. Exemplo no macOS / Linux (zsh):
   ```bash
   export GITHUB_TOKEN="seu_token_aqui"
   ```

## Como executar o script

Dentro da pasta `Lab-01/`, execute:

```bash
python fetch_repos.py
```

Se tudo der certo, ao final você verá mensagens indicando:
- Quantos repositórios foram coletados.
- Onde o arquivo JSON foi salvo (por padrão: `data/repositorios.json`).
- Resultado da validação simples do arquivo gerado.
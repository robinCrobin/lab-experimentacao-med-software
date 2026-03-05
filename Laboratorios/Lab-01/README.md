# Lab01S01 – Coleta inicial de repositórios populares

## Objetivo

Coletar dados dos repositórios populares do GitHub utilizando consulta GraphQL e exportar para JSON.

## Estrutura desta pasta

| Item | Descrição |
|------|-----------|
| `README.md` | Este arquivo |
| `fetch_repos.py` | Script de coleta automática (exporta JSON) |
| `requirements.txt` | Dependências do projeto |
| `.env.example` | Exemplo de configuração de variáveis de ambiente |
| `data/` | Subpasta para dados coletados |
| `data/repositorios.json` | Dados coletados (gerado pelo script) |

## Execução

1. Instale as dependências:
	```powershell
	pip install -r requirements.txt
	```
2. Configure o arquivo `.env` com seu token do GitHub (baseado em `.env.example`).
3. Execute o script de coleta:
	```powershell
	python fetch_repos.py
	```
	Os dados serão salvos em `data/repositorios.json`.

## Observações
- O script utiliza consulta GraphQL para obter dados dos repositórios.

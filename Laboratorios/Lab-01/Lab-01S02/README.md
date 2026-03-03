
# Lab01S02 – Paginação (consulta 1000 repositórios) + dados em arquivo .csv + primeira versão do relatório

## Objetivo

Coletar dados dos 1.000 repositórios com maior número de estrelas no GitHub, exportar para CSV e preparar a primeira versão do relatório com hipóteses informais.

## Estrutura desta pasta

| Item | Descrição |
|------|-----------|
| `README.md` | Este arquivo |
| `fetch_repos_1000.py` | Script de coleta automática (1000 repositórios, exporta CSV) |
| `data/` | Subpasta para dados e relatórios |
| `data/repositorios_1000.csv` | Dados coletados (gerado pelo script) |
| `data/RelatorioAnaliseInicialRepos.md` | Relatório inicial de análise |

## Execução (Lab01S02)

1. Acesse a pasta da etapa:
   ```powershell
   cd lab-experimentacao-med-software\Laboratorios\Lab-01\Lab-01S02
   ```
2. Execute o script de coleta:
   ```powershell
   python fetch_repos_1000.py
   ```
   Os dados serão salvos em `data/repositorios_1000.csv` .

## Observações
- Defina a variável de ambiente `GITHUB_TOKEN` com seu token do GitHub antes de executar.
- Para carregar o token diretamente na sessão do PowerShell, utilize:
   ```powershell
   $env:GITHUB_TOKEN = "SEU_TOKEN_AQUI"
   ```
- O script coleta 10 páginas de 100 repositórios cada, ordena por estrelas e exporta os 1000 mais populares.
- Para análise e relatório, utilize o CSV e o arquivo de relatório gerado em `data/`.


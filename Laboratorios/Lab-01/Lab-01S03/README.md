# Lab01S02 – Coleta e análise de 1000 repositórios

## Objetivo

Coletar dados dos 1.000 repositórios com maior número de estrelas no GitHub, exportar para CSV e preparar a primeira versão do relatório com hipóteses informais.

## Estrutura desta pasta

| Item | Descrição |
|------|-----------|
| `README.md` | Este arquivo |
| `fetch_repos.py` | Script de coleta automática (1000 repositórios, exporta CSV) |
| `repositorios_1000.csv` | Dados coletados (será gerado pelo script) |

## Execução (Lab01S02)

1. Acesse a pasta da etapa:
   ```powershell
   cd LabMedExp\Laboratorios\Lab-01\Lab01S02
   ```
2. Execute o script de coleta:
   ```powershell
   python fetch_repos.py
   ```
   Os dados serão salvos em `repositorios_1000.csv` dentro desta subpasta.

## Observações
- Defina a variável de ambiente `GITHUB_TOKEN` com seu token do GitHub antes de executar.
- O script coleta 10 páginas de 100 repositórios cada, ordena por estrelas e exporta os 1000 mais populares.
- Para análise e relatório, utilize o CSV gerado.
# Lab01S02 – Coleta e análise de 1000 repositórios

## Objetivo

Coletar dados dos 1.000 repositórios com maior número de estrelas no GitHub, exportar para CSV e preparar a primeira versão do relatório com hipóteses informais.

## Estrutura desta pasta

| Item | Descrição |
|------|-----------|
| `README.md` | Este arquivo |
| `fetch_repos.py` | Script de coleta automática (1000 repositórios, exporta CSV) |
| `repositorios_1000.csv` | Dados coletados (será gerado pelo script) |

## Execução (Lab01S02)

1. Acesse a pasta da etapa:
   ```powershell
   cd LabMedExp\Laboratorios\Lab-01\Lab01S02
   ```
2. Execute o script de coleta:
   ```powershell
   python fetch_repos.py
   ```
   Os dados serão salvos em `repositorios_1000.csv` dentro desta subpasta.

## Observações
- Defina a variável de ambiente `GITHUB_TOKEN` com seu token do GitHub antes de executar.
- O script coleta 10 páginas de 100 repositórios cada, ordena por estrelas e exporta os 1000 mais populares.
- Para análise e relatório, utilize o CSV gerado.

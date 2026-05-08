# Coleta PRs para os repositórios nas posições 41–99 do repositorios.csv original.
# Pré-requisito: definir o token antes de executar, por exemplo:
#   $env:GITHUB_TOKEN = "ghp_..."
#
# Uma pessoa por fatia ao mesmo tempo (evitar dois processos no mesmo repositório).
# Saída: data/prs_brutos/

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not $env:GITHUB_TOKEN) {
    Write-Error "Defina GITHUB_TOKEN antes de rodar este script."
}

python coleta_prs.py --input data/repositorios_041_099.csv

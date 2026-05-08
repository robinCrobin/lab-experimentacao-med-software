# Coleta PRs para os repositórios nas posições 141–200 do repositorios.csv original (fatia 141–200).
# Pré-requisito: definir o token antes de executar, por exemplo:
#   $env:GITHUB_TOKEN = "ghp_..."
#
# Não execute a mesma fatia em dois computadores ao mesmo tempo.
# A saída vai para data/prs_brutos/ (mesmo diretório do processo principal).

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not $env:GITHUB_TOKEN) {
    Write-Error "Defina GITHUB_TOKEN antes de rodar este script."
}

python coleta_prs.py --input data/repositorios_141_200.csv

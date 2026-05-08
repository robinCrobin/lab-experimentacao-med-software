# Participante_B — repositórios nas posições 150–200 do repositorios.csv original.
# Pré-requisito:
#   $env:GITHUB_TOKEN = "ghp_..."
#
# Uma pessoa por fatia ao mesmo tempo.
# Saída: data/prs_brutos/

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not $env:GITHUB_TOKEN) {
    Write-Error "Defina GITHUB_TOKEN antes de rodar este script."
}

python coleta_prs.py --input data/repositorios_150_200.csv

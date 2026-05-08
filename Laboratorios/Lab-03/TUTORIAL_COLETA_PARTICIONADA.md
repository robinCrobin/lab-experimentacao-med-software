# Tutorial — coleta particionada de PRs (Lab 03)

Este documento descreve **quem coleta qual intervalo** no `data/repositorios.csv`, **como executar** e **o que versionar no Git** ao final.

## Visão geral das fatias (200 repositórios)

O arquivo `data/repositorios.csv` tem **200 linhas de dados** (além do cabeçalho), na ordem gerada pelo `coleta_repositorios.py`. As posições são **1 a 200** (primeira linha de dados = posição 1).

| Posições | Quantidade | Responsável | Arquivo CSV | Script `.ps1` |
|----------|------------|-------------|-------------|----------------|
| **1–40** | 40 | Você (já coletado antes da divisão atual; checkpoints em `prs_brutos`) | `repositorios.csv` (lista completa, interrompida após o 40) | — |
| **41–99** | 59 | Você | `data/repositorios_041_099.csv` | `coleta_prs_lote_041_099.ps1` |
| **100–149** | 50 | Participante_A | `data/repositorios_100_149.csv` | `coleta_prs_lote_100_149.ps1` |
| **150–200** | 51 | Participante_B | `data/repositorios_150_200.csv` | `coleta_prs_lote_150_200.ps1` |

**Totais:** 40 + 59 + 50 + 51 = **200** repositórios.

**Referência dos limites (primeiro e último `nameWithOwner` da fatia, na versão atual da lista):**

- 41–99: `anomalyco/opencode` → `Anduin2017/HowToCook`
- 100–149: `pytorch/pytorch` → `bregman-arie/devops-exercises`
- 150–200: `zed-industries/zed` → `daytonaio/daytona`

*(Se `repositorios.csv` for regenerado, esses nomes podem mudar; os CSVs fatiados sempre seguem a ordem do arquivo na época em que foram gerados.)*

---

## Regras de paralelismo

1. **Um repositório = um processo por vez.** Dois computadores não devem coletar o **mesmo** `owner/repo` ao mesmo tempo (mesmo arquivo em `data/prs_brutos/`).

2. **Fatias diferentes** (41–99, 100–149, 150–200) **podem** rodar **em paralelo**, cada um com **seu** `GITHUB_TOKEN`.

3. **Não** rode duas vezes a **mesma** fatia em máquinas diferentes sem combinar (risco de corrida no mesmo `.json`).

---

## Pré-requisitos (todos)

1. Pasta do laboratório: `Laboratorios/Lab-03`.

2. Ambiente Python:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. [Personal Access Token](https://github.com/settings/tokens) do GitHub (leitura da API).

4. Token **só na sessão** (não commitar):

   ```powershell
   $env:GITHUB_TOKEN = "seu_token"
   ```

---

## Comandos por responsável

### Você — fatia **41–99**

```powershell
cd Laboratorios\Lab-03
$env:GITHUB_TOKEN = "seu_token"
.\coleta_prs_lote_041_099.ps1
```

Equivalente:

```powershell
python coleta_prs.py --input data/repositorios_041_099.csv
```

### Participante_A — fatia **100–149**

```powershell
cd Laboratorios\Lab-03
$env:GITHUB_TOKEN = "token_do_participante_A"
.\coleta_prs_lote_100_149.ps1
```

### Participante_B — fatia **150–200**

```powershell
cd Laboratorios\Lab-03
$env:GITHUB_TOKEN = "token_do_participante_B"
.\coleta_prs_lote_150_200.ps1
```

### Parâmetros úteis (qualquer fatia)

- `--force`: recolhe mesmo com checkpoint existente (só se precisar refazer).
- `--max-prs-per-repo N`: altera o limite de PRs por repositório após os filtros; documentar no relatório se mudarem o padrão.

---

## Depois que as três fatias estiverem concluídas

Reúnam os arquivos em **uma** pasta `data/prs_brutos/` (mesmo clone ou cópia dos JSON — um arquivo por repositório). Devem existir **200** checkpoints `*.json` para cobrir os 200 repositórios da lista (40 seus + 59 + 50 + 51).

Geração do dataset único:

```powershell
python extrai_metricas.py --input-dir data/prs_brutos --output data/dataset_prs.csv
```

---

## O que commitar no Git após as coletas

**Recomendado versionar**

- Scripts: `coleta_prs.py`, `coleta_repositorios.py`, `extrai_metricas.py`, `requirements.txt`.
- Fatias: `data/repositorios_041_099.csv`, `data/repositorios_100_149.csv`, `data/repositorios_150_200.csv`.
- Tutorial: `TUTORIAL_COLETA_PARTICIONADA.md`.
- Scripts: `coleta_prs_lote_041_099.ps1`, `coleta_prs_lote_100_149.ps1`, `coleta_prs_lote_150_200.ps1`.
- `data/repositorios.csv` e `data/repositorios.json` se forem a lista oficial acordada.

**Dados — alinhar com professor/equipe**

- `data/dataset_prs.csv`: artefato principal da análise; commitar se o tamanho permitir, ou **Git LFS** / arquivo compactado externo.
- `data/prs_brutos/*.json`: em geral **muito grande**; muitas equipes não versionam tudo e usam backup compartilhado.

**Nunca commitar**

- Tokens, `.env` com segredos.
- Pasta **`Laboratorios/Lab-03/auxiliar/`** (PDF, rascunhos locais) — está no `.gitignore`.

---

## Mensagem de commit (exemplo)

> Lab03: tutorial de coleta particionada (41–99, 100–149, 150–200), CSVs e scripts PowerShell atualizados.

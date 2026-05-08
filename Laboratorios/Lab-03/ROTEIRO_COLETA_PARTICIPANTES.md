# Roteiro — coleta de PRs (Lab 03) em equipe

Este roteiro descreve **quem roda o quê**, **como executar** e **o que versionar no Git** depois que todas as coletas terminarem.

## Visão geral das fatias

O arquivo `data/repositorios.csv` contém **200 repositórios** (1 cabeçalho + 200 linhas de dados), na ordem usada pelo `coleta_repositorios.py`.

| Fatia (posições no CSV) | Arquivo de entrada | Script de conveniência | Responsável sugerido |
|-------------------------|--------------------|------------------------|----------------------|
| 1–40 | `data/repositorios.csv` (interromper após o 40) **ou** fatia manual | — | Participante A (máquina principal) |
| 41–80 | `data/repositorios_041_080.csv` | `coleta_prs_lote_041_080.ps1` | Participante A (ou B, se combinado) |
| 81–140 | `data/repositorios_081_140.csv` | `coleta_prs_lote_081_140.ps1` | Participante B |
| 141–200 | `data/repositorios_141_200.csv` | `coleta_prs_lote_141_200.ps1` | Participante C |

**Regra de ouro:** em um dado repositório, **só um processo** deve coletar por vez. Duas máquinas na **mesma fatia** ao mesmo tempo podem corromper o mesmo `data/prs_brutos/owner__repo.json`.

**Regra de paralelismo:** faixas **diferentes** (ex.: 41–80 e 81–140) **podem** rodar em paralelo, cada um com **seu** `GITHUB_TOKEN`.

---

## Pré-requisitos (todos os participantes)

1. Clonar o repositório e ir para a pasta do Lab 03:

   `Laboratorios/Lab-03`

2. Criar/ativar o ambiente virtual e instalar dependências:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Criar um [Personal Access Token](https://github.com/settings/tokens) do GitHub com permissão para leitura da API (escopos padrão de leitura costumam bastar).

4. **Não** commitar o token. No PowerShell, **por sessão**:

   ```powershell
   $env:GITHUB_TOKEN = "seu_token"
   ```

---

## O que cada participante executa

### Participante A — repositórios 1–40 (e depois 41–80, se for a mesma pessoa)

**Opção 1 — lista completa e parada no 40**

1. Rodar:

   ```powershell
   python coleta_prs.py --input data/repositorios.csv
   ```

2. Após **concluir** o repositório da posição **40**, interromper com **Ctrl+C** **antes** de começar o `[41/200]`.

3. Em seguida rodar a fatia 41–80 (veja abaixo).

**Opção 2 — só a fatia 41–80** (se 1–40 já estiverem com checkpoint em `data/prs_brutos/`)

```powershell
.\coleta_prs_lote_041_080.ps1
```

(ou `python coleta_prs.py --input data/repositorios_041_080.csv`)

### Participante B — repositórios 81–140

```powershell
$env:GITHUB_TOKEN = "token_do_participante_B"
.\coleta_prs_lote_081_140.ps1
```

### Participante C — repositórios 141–200

```powershell
$env:GITHUB_TOKEN = "token_do_participante_C"
.\coleta_prs_lote_141_200.ps1
```

### Parâmetros úteis (qualquer fatia)

- `--force`: refaz repositórios mesmo já existindo checkpoint (use só quando precisar recolher).
- `--max-prs-per-repo N`: limite de PRs por repo após filtros (padrão do script; reduz tempo em repositórios enormes). Documentar no relatório se alterarem.

---

## Depois que **todas** as fatias terminarem (uma máquina com o repositório reunido)

1. Garantir que `data/prs_brutos/` contenha **200 arquivos** `*.json` (um por repositório), ou o conjunto acordado pela equipe.

2. Gerar o dataset consolidado:

   ```powershell
   python extrai_metricas.py --input-dir data/prs_brutos --output data/dataset_prs.csv
   ```

3. Conferir `data/dataset_prs.csv` (número de linhas, colunas esperadas).

---

## O que commitar após as coletas finalizadas

**Sempre commitar (recomendado)**

- Alterações em scripts: `coleta_prs.py`, `coleta_repositorios.py`, `extrai_metricas.py`, `requirements.txt`.
- Arquivos de fatia e roteiro: `data/repositorios_041_080.csv`, `data/repositorios_081_140.csv`, `data/repositorios_141_200.csv`, `ROTEIRO_COLETA_PARTICIPANTES.md`, `coleta_prs_lote_*.ps1`.
- `data/repositorios.csv` e `data/repositorios.json` **se** forem a versão oficial da equipe.

**Dados — combinar com o professor/equipe (tamanho do repositório)**

- **`data/dataset_prs.csv`**: costuma ser o principal artefato para análise; se couber no Git, commitar. Se for muito grande, usar **Git LFS** ou anexar zip no ambiente indicado pela disciplina.
- **`data/prs_brutos/*.json`**: muito volumoso na maioria dos casos; muitas equipes **não** commitam tudo e guardam backup em drive compartilhado. Se precisar versionar, preferir **Git LFS** ou amostra documentada.

**Nunca commitar**

- Tokens, `.env` com segredos, ou qualquer arquivo que contenha `GITHUB_TOKEN`.
- Pasta **`Laboratorios/Lab-03/auxiliar/`** (PDF do enunciado, rascunhos, materiais locais). Está listada no `.gitignore` do repositório — não enviar ao GitHub.

---

## Mensagem sugerida para o commit (exemplo)

> Lab03: roteiro de coleta em equipe, script da fatia 41–80 e dataset consolidado (`dataset_prs.csv`).  
> Inclui checkpoints em `prs_brutos/` apenas se a política do grupo/disciplina permitir o tamanho.

(Ajuste a última frase conforme o que de fato for versionado.)

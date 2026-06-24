# Lab 05 – GraphQL vs REST – Um experimento controlado

**Sprint 5** da disciplina Laboratório de Experimentação de Software.

Experimento controlado que avalia quantitativamente os benefícios de uma API
**GraphQL** frente a uma API **REST**, usando a API pública do GitHub (que
oferece as duas abordagens sobre a mesma base). Perguntas de pesquisa:

- **RQ1.** Respostas GraphQL são mais rápidas que respostas REST?
- **RQ2.** Respostas GraphQL têm tamanho menor que respostas REST?

## Enunciado

- [LABORATÓRIO 05 - GraphQL vs REST - Um experimento controlado.pdf](https://github.com/joaopauloaramuni/laboratorio-de-experimentacao-de-software/blob/main/LABORATORIOS/LABORAT%C3%93RIO%2005%20-%20GraphQL%20vs%20REST%20-%20Um%20experimento%20controlado.pdf)

## Estrutura desta pasta

| Item | Descrição |
|------|-----------|
| `DESENHO_EXPERIMENTO.md` | Desenho do experimento (Sprint Lab05S01): hipóteses, variáveis, tratamentos, objetos, projeto, medições e ameaças à validade. |
| `RELATORIO.md` | Relatório final (Sprint Lab05S02): metodologia, resultados estatísticos e discussão. |
| `scripts/coletar_repos.py` | Coleta os objetos experimentais (repositórios populares) via GraphQL. |
| `scripts/benchmark.py` | Executa os tratamentos REST e GraphQL medindo tempo e tamanho. |
| `scripts/analise.py` | Validação, estatísticas descritivas, testes de hipótese e figuras. |
| `scripts/dashboard.py` | Dashboard HTML de visualização (Sprint Lab05S03). |
| `data/` | Dados coletados e processados (`repositorios.json`, `medicoes.csv`, tabelas-resumo). |
| `figures/` | Figuras geradas pela análise. |
| `dashboard/dashboard_lab05.html` | Dashboard final. |
| `requirements.txt` | Dependências. |
| `.env.example` | Modelo de configuração do token do GitHub. |

## Pré-requisitos

- Python 3.
- Dependências: `pip install -r requirements.txt`.
- Token de acesso do GitHub na variável `GITHUB_TOKEN` (via `.env`).

### Token do GitHub

O token só precisa acessar **dados públicos** (eleva o rate limit para 5.000
req/h). Gere em <https://github.com/settings/tokens>:

- **Classic token:** marque apenas o escopo `public_repo` (e, se quiser,
  `read:user`).
- **Fine-grained token:** *Public Repositories (read-only)* já basta.

Copie `.env.example` para `.env` e preencha:

```zsh
cp .env.example .env
# edite .env e cole o token em GITHUB_TOKEN
```

## Como executar (pipeline completo)

Na pasta `Laboratorios/Lab-05/`:

```zsh
pip install -r requirements.txt

# 1) Coletar objetos experimentais (repositórios populares)
python scripts/coletar_repos.py --n 100

# 2) Executar o experimento (tratamentos REST e GraphQL)
python scripts/benchmark.py --rep 5

# 3) Analisar resultados (estatísticas + testes + figuras)
python scripts/analise.py

# 4) Gerar o dashboard de visualização
python scripts/dashboard.py
```

Abra `dashboard/dashboard_lab05.html` no navegador para ver os resultados.

## Metodologia (resumo)

- **Desenho pareado:** cada repositório recebe os dois tratamentos (REST e
  GraphQL), solicitando exatamente os mesmos campos.
- **Medições:** 100 repositórios × 2 APIs × 5 repetições; usa-se a **mediana**
  das repetições por par e o teste **Wilcoxon pareado** para as hipóteses.
- **Métricas:** tempo de resposta (ms) e tamanho do payload (bytes).

Detalhes completos em `DESENHO_EXPERIMENTO.md` e `RELATORIO.md`.

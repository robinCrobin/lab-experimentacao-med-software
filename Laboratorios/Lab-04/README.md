# Lab 04 – Visualização de dados utilizando uma ferramenta de BI

**Sprint 4** da disciplina Laboratório de Experimentação de Software.

## Enunciado

O enunciado oficial está no repositório da disciplina:

- [LABORATÓRIO 04 - Visualização de dados utilizando uma ferramenta de bi.pdf](https://github.com/joaopauloaramuni/laboratorio-de-experimentacao-de-software/blob/main/LABORATORIOS/LABORAT%C3%93RIO%2004%20-%20Visualiza%C3%A7%C3%A3o%20de%20dados%20utilizando%20uma%20ferramenta%20de%20bi.pdf)

## Conteúdo desta pasta

Aqui serão colocados o planejamento, dashboards/relatórios da ferramenta de BI escolhida, datasets e documentação do Lab 04.

## Material de apoio

Dados e visualizações dos Labs anteriores (ex.: Lab 01) podem ser reutilizados ou complementados com novas fontes para análise em BI.

---

## 📊 Dashboard do Artigo TIS 6 — Tamanho de Commits × Manutenibilidade

### 📁 Estrutura

```
Lab-04/
├── README.md (este arquivo)
├── scripts/
│   └── gerar_dados_dashboard.py     # Gerador de CSVs (reproduzível)
└── dados_dashboard/
    ├── *.csv                        # 12 CSVs prontos para Power BI (5,2 MB)
    ├── GUIA_DASHBOARD_POWERBI.md    # Passo a passo de montagem
    └── README.md                     # Documentação dos dados
```

### ✅ O que já está pronto

Os arquivos em `dados_dashboard/` incluem **12 CSVs** com dados consolidados de:
- **Caracterização**: 500 repositórios Python (stars, contribuidores, commits)
- **Q1**: Relação tamanho do commit × ocorrência de bugs (BIC)
- **Q2**: Tamanho do PR × complexidade da revisão (69.615 PRs)
- **Q3**: Tamanho do commit × manutenibilidade (CC/LOC, reverts)

**Todos os números validados contra o artigo publicado** ✓

### 🚀 Para montar o dashboard

1. **Abra Power BI Desktop**
2. **Obter dados → Texto/CSV**
3. **Importe todos os CSVs** da pasta `dados_dashboard/` (encoding UTF-8)
4. **Siga `GUIA_DASHBOARD_POWERBI.md`** para montar os 4 painéis (Caracterização, Q1, Q2, Q3)
5. **Exportar em PDF** (entrega do Lab 04)
6. **Inserir figuras** no artigo `Artigo/relatorio.tex` (Seções 3 e 4)

### 📈 Números esperados (checklist)

| Q | Metrica | Pequeno | Médio | Grande |
|---|---------|---------|-------|--------|
| **Q1** | Taxa BIC | 0,82% | 2,90% | 6,98% |
| **Q2** | Comentários | 1,58 | 2,45 | 5,67 |
| **Q2** | Densidade | 0,125 | 0,024 | 0,004 |
| **Q3** | CC/LOC | 1,96 | 0,16 | 0,04 |
| **Q3** | Taxa reverts | 1,26% | 1,99% | 3,56% |

### 🔧 Regenerar os dados (opcional)

Se precisar recalcular a partir das fontes brutas:

```bash
cd scripts/
python3 gerar_dados_dashboard.py
```

Pré-requisitos:
- Acesso a `/Facul/plf-es-2026-1-ti6-8508100-ti6grupo7/Instrumentos/Resultados/raw/`
- Acesso a `/Facul/plf-es-2026-1-ti6-8508100-ti6grupo7/q2_dados_processed/processed/prs_clean.csv`
- Acesso a `/Facul/plf-es-2026-1-ti6-8508100-ti6grupo7/Instrumentos/Codigos/szz-commit-size/szz_data/resultados/`

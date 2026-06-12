# -*- coding: utf-8 -*-
"""
Prepara os CSVs para upload no Google Looker Studio (LAB04).

O Looker Studio importa um CSV por "fonte de dados". Este script copia para
`dados_looker/` apenas os arquivos necessários, garantindo:
  - UTF-8 sem BOM (acentos e símbolos ≤ → χ² preservados);
  - separador decimal "." (que o Looker interpreta como número);
  - ordenação correta das classes (prefixos "1.", "2.", "3." mantidos).

Também gera dois auxiliares "long" que rendem gráficos melhores no Looker:
  - caracterizacao_distribuicoes.csv  (3 distribuições num só controle)
  - q1_taxa_bic_ic.csv                (taxa + limites IC95 em colunas próprias)

Rodar:
    python3 preparar_dados_looker.py
"""
import csv
import os
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "dados_dashboard")
OUT = os.path.join(BASE, "dados_looker")
os.makedirs(OUT, exist_ok=True)

# 1) Arquivos que já estão prontos: cópia direta (sem a base bruta de 102k PRs,
#    usada só no scatter exploratório opcional 2.5).
COPIAR = [
    "01_caracterizacao_repositorios.csv",
    "01b_caracterizacao_resumo.csv",
    "01c_caracterizacao_commits_por_classe.csv",
    "02_q1_taxa_bic_por_classe.csv",
    "02_q1_distribuicao_classes_por_grupo.csv",
    "02_q1_por_repositorio.csv",
    "02_q1_testes_estatisticos.csv",
    "03_q2_resumo_categoria.csv",
    "03_q2_fechamento_por_faixa_loc.csv",
    "03_q2_testes_estatisticos.csv",
    "04_q3_resumo_categoria.csv",
    "04_q3_testes_estatisticos.csv",
]


def ler(nome):
    with open(os.path.join(SRC, nome), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def escrever(nome, campos, linhas):
    # utf-8 (sem BOM) e newline padrão — o Looker lê melhor assim.
    with open(os.path.join(OUT, nome), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)


def copia_limpa(nome):
    escrever(nome, list(ler(nome)[0].keys()), ler(nome))


# 2) Auxiliar: as 3 distribuições de caracterização em formato "long".
#    Permite um único gráfico com um controle de "dimensao" no dashboard.
def distribuicoes_long():
    repos = ler("01_caracterizacao_repositorios.csv")
    dims = [
        ("Estrelas", "faixa_stars"),
        ("Contribuidores", "faixa_contributors"),
        ("Commits (5 anos)", "faixa_commits"),
    ]
    linhas = []
    for rotulo, col in dims:
        cont = {}
        for r in repos:
            cont[r[col]] = cont.get(r[col], 0) + 1
        for faixa, n in cont.items():
            linhas.append({"dimensao": rotulo, "faixa": faixa, "n_repositorios": n})
    escrever("caracterizacao_distribuicoes.csv",
             ["dimensao", "faixa", "n_repositorios"], linhas)


# 3) Auxiliar: taxa de BIC com erro do IC95 já calculado (barra de +/-).
def q1_taxa_ic():
    linhas = []
    for r in ler("02_q1_taxa_bic_por_classe.csv"):
        taxa = float(r["taxa_bic_pct"])
        linhas.append({
            "classe_tamanho": r["classe_tamanho"],
            "taxa_bic_pct": taxa,
            "ic95_inf_pct": float(r["ic95_inf_pct"]),
            "ic95_sup_pct": float(r["ic95_sup_pct"]),
            "erro_inf": round(taxa - float(r["ic95_inf_pct"]), 4),
            "erro_sup": round(float(r["ic95_sup_pct"]) - taxa, 4),
            "loc_mediana": r["loc_mediana"],
            "arquivos_mediana": r["arquivos_mediana"],
        })
    escrever("q1_taxa_bic_ic.csv",
             ["classe_tamanho", "taxa_bic_pct", "ic95_inf_pct", "ic95_sup_pct",
              "erro_inf", "erro_sup", "loc_mediana", "arquivos_mediana"], linhas)


def main():
    for nome in COPIAR:
        copia_limpa(nome)
    distribuicoes_long()
    q1_taxa_ic()
    arquivos = sorted(os.listdir(OUT))
    print(f"{len(arquivos)} arquivos gerados em dados_looker/:")
    for a in arquivos:
        print(" -", a)


if __name__ == "__main__":
    main()

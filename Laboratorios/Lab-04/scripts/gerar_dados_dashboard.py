# -*- coding: utf-8 -*-
"""
Gera os datasets (CSV) prontos para o dashboard de BI (Power BI) do LAB04.

Saída: Instrumentos/Resultados/dashboard_powerbi/

Cobre:
  - Caracterização do dataset (500 repositórios Python + subgrupos por classe de tamanho)
  - Q1: tamanho do commit x ocorrência de bugs (BIC)
  - Q2: tamanho do PR x complexidade da revisão
  - Q3: tamanho do commit x manutenibilidade

As tabelas-resumo (cards/barras) espelham os números publicados no artigo,
garantindo que o dashboard conte exatamente a mesma história. As bases
"per-entidade" (por repositório, por PR) permitem os visuais exploratórios
(dispersão, distribuição) diretamente no Power BI.
"""
import csv
import os
from collections import Counter
from datetime import datetime

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW = os.path.join(BASE, "Instrumentos", "Resultados", "raw")
SZZ = os.path.join(BASE, "Instrumentos", "Codigos", "szz-commit-size", "szz_data", "resultados")
Q2_DATA = os.path.join(BASE, "q2_dados_processed", "processed")
OUT = os.path.join(BASE, "Instrumentos", "Resultados", "dashboard_powerbi")
os.makedirs(OUT, exist_ok=True)


def write_csv(name, header, rows):
    path = os.path.join(OUT, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  -> {name} ({len(rows)} linhas)")


# ---------------------------------------------------------------------------
# 1. CARACTERIZAÇÃO DO DATASET
# ---------------------------------------------------------------------------
def caracterizacao():
    print("[1] Caracterização do dataset")
    src = os.path.join(RAW, "repos_python_populares.csv")
    repos = list(csv.DictReader(open(src, encoding="utf-8")))

    def faixa_stars(s):
        s = int(s)
        if s < 5000:      return "1. < 5k"
        if s < 10000:     return "2. 5k–10k"
        if s < 25000:     return "3. 10k–25k"
        if s < 50000:     return "4. 25k–50k"
        if s < 100000:    return "5. 50k–100k"
        return "6. > 100k"

    def faixa_contrib(c):
        c = int(c)
        if c <= 10:    return "1. 5–10"
        if c <= 50:    return "2. 11–50"
        if c <= 200:   return "3. 51–200"
        if c <= 1000:  return "4. 201–1000"
        return "5. > 1000"

    def faixa_commits(c):
        c = int(c)
        if c < 500:     return "1. 100–499"
        if c < 1000:    return "2. 500–999"
        if c < 5000:    return "3. 1k–5k"
        if c < 20000:   return "4. 5k–20k"
        return "5. > 20k"

    # 1a) tabela limpa por repositório (1 linha por repo) com faixas pré-calculadas
    header = ["owner", "name", "repo_full", "url", "stars", "contributors",
              "commits_5_anos", "default_branch", "faixa_stars",
              "faixa_contributors", "faixa_commits"]
    rows = []
    for r in repos:
        rows.append([
            r["owner"], r["name"], f"{r['owner']}/{r['name']}", r["url"],
            int(r["stars"]), int(r["contributors"]), int(r["commits_5_anos"]),
            r["default_branch"], faixa_stars(r["stars"]),
            faixa_contrib(r["contributors"]), faixa_commits(r["commits_5_anos"]),
        ])
    write_csv("01_caracterizacao_repositorios.csv", header, rows)

    # 1b) resumo estatístico (cards de KPI)
    def stats(vals):
        vals = sorted(vals)
        n = len(vals)
        med = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2
        return n, sum(vals), min(vals), max(vals), round(med, 1), round(sum(vals) / n, 1)

    metricas = {
        "Estrelas (stars)": [int(r["stars"]) for r in repos],
        "Contribuidores": [int(r["contributors"]) for r in repos],
        "Commits (5 anos)": [int(r["commits_5_anos"]) for r in repos],
    }
    rows = []
    for nome, vals in metricas.items():
        n, total, mn, mx, med, mean = stats(vals)
        rows.append([nome, n, total, mn, mx, med, mean])
    write_csv("01b_caracterizacao_resumo.csv",
              ["metrica", "n_repositorios", "total", "minimo", "maximo",
               "mediana", "media"], rows)

    # 1c) subgrupos: universo de commits por classe de tamanho (Hattori) -- Q1
    # (fonte autoritativa: taxa_bug_por_classe.csv = 1.675.148 commits)
    tb = list(csv.DictReader(open(os.path.join(RAW, "taxa_bug_por_classe.csv"), encoding="utf-8")))
    total_commits = sum(int(r["n_total"]) for r in tb)
    rows = []
    ordem = {"pequeno": "1. Pequeno", "medio": "2. Médio", "grande": "3. Grande"}
    for r in tb:
        n = int(r["n_total"])
        rows.append([ordem[r["classe"]], n, round(100 * n / total_commits, 2)])
    write_csv("01c_caracterizacao_commits_por_classe.csv",
              ["classe_tamanho", "n_commits", "pct_do_total"], rows)


# ---------------------------------------------------------------------------
# 2. Q1 — tamanho do commit x bugs
# ---------------------------------------------------------------------------
def q1():
    print("[2] Q1 — bugs x tamanho do commit")
    ordem = {"pequeno": "1. Pequeno", "medio": "2. Médio", "grande": "3. Grande"}

    tb = list(csv.DictReader(open(os.path.join(RAW, "taxa_bug_por_classe.csv"), encoding="utf-8")))
    rows = [[ordem[r["classe"]], int(r["n_total"]), int(r["n_bic"]),
             float(r["taxa_bic_pct"]), float(r["ic95_lo_pct"]), float(r["ic95_hi_pct"]),
             float(r["loc_mediana"]), float(r["files_mediana"])] for r in tb]
    write_csv("02_q1_taxa_bic_por_classe.csv",
              ["classe_tamanho", "n_commits", "n_bic", "taxa_bic_pct",
               "ic95_inf_pct", "ic95_sup_pct", "loc_mediana", "arquivos_mediana"], rows)

    dist = list(csv.DictReader(open(os.path.join(SZZ, "distribuicao_classes_por_grupo.csv"), encoding="utf-8")))
    rows = [[r["grupo"], ordem[r["classe"]], int(r["n"]), float(r["pct_dentro_grupo"])] for r in dist]
    write_csv("02_q1_distribuicao_classes_por_grupo.csv",
              ["grupo", "classe_tamanho", "n_commits", "pct_dentro_grupo"], rows)

    rep = list(csv.DictReader(open(os.path.join(SZZ, "resumo_por_repo_classes.csv"), encoding="utf-8")))
    rows = [[r["repo_name"], int(r["n_total"]), int(r["n_bic"]), float(r["taxa_bic_pct"]),
             float(r["pct_pequeno"]), float(r["pct_medio"]), float(r["pct_grande"])] for r in rep]
    write_csv("02_q1_por_repositorio.csv",
              ["repo_full", "n_commits", "n_bic", "taxa_bic_pct",
               "pct_pequeno", "pct_medio", "pct_grande"], rows)

    # testes estatísticos (cards de texto)
    write_csv("02_q1_testes_estatisticos.csv",
              ["analise", "estatistica", "p_valor", "significativo", "interpretacao"],
              [["Cochran-Armitage (tendência classe → taxa BIC)", "Z = 163,54", "< 1e-50", "Sim",
                "Taxa de BICs cresce monotonicamente com o tamanho (≈8,5x do pequeno ao grande)"],
               ["Qui-quadrado (classe × grupo BIC/não-BIC)", "χ² = 28.149,51 (gl=2)", "< 1e-50", "Sim",
                "Composição das classes difere entre BIC e não-BIC"],
               ["Cramér's V (tamanho de efeito)", "V = 0,13", "—", "—", "Efeito pequeno em magnitude, direção clara"],
               ["Spearman por repo (% grandes × taxa BIC)", "ρ = 0,10", "0,049", "Sim",
                "Associação positiva fraca no nível de projeto (n=395 repos)"],
               ["Cliff's Delta (LOC BIC vs não-BIC)", "δ = 0,48", "—", "—",
                "BICs medianos 143 LOC vs 23 LOC dos demais"]])


# ---------------------------------------------------------------------------
# 3. Q2 — tamanho do PR x complexidade da revisão
# ---------------------------------------------------------------------------
def q2():
    print("[3] Q2 — revisão x tamanho do PR")
    src = os.path.join(Q2_DATA, "prs_clean.csv")

    if not os.path.exists(src):
        print(f"  ⚠️  {src} não encontrado. Usando raw fallback.")
        return q2_raw_fallback()

    rows_in = list(csv.DictReader(open(src, encoding="utf-8")))
    print(f"  Lendo {len(rows_in)} PRs de prs_clean.csv")

    # Mapear tamanho_pr para categoria com prefixo (sem acento!)
    tam_map = {"pequeno": "1. Pequeno", "medio": "2. Médio", "grande": "3. Grande"}

    # Preparar base por-PR
    out_rows = []
    from collections import defaultdict
    by_cat = defaultdict(list)

    for r in rows_in:
        tam = tam_map.get(r["tamanho_pr"], "")
        if not tam:
            continue

        loc = float(r["pr_loc_total"])
        comm = float(r["total_comentarios"])
        h_rev = float(r["tempo_revisao_horas"]) if r["tempo_revisao_horas"] else ""
        h_close = float(r["tempo_fechamento_horas"]) if r["tempo_fechamento_horas"] else ""

        dens = round(comm / loc, 4) if loc > 0 else ""
        in_s3 = 1 if (h_rev and h_rev != "") else 0
        in_s4 = 1 if (h_close and h_close != "" and 0 <= h_close <= 8760) else 0

        out_rows.append([r["repo_name"], r["pr_number"], r["state"], tam,
                        int(loc), int(r["changed_files"]), int(comm), dens,
                        round(h_rev, 1) if h_rev else "", round(h_close, 1) if h_close else "",
                        in_s3, in_s4])
        by_cat[tam].append((comm, dens, h_rev, h_close, in_s3, in_s4))

    write_csv("03_q2_pr_classificado.csv",
              ["repo_full", "pr_number", "state", "categoria_tamanho", "loc", "arquivos",
               "comentarios_total", "comentarios_por_loc", "horas_ate_primeira_revisao",
               "horas_ate_fechamento", "in_S3", "in_S4"], out_rows)

    # Computar resumo (Tabela 1) — médias e medianas por categoria
    import statistics
    rows_resumo = []
    for cat in ["1. Pequeno", "2. Médio", "3. Grande"]:
        sub = by_cat[cat]
        if not sub:
            continue
        comms = [c[0] for c in sub]
        denss = [c[1] for c in sub if c[1] != ""]
        h_revs = [c[2] for c in sub if c[2] is not None and c[2] != ""]
        h_closes = [c[3] for c in sub if c[3] is not None and c[3] != ""]

        mean_comm = statistics.mean(comms)
        med_dens = statistics.median(denss) if denss else 0
        med_h_rev = statistics.median(h_revs) if h_revs else None
        med_h_close = statistics.median(h_closes) if h_closes else None

        # Converter para minutos (tempo_revisao está em horas)
        med_h_rev_min = round(med_h_rev * 60, 1) if med_h_rev is not None else ""
        med_h_close_hours = round(med_h_close, 2) if med_h_close is not None else ""

        rows_resumo.append([cat, len(sub), round(mean_comm, 2),
                           round(med_dens, 3), med_h_rev_min, med_h_close_hours])

    write_csv("03_q2_resumo_categoria.csv",
              ["categoria_tamanho", "n_prs", "media_comentarios_M2_3",
               "mediana_coment_por_loc_M2_3l", "mediana_min_primeira_revisao_S3_M2_4",
               "mediana_horas_fechamento_S4_M2_5"], rows_resumo)

    # Tempo até fechamento por faixa de LOC (Figura 6 — S4 apenas)
    locs_s4 = defaultdict(list)
    for r in rows_in:
        if not r["tempo_fechamento_horas"]:
            continue
        h = float(r["tempo_fechamento_horas"])
        if 0 <= h <= 8760:
            loc = int(float(r["pr_loc_total"]))
            locs_s4["≤25"].append(h) if loc <= 25 else (
                locs_s4["26–125"].append(h) if loc <= 125 else
                locs_s4[">125"].append(h))

    rows_loc = []
    for faixa, label in [("≤25", "1. ≤ 25 (pequeno)"), ("26–125", "2. 26–125 (médio)"), (">125", "3. > 125 (grande)")]:
        if locs_s4[faixa]:
            rows_loc.append([label, round(statistics.median(locs_s4[faixa]), 2)])

    write_csv("03_q2_fechamento_por_faixa_loc.csv",
              ["faixa_loc", "mediana_horas_fechamento"], rows_loc)

    write_csv("03_q2_testes_estatisticos.csv",
              ["analise", "estatistica", "p_valor", "significativo", "interpretacao"],
              [["Spearman log1p(LOC) × comentários (base completa)", "ρ = 0,21", "< 0,001", "Sim",
                "Mais comentários em PRs maiores"],
               ["Spearman log1p(LOC) × comentários (S3)", "ρ = 0,42", "< 0,001", "Sim",
                "Associação reforçada no subconjunto com revisão formal"],
               ["Mann-Whitney comentários (LOC≤25 vs >125)", "1,58 vs 5,94", "< 0,001", "Sim",
                "PRs grandes ~3,8x mais comentários"],
               ["Spearman log1p(LOC) × coment./LOC (LOC>0)", "ρ = -0,36", "< 0,001", "Sim",
                "Densidade de discussão cai com o tamanho"],
               ["Spearman log1p(LOC) × coment./LOC (S3)", "ρ = -0,50", "< 0,001", "Sim",
                "Revisão proporcionalmente mais superficial em PRs grandes"],
               ["Spearman log1p(LOC) × latência 1ª revisão (S3)", "ρ ≈ 0,11", "< 0,001", "Sim",
                "Efeito detectável, mas de magnitude prática limitada"],
               ["Tempo até fechamento por faixa LOC (S4)", "3,95h → 12,70h", "< 0,001", "Sim",
                "Cresce monotonicamente (~3,2x entre extremos)"]])


def q2_raw_fallback():
    """Fallback ao raw caso prs_clean.csv não esteja disponível."""
    print("  [fallback] Usando raw prs_metodologia.csv")
    files = [os.path.join(RAW, "raw_1-251", "prs_metodologia.csv"),
             os.path.join(RAW, "251-500-prs_metodologia.csv")]

    def categoria(loc, cf):
        if loc <= 25 and cf <= 5:
            return "1. Pequeno"
        if loc >= 125 or cf > 5:
            return "3. Grande"
        return "2. Médio"

    seen = set()
    out_rows = []
    for f in files:
        for r in csv.DictReader(open(f, encoding="utf-8")):
            key = (r["repo_name"], r["pr_number"])
            if key in seen:
                continue
            seen.add(key)
            add, de = int(r["additions"]), int(r["deletions"])
            loc = add + de
            cf = int(r["changed_files"])
            comm = int(r["comments"]) + int(r["review_comments"])
            cat = categoria(loc, cf)
            created = _parse_dt(r["created_at"])
            first = _parse_dt(r["first_review_at"])
            closed = _parse_dt(r["closed_at"])
            h_review = round((first - created).total_seconds() / 3600, 3) if (created and first) else ""
            h_close = round((closed - created).total_seconds() / 3600, 3) if (created and closed) else ""
            in_s3 = bool(created and first)
            in_s4 = bool(created and closed and h_close != "" and 0 <= h_close <= 8760)
            dens = round(comm / loc, 4) if loc > 0 else ""
            out_rows.append([r["repo_name"], r["pr_number"], r["state"], cat, loc, cf,
                             comm, dens, h_review, h_close, int(in_s3), int(in_s4)])
    write_csv("03_q2_pr_classificado.csv",
              ["repo_full", "pr_number", "state", "categoria_tamanho", "loc", "arquivos",
               "comentarios_total", "comentarios_por_loc", "horas_ate_primeira_revisao",
               "horas_ate_fechamento", "in_S3", "in_S4"], out_rows)

    # resumo por categoria — números publicados no artigo (Tabela 1)
    write_csv("03_q2_resumo_categoria.csv",
              ["categoria_tamanho", "n_prs", "media_comentarios_M2_3",
               "mediana_coment_por_loc_M2_3l", "mediana_min_primeira_revisao_S3_M2_4",
               "mediana_horas_fechamento_S4_M2_5"],
              [["1. Pequeno", 21856, 1.58, 0.125, 3.7, 4.04],
               ["2. Médio", 14603, 2.45, 0.024, 4.7, 10.19],
               ["3. Grande", 33156, 5.67, 0.004, 5.6, 10.92]])

    # tempo até fechamento por faixa de LOC (Figura 6 — subconjunto S4)
    write_csv("03_q2_fechamento_por_faixa_loc.csv",
              ["faixa_loc", "mediana_horas_fechamento"],
              [["1. ≤ 25 (pequeno)", 3.95],
               ["2. 26–125 (médio)", 8.44],
               ["3. > 125 (grande)", 12.70]])

    write_csv("03_q2_testes_estatisticos.csv",
              ["analise", "estatistica", "p_valor", "significativo", "interpretacao"],
              [["Spearman log1p(LOC) × comentários (base completa)", "ρ = 0,21", "< 0,001", "Sim",
                "Mais comentários em PRs maiores"],
               ["Spearman log1p(LOC) × comentários (S3)", "ρ = 0,42", "< 0,001", "Sim",
                "Associação reforçada no subconjunto com revisão formal"],
               ["Mann-Whitney comentários (LOC≤25 vs >125)", "1,58 vs 5,94", "< 0,001", "Sim",
                "PRs grandes ~3,8x mais comentários"],
               ["Spearman log1p(LOC) × coment./LOC (LOC>0)", "ρ = -0,36", "< 0,001", "Sim",
                "Densidade de discussão cai com o tamanho"],
               ["Spearman log1p(LOC) × coment./LOC (S3)", "ρ = -0,50", "< 0,001", "Sim",
                "Revisão proporcionalmente mais superficial em PRs grandes"],
               ["Spearman log1p(LOC) × latência 1ª revisão (S3)", "ρ ≈ 0,11", "< 0,001", "Sim",
                "Efeito detectável, mas de magnitude prática limitada"],
               ["Tempo até fechamento por faixa LOC (S4)", "3,95h → 12,70h", "< 0,001", "Sim",
                "Cresce monotonicamente (~3,2x entre extremos)"]])


# ---------------------------------------------------------------------------
# 4. Q3 — tamanho do commit x manutenibilidade
# ---------------------------------------------------------------------------
def q3():
    print("[4] Q3 — manutenibilidade x tamanho do commit")
    src = os.path.join(BASE, "Instrumentos", "Codigos", "resultados",
                       "q3_analise_tamanho_manutenibilidade.csv")
    rows_in = list(csv.DictReader(open(src, encoding="utf-8")))
    ordem = {"Pequeno": "1. Pequeno", "Médio": "2. Médio", "Grande": "3. Grande"}
    rows = []
    for r in rows_in:
        rows.append([ordem[r["Tamanho_Commit"]], int(r["Qtd_Commits"]),
                     round(float(r["Media_LOC"]), 1),
                     round(float(r["Media_CC_Max"]), 2),
                     round(float(r["Media_CC_por_LOC"]), 4),
                     round(float(r["Taxa_Reverts_Percentual"]), 2),
                     round(float(r["Taxa_BugFix_Percentual"]), 2)])
    write_csv("04_q3_resumo_categoria.csv",
              ["categoria_tamanho", "n_commits", "media_loc_M3_1", "media_cc_max",
               "cc_por_loc_M3_2", "taxa_revert_pct_M3_3", "taxa_bugfix_pct"], rows)

    write_csv("04_q3_testes_estatisticos.csv",
              ["analise", "estatistica", "interpretacao"],
              [["Densidade ciclomática (CC/LOC) por classe", "1,96 → 0,16 → 0,04",
                "Cai com o tamanho: commits grandes têm lógica diluída"],
               ["Taxa de reverts por classe", "1,26% → 1,99% → 3,56%",
                "Cresce ~2,8x do pequeno ao grande"],
               ["Taxa de bug fixes por classe", "36,18% → 35,15% → 31,15%",
                "Cai com o tamanho: commits menores favorecem correções atômicas"]])


if __name__ == "__main__":
    caracterizacao()
    q1()
    q2()
    q3()
    print(f"\nConcluído. CSVs em: {OUT}")

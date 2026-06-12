# -*- coding: utf-8 -*-
"""
Gera o dashboard completo em PDF (4 páginas) a partir dos CSVs.
Monta: Caracterização, Q1, Q2, Q3.
"""
import csv
import os
import textwrap
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "dados_looker")
OUT = os.path.join(BASE, "dashboard_output")
os.makedirs(OUT, exist_ok=True)

# Cores por classe
CORES = {"1. Pequeno": "#2E7D32", "2. Médio": "#F9A825", "3. Grande": "#C62828"}

def load_csv(name):
    """Carrega CSV de dados_looker/."""
    path = os.path.join(DATA, name)
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def fmt_num(v):
    """Formata número para exibição."""
    if isinstance(v, str):
        return v
    if isinstance(v, float) and v == int(v):
        return f"{int(v):,}".replace(",", ".")
    return f"{v:,.2f}".replace(",", ".")

def page_title(fig, title):
    """Título da página com margem para não sobrepor os gráficos."""
    fig.suptitle(title, fontsize=18, fontweight="bold", y=0.97)

def gridspec_layout(fig, rows, cols, **kwargs):
    """Grid com margem superior reservada ao título."""
    defaults = dict(hspace=0.45, wspace=0.32, top=0.84, bottom=0.08, left=0.08, right=0.92)
    defaults.update(kwargs)
    return fig.add_gridspec(rows, cols, **defaults)

def wrapped_text(text, width=105):
    return "\n".join(textwrap.wrap(text, width=width))

def annotate_bars(ax, values, fmt, pad=0.12, yerr_top=None):
    """Rótulos acima das barras com espaço no eixo Y."""
    ymax = max(values)
    if yerr_top is not None:
        ymax = max(ymax, max(yerr_top))
    offset = ymax * pad
    ax.set_ylim(0, ymax + offset * 2.5)
    for i, v in enumerate(values):
        ax.text(i, v + offset, fmt(v), ha="center", fontsize=9, fontweight="bold")

# ============================================================================
# PÁGINA 0: CARACTERIZAÇÃO
# ============================================================================
def page_caracterizacao():
    fig = plt.figure(figsize=(11, 8.5))
    page_title(fig, "0 · Caracterização do Dataset")

    gs = gridspec_layout(fig, 3, 2, hspace=0.5, bottom=0.06)

    # KPIs
    ax = fig.add_subplot(gs[0, :])
    ax.axis("off")
    kpis = load_csv("01b_caracterizacao_resumo.csv")
    txt = "500 repositórios Python populares (GitHub)\n"
    txt += f"  • Mediana de stars: {fmt_num(float(kpis[0]['mediana']))}\n"
    txt += f"  • Mediana de contribuidores: {fmt_num(float(kpis[1]['mediana']))}\n"
    txt += f"  • Mediana de commits (5 anos): {fmt_num(float(kpis[2]['mediana']))}"
    ax.text(0.05, 0.5, txt, fontsize=11, va="center")

    # Distribuição stars
    ax = fig.add_subplot(gs[1, 0])
    repos = load_csv("01_caracterizacao_repositorios.csv")
    stars_faixa = defaultdict(int)
    for r in repos:
        faixa = r["faixa_stars"]
        stars_faixa[faixa] += 1
    faixas = sorted(stars_faixa.keys())
    vals = [stars_faixa[f] for f in faixas]
    ax.bar(range(len(faixas)), vals, color="#1976D2", alpha=0.7)
    ax.set_xticks(range(len(faixas)))
    ax.set_xticklabels([f.replace(". ", "\n") for f in faixas], fontsize=8)
    ax.set_ylabel("Quantidade de repos", fontsize=10)
    ax.set_title("Distribuição de stars", fontsize=11, fontweight="bold", pad=12)
    ax.set_ylim(0, max(vals) * 1.12)
    ax.grid(axis="y", alpha=0.3)

    # Distribuição commits por classe
    ax = fig.add_subplot(gs[1, 1])
    commits_clase = load_csv("01c_caracterizacao_commits_por_classe.csv")
    labels = [r["classe_tamanho"].replace("1. ", "").replace("2. ", "").replace("3. ", "") for r in commits_clase]
    sizes = [float(r["pct_do_total"]) for r in commits_clase]
    colors = [CORES.get(r["classe_tamanho"], "#999") for r in commits_clase]
    wedges, _ = ax.pie(sizes, colors=colors, startangle=90)
    ax.legend(
        wedges, [f"{label} ({size:.1f}%)" for label, size in zip(labels, sizes)],
        loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=9, frameon=False,
    )
    ax.set_title("Universo de 1.675.148 commits\npor classe de tamanho", fontsize=11, fontweight="bold", pad=12)

    # Texto narrativo
    ax = fig.add_subplot(gs[2, :])
    ax.axis("off")
    txt = (
        "O estudo analisa 500 repositórios Python populares do GitHub, com uma mediana de 23.174 estrelas "
        "e 1.234 commits no período de 5 anos. Como as análises particionam os dados por classe de tamanho (Hattori & Lanza, 2008), "
        "apresentamos também a composição do universo de 1.675.148 commits: 51,4% pequenos, 37,1% médios e 11,4% grandes."
    )
    ax.text(0.02, 0.85, wrapped_text(txt, width=115), fontsize=10, va="top")

    return fig

# ============================================================================
# PÁGINA 1: Q1 — TAMANHO DO COMMIT × BUGS
# ============================================================================
def page_q1():
    fig = plt.figure(figsize=(11, 8.5))
    page_title(fig, "1 · Q1 — Tamanho do Commit × Ocorrência de Bugs")

    gs = gridspec_layout(fig, 2, 2, hspace=0.5)

    # Taxa BIC por classe
    ax = fig.add_subplot(gs[0, 0])
    q1_taxa = load_csv("02_q1_taxa_bic_por_classe.csv")
    classes = [r["classe_tamanho"] for r in q1_taxa]
    taxa = [float(r["taxa_bic_pct"]) for r in q1_taxa]
    ic_inf = [float(r["ic95_inf_pct"]) for r in q1_taxa]
    ic_sup = [float(r["ic95_sup_pct"]) for r in q1_taxa]
    erros = [np.array(ic_sup) - np.array(taxa), np.array(taxa) - np.array(ic_inf)]

    ax.bar(range(len(classes)), taxa, color=[CORES[c] for c in classes], alpha=0.7, yerr=erros, capsize=5)
    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels([c.replace("1. ", "").replace("2. ", "").replace("3. ", "") for c in classes], fontsize=10)
    ax.set_ylabel("Taxa BIC (%)", fontsize=10)
    ax.set_title("Taxa de Bug-Introducing Commits\npor Classe de Tamanho", fontsize=11, fontweight="bold", pad=12)
    ax.grid(axis="y", alpha=0.3)
    annotate_bars(ax, taxa, lambda v: f"{v:.2f}%", pad=0.15, yerr_top=ic_sup)

    # Distribuição BIC vs não-BIC
    ax = fig.add_subplot(gs[0, 1])
    dist = load_csv("02_q1_distribuicao_classes_por_grupo.csv")
    grupos = list(set(r["grupo"] for r in dist))
    grupos.sort()

    x = np.arange(len(grupos))
    width = 0.25
    for i, cls in enumerate(["1. Pequeno", "2. Médio", "3. Grande"]):
        vals = [float(next((r["pct_dentro_grupo"] for r in dist if r["grupo"] == g and r["classe_tamanho"] == cls), 0)) for g in grupos]
        ax.bar(x + i * width, vals, width, label=cls.replace("1. ", "").replace("2. ", "").replace("3. ", ""), color=CORES[cls], alpha=0.7)

    ax.set_ylabel("% dentro do grupo", fontsize=10)
    ax.set_title("Composição das Classes:\nBIC vs Não-BIC", fontsize=11, fontweight="bold", pad=12)
    ax.set_xticks(x + width)
    ax.set_xticklabels(grupos, fontsize=9)
    ax.legend(fontsize=9, loc="upper right")
    ax.set_ylim(0, 55)
    ax.grid(axis="y", alpha=0.3)

    # Testes estatísticos
    ax = fig.add_subplot(gs[1, :])
    ax.axis("off")
    testes = load_csv("02_q1_testes_estatisticos.csv")

    lines = ["Testes Estatísticos (Q1):", ""]
    for teste in testes[:2]:
        lines.append(f"• {teste['analise']}")
        lines.append(f"  {teste['estatistica']} | p{teste['p_valor']} | {teste['significativo']}")
        lines.append(f"  -> {teste['interpretacao']}")
        lines.append("")

    conclusao = (
        "Hipótese comprovada: A taxa de BICs cresce monotonicamente com o tamanho (8,5x entre extremos). "
        "Commits maiores estão significativamente associados a maior introdução de bugs."
    )
    ax.text(
        0.02, 0.98, "\n".join(lines), fontsize=9, va="top", family="sans-serif",
        transform=ax.transAxes,
    )
    ax.text(
        0.02, 0.08, wrapped_text(conclusao, width=120), fontsize=10, va="bottom",
        bbox=dict(boxstyle="round", facecolor="#E8F5E9", alpha=0.5),
        transform=ax.transAxes,
    )

    return fig

# ============================================================================
# PÁGINA 2: Q2 — TAMANHO DO PR × REVISÃO
# ============================================================================
def page_q2():
    fig = plt.figure(figsize=(11, 8.5))
    page_title(fig, "2 · Q2 — Tamanho do PR × Complexidade da Revisão")

    gs = gridspec_layout(fig, 3, 2, hspace=0.55, bottom=0.06)

    # Comentários
    ax = fig.add_subplot(gs[0, 0])
    q2_resumo = load_csv("03_q2_resumo_categoria.csv")
    classes = [r["categoria_tamanho"] for r in q2_resumo]
    coments = [float(r["media_comentarios_M2_3"]) for r in q2_resumo]
    ax.bar(range(len(classes)), coments, color=[CORES[c] for c in classes], alpha=0.7)
    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels([c.replace("1. ", "").replace("2. ", "").replace("3. ", "") for c in classes], fontsize=10)
    ax.set_ylabel("Média de comentários", fontsize=10)
    ax.set_title("Volume de Comentários por Categoria", fontsize=11, fontweight="bold", pad=12)
    ax.grid(axis="y", alpha=0.3)
    annotate_bars(ax, coments, lambda v: f"{v:.2f}")

    # Densidade
    ax = fig.add_subplot(gs[0, 1])
    dens = [float(r["mediana_coment_por_loc_M2_3l"]) for r in q2_resumo]
    ax.bar(range(len(classes)), dens, color=[CORES[c] for c in classes], alpha=0.7)
    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels([c.replace("1. ", "").replace("2. ", "").replace("3. ", "") for c in classes], fontsize=10)
    ax.set_ylabel("Mediana (comentários/LOC)", fontsize=10)
    ax.set_title("Densidade de Comentários\n(proporcional ao tamanho)", fontsize=11, fontweight="bold", pad=12)
    ax.grid(axis="y", alpha=0.3)
    annotate_bars(ax, dens, lambda v: f"{v:.4f}")

    # Tempo até fechamento
    ax = fig.add_subplot(gs[1, :])
    faixa_loc = load_csv("03_q2_fechamento_por_faixa_loc.csv")
    faixas = [r["faixa_loc"] for r in faixa_loc]
    tempos = [float(r["mediana_horas_fechamento"]) for r in faixa_loc]
    ax.plot(range(len(faixas)), tempos, marker="o", markersize=10, linewidth=2.5, color="#D32F2F")
    ax.fill_between(range(len(faixas)), tempos, alpha=0.3, color="#D32F2F")
    ax.set_xticks(range(len(faixas)))
    ax.set_xticklabels(
        [f.replace("1. ", "").replace("2. ", "").replace("3. ", "") for f in faixas],
        fontsize=9, rotation=12, ha="right",
    )
    ax.set_ylabel("Mediana (horas)", fontsize=10)
    ax.set_title("Tempo até Fechamento por Faixa de LOC (S4)", fontsize=11, fontweight="bold", pad=12)
    ax.grid(alpha=0.3)
    ymax = max(tempos)
    ax.set_ylim(0, ymax * 1.18)
    for i, v in enumerate(tempos):
        ax.text(i, v + ymax * 0.04, f"{v:.2f}h", ha="center", fontsize=9, fontweight="bold")

    # Narrativa
    ax = fig.add_subplot(gs[2, :])
    ax.axis("off")
    narrativa = (
        "Hipótese comprovada (parcialmente qualificada): PRs maiores recebem mais comentários "
        "(1,58 -> 5,67) e levam mais tempo até fechamento (3,95h -> 12,70h). Porém, a densidade de "
        "comentários por LOC cai (0,125 -> 0,004): revisões de mudanças extensas são proporcionalmente "
        "mais superficiais (rho=-0,50 em S3). Isso sugere que o aumento do escopo reduz a capacidade "
        "de revisão criteriosa."
    )
    ax.text(
        0.02, 0.95, wrapped_text(narrativa, width=118), fontsize=10, va="top",
        bbox=dict(boxstyle="round", facecolor="#FFF3E0", alpha=0.5),
        transform=ax.transAxes,
    )

    return fig

# ============================================================================
# PÁGINA 3: Q3 — TAMANHO DO COMMIT × MANUTENIBILIDADE
# ============================================================================
def page_q3():
    fig = plt.figure(figsize=(11, 8.5))
    page_title(fig, "3 · Q3 — Tamanho do Commit × Manutenibilidade")

    gs = gridspec_layout(fig, 2, 3, hspace=0.45, wspace=0.35)

    q3_resumo = load_csv("04_q3_resumo_categoria.csv")
    classes = [r["categoria_tamanho"] for r in q3_resumo]

    # CC/LOC
    ax = fig.add_subplot(gs[0, 0])
    cc_loc = [float(r["cc_por_loc_M3_2"]) for r in q3_resumo]
    ax.bar(range(len(classes)), cc_loc, color=[CORES[c] for c in classes], alpha=0.7)
    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels([c.replace("1. ", "").replace("2. ", "").replace("3. ", "") for c in classes], fontsize=10)
    ax.set_ylabel("CC/LOC", fontsize=10)
    ax.set_title("Densidade Ciclomática\n(CC/LOC)", fontsize=11, fontweight="bold", pad=12)
    ax.grid(axis="y", alpha=0.3)
    annotate_bars(ax, cc_loc, lambda v: f"{v:.3f}")

    # Taxa reverts
    ax = fig.add_subplot(gs[0, 1])
    reverts = [float(r["taxa_revert_pct_M3_3"]) for r in q3_resumo]
    ax.bar(range(len(classes)), reverts, color=[CORES[c] for c in classes], alpha=0.7)
    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels([c.replace("1. ", "").replace("2. ", "").replace("3. ", "") for c in classes], fontsize=10)
    ax.set_ylabel("Taxa de reverts (%)", fontsize=10)
    ax.set_title("Taxa de Reverts\n(rollbacks)", fontsize=11, fontweight="bold", pad=12)
    ax.grid(axis="y", alpha=0.3)
    annotate_bars(ax, reverts, lambda v: f"{v:.2f}%")

    # Taxa bug fix
    ax = fig.add_subplot(gs[0, 2])
    bugfix = [float(r["taxa_bugfix_pct"]) for r in q3_resumo]
    ax.bar(range(len(classes)), bugfix, color=[CORES[c] for c in classes], alpha=0.7)
    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels([c.replace("1. ", "").replace("2. ", "").replace("3. ", "") for c in classes], fontsize=10)
    ax.set_ylabel("Taxa de bug fixes (%)", fontsize=10)
    ax.set_title("Taxa de Bug Fixes\n(correções)", fontsize=11, fontweight="bold", pad=12)
    ax.grid(axis="y", alpha=0.3)
    annotate_bars(ax, bugfix, lambda v: f"{v:.2f}%")

    # Tabela resumo
    ax = fig.add_subplot(gs[1, :])
    ax.axis("off")

    table_data = [
        ["Classe", "n commits", "LOC médio", "CC/LOC", "Reverts", "Bug Fixes"],
    ]
    for r in q3_resumo:
        table_data.append([
            r["categoria_tamanho"].replace("1. ", "").replace("2. ", "").replace("3. ", ""),
            f"{int(r['n_commits']):,}".replace(",", "."),
            f"{float(r['media_loc_M3_1']):.1f}",
            f"{float(r['cc_por_loc_M3_2']):.4f}",
            f"{float(r['taxa_revert_pct_M3_3']):.2f}%",
            f"{float(r['taxa_bugfix_pct']):.2f}%",
        ])

    table = ax.table(cellText=table_data, cellLoc="center", loc="center",
                     colWidths=[0.15, 0.15, 0.15, 0.15, 0.15, 0.15])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)

    for i in range(len(table_data)):
        for j in range(len(table_data[0])):
            cell = table[(i, j)]
            if i == 0:
                cell.set_facecolor("#1976D2")
                cell.set_text_props(weight="bold", color="white")
            else:
                cell.set_facecolor("#F5F5F5" if i % 2 == 0 else "white")

    return fig

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    print("Gerando dashboard PDF...")

    pdf_path = os.path.join(OUT, "dashboard_lab04.pdf")
    with PdfPages(pdf_path) as pdf:
        plt.style.use("default")

        print("  - Pagina 0: Caracterizacao...")
        fig = page_caracterizacao()
        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.25)
        plt.close(fig)

        print("  - Pagina 1: Q1...")
        fig = page_q1()
        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.25)
        plt.close(fig)

        print("  - Pagina 2: Q2...")
        fig = page_q2()
        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.25)
        plt.close(fig)

        print("  - Pagina 3: Q3...")
        fig = page_q3()
        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.25)
        plt.close(fig)

    size_mb = os.path.getsize(pdf_path) / 1024 / 1024
    print(f"\nDashboard gerado: {pdf_path}")
    print(f"   4 paginas | Tamanho: {size_mb:.2f} MB")

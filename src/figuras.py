"""Genera las cuatro figuras del ensayo a partir de los CSV de /data.
python figuras.py   (requiere haber ejecutado antes simulacion_evaluabilidad.py)
"""
import pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA, FIG = ROOT / "data", ROOT / "figures"
FIG.mkdir(exist_ok=True)

# Paleta validada (dataviz, modo claro): dos series categóricas + tintas de texto
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0", "#ffffff"
LIGHT_BLUE, LIGHT_ORANGE, NEUTRAL = "#b7d3f6", "#f6c3ad", "#d9d8d3"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK2, "axes.linewidth": 0.6,
    "xtick.color": INK2, "ytick.color": INK2, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.dpi": 300,
})
W = 6.5  # pulgadas, ancho de página útil


def es(x, dec=1):
    return f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


SOURCES = {}


def finish(fig, name, source):
    SOURCES[name] = source  # la fuente va en el pie de figura del documento
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


# ---------------------------------------------------------------- Figura 1
def fig1():
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.9), gridspec_kw=dict(width_ratios=[1.35, 1], wspace=0.45))
    # (a) magnitudes, en miles
    rows = [
        ("Stock estimado en situación\nirregular, 2019", 131, 239, "range"),
        ("Stock estimado en situación\nirregular, inicio 2025", 614, 838, "range"),
        ("Cuentas de pago básicas,\nfin 2023", 64.489, 64.489, "bar"),
        ("Cuentas de pago básicas,\nfin 2024 (sin reclasificación)", 82.903, 82.903, "bar"),
    ]
    y = np.arange(len(rows))[::-1]
    for yi, (lab, lo, hi, kind) in zip(y, rows):
        if kind == "range":
            a.barh(yi, hi - lo, left=lo, height=0.5, color=LIGHT_ORANGE, edgecolor=ORANGE, linewidth=1)
            a.text(hi + 12, yi, f"{es(lo,0)}–{es(hi,0)} mil", va="center", fontsize=7.8, color=INK)
        else:
            a.barh(yi, hi, height=0.5, color=BLUE)
            a.text(hi + 12, yi, f"{es(hi*1000,0)}", va="center", fontsize=7.8, color=INK)
    a.set_yticks(y, [r[0] for r in rows], fontsize=7.6)
    a.set_xlim(0, 1000)
    a.set_xlabel("miles")
    a.xaxis.grid(True, color=GRID, linewidth=0.5); a.set_axisbelow(True)
    a.tick_params(axis="y", length=0)
    a.set_title("a) Población potencial frente a cuentas", loc="left", fontsize=8.8, color=INK, fontweight="bold")
    a.legend(handles=[Patch(facecolor=LIGHT_ORANGE, edgecolor=ORANGE, label="Rango estimado (Funcas)"),
                      Patch(facecolor=BLUE, label="Cuentas registradas")],
             fontsize=7, frameon=False, loc="lower right", bbox_to_anchor=(1.0, 0.0))

    # (b) cobertura
    xs = [0, 1, 2.2]
    labels = ["Fin 2022", "Fin 2023", "Inicio 2025"]
    b.plot(xs[:2], [7.8, 8.6], color=BLUE, linewidth=2, zorder=2)
    b.plot([xs[1], xs[2]], [8.6, 11], color=BLUE, linewidth=2, linestyle=(0, (3, 2)), zorder=2)
    b.vlines(xs[2], 10, 12, color=BLUE, linewidth=6, alpha=0.35, zorder=1)
    b.scatter(xs[:2], [7.8, 8.6], s=38, color=BLUE, edgecolor=SURF, linewidth=1.5, zorder=3)
    b.scatter([xs[2]], [11], s=38, color=BLUE, edgecolor=SURF, linewidth=1.5, zorder=3)
    b.text(xs[0], 8.3, "7,8 %", ha="center", va="bottom", fontsize=7.4, color=INK)
    b.text(xs[1] - 0.05, 9.1, "8,6 %", ha="right", va="bottom", fontsize=7.4, color=INK)
    b.text(xs[2] - 0.15, 11.0, "10–12 %", ha="right", va="center", fontsize=7.8, color=INK)
    b.set_xticks(xs, labels, fontsize=7.6)
    b.set_ylim(0, 14); b.set_xlim(-0.7, 2.6)
    b.set_ylabel("% con cuenta de pago básica")
    b.yaxis.grid(True, color=GRID, linewidth=0.5); b.set_axisbelow(True)
    b.set_title("b) Cobertura estimada", loc="left", fontsize=8.8, color=INK, fontweight="bold")
    finish(fig, "fig2_brecha_cpb_espana",
           "Fuente: elaboración propia con Banco de España (2026), Informe de Inclusión Financiera 2025, pp. 48-50 y nota 18, y estimaciones de Funcas (2026) allí citadas.\n"
           "Las estimaciones de población no incluyen a solicitantes de asilo. La cobertura excluye la reclasificación de unas 340.000 cuentas sociales en 2024.")


# ---------------------------------------------------------------- Figura 2
def fig2():
    d = pd.read_csv(DATA / "bde_cuadro31_ecf2021.csv")
    pick = [("Cuenta corriente", "Cuenta corriente"),
            ("Tarjeta de crédito", "Tarjeta de crédito"),
            ("Hipoteca", "Hipoteca"),
            ("Ha ahorrado formalmente (b)", "Ahorro en vehículos formales¹"),
            ("Crédito informal (c)", "Recurre a crédito informal²"),
            ("% de rechazados (crédito últimos 2 años)", "Le rechazaron un crédito³"),
            ("% que no lo solicita por temor a rechazo", "No lo pide por temor al rechazo³")]
    d = d.set_index("indicador").loc[[p[0] for p in pick]]
    fig, (a, b) = plt.subplots(2, 1, figsize=(W, 3.9), gridspec_kw=dict(height_ratios=[5, 2], hspace=0.55))
    for ax, sl, xmax, title in [(a, slice(0, 5), 100, "Tenencia de productos, ahorro y financiación (%)"),
                                (b, slice(5, 7), 16, "Acceso al crédito en los dos últimos años (%)")]:
        sub = d.iloc[sl]
        labs = [p[1] for p in pick][sl]
        y = np.arange(len(sub))[::-1]
        for yi, (_, r) in zip(y, sub.iterrows()):
            ax.plot([r.nativo_total, r.inmigrante_total], [yi, yi], color=NEUTRAL, linewidth=3, zorder=1, solid_capstyle="round")
        ax.scatter(sub.nativo_total, y, s=40, color=BLUE, marker="o", edgecolor=SURF, linewidth=1.2, zorder=3, label="Nacidos en España")
        ax.scatter(sub.inmigrante_total, y, s=40, color=ORANGE, marker="s", edgecolor=SURF, linewidth=1.2, zorder=3, label="Nacidos fuera de España")
        for yi, (_, r) in zip(y, sub.iterrows()):
            gap, adj = abs(r.dif_total_pp), abs(r.dif_comparable_pp)
            ax.text(1.02, yi, f"{es(gap)} pp  ({es(adj)})", transform=ax.get_yaxis_transform(),
                    va="center", fontsize=7.4, color=INK)
        ax.set_yticks(y, labs, fontsize=7.6)
        ax.set_xlim(0, xmax)
        ax.xaxis.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)
        ax.tick_params(axis="y", length=0)
        ax.set_title(title, loc="left", fontsize=8.6, color=INK, fontweight="bold")
    a.text(1.02, 1.06, "Brecha  (comparable⁴)", transform=a.transAxes, fontsize=7.2, color=INK2, ha="left")
    a.legend(frameon=False, fontsize=7.4, loc="lower center", bbox_to_anchor=(0.45, 1.08), ncol=2, handletextpad=0.3)
    finish(fig, "fig1_nativos_inmigrantes",
           "Fuente: elaboración propia con Banco de España (2026), cuadro 3.1, a partir de la Encuesta de Competencias Financieras 2021.\n"
           "¹ Entre quienes ahorraron en los últimos 12 meses. ² Entre hogares con gastos superiores a ingresos. ³ Últimos dos años.\n"
           "⁴ Población comparable: menores de 45 años con renta del hogar inferior a 27.000 € anuales. Asociaciones descriptivas; no prueban discriminación.")


# ---------------------------------------------------------------- Figura D.1 del anexo D del ensayo (México); función fig3 por compatibilidad
def fig3():
    udi_2026 = 8.830224
    cap24, cap26 = 24390, 3000 * udi_2026
    mean24 = 65_000_000 / 5500
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.6), gridspec_kw=dict(width_ratios=[2.1, 1], wspace=0.35))
    y = [1, 0]
    a.barh(y, [cap24, cap26], height=0.52, color=NEUTRAL, zorder=1)
    a.barh(1, mean24, height=0.52, color=BLUE, zorder=2)
    a.barh(0, 14000 - 2000, left=2000, height=0.52, color=LIGHT_BLUE, edgecolor=BLUE, linewidth=1, zorder=2)
    a.text(mean24 / 2, 1, f"≈ {es(mean24,0)}\n(48 % del tope)", ha="center", va="center", fontsize=7.3, color="white", fontweight="bold")
    a.text(8000, 0, "rango de abonos\n2.000–14.000", ha="center", va="center", fontsize=7.3, color=INK)
    a.text(cap24 + 300, 1, f"tope N2\n{es(cap24,0)}", va="center", fontsize=7.3, color=INK2)
    a.text(cap26 + 300, 0, f"tope N2\n≈ {es(cap26,0)}", va="center", fontsize=7.3, color=INK2)
    a.set_yticks(y, ["Julio 2024", "Julio 2026"], fontsize=7.8)
    a.set_xlim(0, 31000); a.set_xlabel("pesos mexicanos al mes")
    a.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: es(v, 0)))
    a.xaxis.grid(True, color=GRID, linewidth=0.5); a.set_axisbelow(True); a.tick_params(axis="y", length=0)
    a.set_title("a) Abonos mensuales frente al tope N2", loc="left", fontsize=8.6, fontweight="bold")

    b.bar([0, 1], [5500, 12000], width=0.55, color=BLUE)
    for x, v, t in [(0, 5500, "5.500"), (1, 12000, "> 12.000")]:
        b.text(x, v + 300, t, ha="center", va="bottom", fontsize=7.6, color=INK)
    b.set_xticks([0, 1], ["Activas\njul. 2024", "Abiertas\n2022-2025"], fontsize=7.6)
    b.set_ylim(0, 14500); b.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: es(v, 0)))
    b.yaxis.grid(True, color=GRID, linewidth=0.5); b.set_axisbelow(True)
    b.set_title("b) Cuentas activas y abiertas", loc="left", fontsize=8.6, fontweight="bold")
    finish(fig, "figD1_mexico_uso_vs_tope",
           "Fuente: elaboración propia con Banorte (31 jul. 2024; 10 jul. 2026), El Universal (jul. 2026) y valor de la UDI publicado en el DOF (28/09/2026).\n"
           "El abono medio de 2024 divide 65 millones de pesos mensuales en salarios entre 5.500 cuentas y supone un reparto homogéneo. Datos declarados por la entidad; no es una evaluación independiente.")


# ---------------------------------------------------------------- Figura 3 del ensayo (simulación); función fig4 por compatibilidad
def fig4():
    res = pd.read_csv(DATA / "simulacion_resultados_por_semilla.csv")
    g = res.groupby("r_b")
    m, lo, hi = g.mean(), g.quantile(0.025), g.quantile(0.975)
    x = m.index.values
    fig, ax = plt.subplots(figsize=(W, 3.2))
    fig.subplots_adjust(left=0.1, right=0.98)
    ax.fill_between(x, m.ratio_access, m.ratio_tpr_eval, color=LIGHT_ORANGE, alpha=0.45, linewidth=0, zorder=0)
    ax.axhline(0.8, color=MUTED, linewidth=0.8, linestyle=(0, (2, 2)), zorder=1)
    ax.text(0.405, 0.815, "referencia 4/5", fontsize=7, color=INK2, va="bottom")
    for col, c, mk, lab in [("ratio_tpr_eval", BLUE, "o", "Vista de auditoría del modelo: solventes evaluados que obtienen crédito, B/A"),
                            ("ratio_access", ORANGE, "s", "Vista de población completa: solventes que obtienen crédito, B/A")]:
        ax.fill_between(x, lo[col], hi[col], color=c, alpha=0.18, linewidth=0, zorder=1)
        ax.plot(x, m[col], color=c, linewidth=2, zorder=2)
        ax.scatter(x, m[col], s=22, color=c, marker=mk, edgecolor=SURF, linewidth=1, zorder=3, label=lab)
    ax.text(0.52, 0.9, "Exclusión que la auditoría\ndel modelo no observa", fontsize=7.8, color=INK, ha="center", va="center")
    ax.set_xlim(0.38, 0.99); ax.set_ylim(0.35, 1.12)
    ax.set_xlabel("Tasa de éxito del alta (KYC) del grupo B, con documentación no estándar (grupo A: 0,97)")
    ax.set_ylabel("Cociente B/A")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: es(v, 2)))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: es(v, 1)))
    ax.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=7.3, loc="lower right")
    finish(fig, "fig3_simulacion_evaluabilidad",
           "Fuente: simulación propia (200.000 personas por escenario, 20 semillas; bandas = dispersión entre semillas, percentiles 2,5 y 97,5). Ambos grupos tienen idéntica distribución de solvencia.\n"
           "Simulación ilustrativa del mecanismo, no estimación empírica. Código, datos y supuestos en el repositorio del trabajo.")


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4()
    import json
    json.dump(SOURCES, open(FIG / "fuentes_figuras.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(sorted(p.name for p in FIG.glob("*.png")))

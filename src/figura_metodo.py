"""Figura 6 del ensayo: esquema del método de evaluabilidad (etapas, ecuaciones, regla de señal y controles)."""
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = pathlib.Path(__file__).resolve().parents[1]
NAVY, BLUE, INK, INK2, LINE, SOFT, PALE = "#0a2240", "#2a78d6", "#101828", "#475467", "#98a2b3", "#f2f5f9", "#e8eff7"
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavuserif", "font.size": 9})
fig, ax = plt.subplots(figsize=(10.5, 6.4)); ax.set_xlim(0, 104); ax.set_ylim(0, 64); ax.axis("off")

def caja(x, y, w, h, fc, ec, lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=1.2", fc=fc, ec=ec, lw=lw))

def flecha(x0, x1, y):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>", mutation_scale=12, color=INK2, lw=1.1))

# población en cada punto del proceso
pobl = [(1, "Intentos\nde alta", r"$n$"), (28, "Con\ncuenta", r"$a$"), (55, "Evaluados\npor el modelo", r"$e$"), (82, "Obtienen\ncrédito", r"$c$")]
for x, t, s in pobl:
    caja(x, 50, 20, 9.5, "white", LINE)
    ax.text(x + 10, 56.5, t, ha="center", va="center", fontsize=8.5, color=INK, linespacing=1.1)
    ax.text(x + 10, 51.6, s, ha="center", va="center", fontsize=12, color=NAVY)
for x0, x1 in ((21.6, 27.4), (48.6, 54.4), (75.6, 81.4)):
    flecha(x0, x1, 54.8)

# etapas y ecuaciones
etapas = [(12.5, "1 · Alta", r"$R_{\mathrm{alta}}=\dfrac{a_p/n_p}{a_r/n_r}$", "¿Consigue la cuenta?"),
          (39.5, "2 · Llegada al modelo", r"$R_{\mathrm{modelo}}=\dfrac{e_p/a_p}{e_r/a_r}$", "Con cuenta, ¿es evaluado?"),
          (66.5, "3 · Decisión", r"$R_{\mathrm{decisión}}=\dfrac{c_p/e_p}{c_r/e_r}$", "Evaluados: ¿misma aprobación?")]
for x, t, eq, q in etapas:
    caja(x - 1, 30.5, 24, 16.5, PALE, BLUE, 1.3)
    ax.text(x + 11, 44.6, t, ha="center", va="center", fontsize=9, fontweight="bold", color=NAVY)
    ax.text(x + 11, 38.2, eq, ha="center", va="center", fontsize=12.5, color=INK)
    ax.text(x + 11, 32.3, q, ha="center", va="center", fontsize=7.4, color=INK2, style="italic")
# controles que ven cada etapa
ctrl = [(12.5, "Gobernanza del no acceso", "RDL 19/2017, art. 5 · EBA/GL/2023/04\nDirectiva 2014/92/UE, arts. 15-16"),
        (39.5, "Gobernanza de datos", "Reglamento de IA, arts. 10 y 26.4\nRGPD, arts. 5.1.c y 25"),
        (66.5, "Auditoría de equidad del modelo", "Reglamento de IA, art. 9\nRGPD, art. 22")]
for x, t, s in ctrl:
    ax.text(x + 11, 26.6, t, ha="center", va="center", fontsize=8.2, fontweight="bold", color=INK)
    ax.text(x + 11, 22.9, s, ha="center", va="center", fontsize=7, color=INK2, linespacing=1.25)
# llave: lo que ve la auditoría habitual
ax.plot([66, 66, 89.5, 89.5], [19.6, 18.8, 18.8, 19.6], color=BLUE, lw=1.2)
ax.text(77.7, 17.3, "Única etapa que observa la auditoría habitual del modelo", ha="center", va="center", fontsize=7.4, color=BLUE)
ax.plot([11.5, 11.5, 62.5, 62.5], [19.6, 18.8, 18.8, 19.6], color="#c2410c", lw=1.2)
ax.text(37, 17.3, "Pérdidas previas: invisibles para la auditoría del modelo", ha="center", va="center", fontsize=7.4, color="#c2410c")

# banda inferior: regla de señal e intervalo
caja(1, 1.5, 102, 12.3, SOFT, LINE)
ax.text(3, 11.3, "Regla de señal", fontsize=8.5, fontweight="bold", color=NAVY, va="center")
ax.text(3, 7.6, r"«Señal clara» si  $R<0{,}80$,  $\mathrm{IC}^{sup}_{95\%}<1$  y  $n\geq 100$", fontsize=10, color=INK, va="center")
ax.text(3, 3.8, "«A confirmar» si R < 0,80 sin cumplir las otras dos condiciones", fontsize=7.6, color=INK2, va="center")
ax.text(52, 11.3, "Intervalo de confianza (Katz)", fontsize=8.5, fontweight="bold", color=NAVY, va="center")
ax.text(52, 7.2, r"$\exp\!\left(\ln R \pm 1{,}96\,\sqrt{\frac{1}{x_p}-\frac{1}{m_p}+\frac{1}{x_r}-\frac{1}{m_r}}\right)$", fontsize=10.5, color=INK, va="center")
ax.text(52, 3.3, "x: éxitos y m: base de la etapa; p: perfil de entrada; r: referencia.\nVistas acumuladas: evaluabilidad e/n y acceso efectivo c/n.",
        fontsize=7, color=INK2, va="center", linespacing=1.3)
fig.savefig(ROOT / "figures/fig6_metodo.png", dpi=220, bbox_inches="tight", pad_inches=0.08, facecolor="white")
print("ok")

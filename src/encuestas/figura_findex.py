"""Figura 5 del ensayo: acceso a una cuenta según la condición de entrada (Global Findex 2025)."""
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[2]
INK, INK2, GRID, AZUL = "#101828", "#475467", "#eaecf0", "#2a78d6"
f2 = lambda v: f"{v:.2f}".replace(".", ",")
t = pd.read_csv(RAIZ / "data/encuestas/findex2025_condiciones.csv")
orden = ["sin_documento", "sin_telefono", "sin_internet", "telefono_basico"]
t = t.set_index("condicion").loc[orden[::-1]].reset_index()
ET = {"sin_documento": "Sin documento de identidad\nfrente a con documento",
      "sin_telefono": "Sin teléfono móvil\nfrente a con smartphone",
      "sin_internet": "Sin uso de internet\nfrente a con uso",
      "telefono_basico": "Sólo teléfono básico\nfrente a con smartphone"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.spines.left": False, "axes.edgecolor": "#98a2b3"})
fig, ax = plt.subplots(figsize=(9.2, 4.4))
for yi, (_, r) in enumerate(t.iterrows()):
    ax.plot([r.ic_inf, r.ic_sup], [yi + .14] * 2, color=AZUL, lw=2, solid_capstyle="round")
    ax.plot(r.cociente, yi + .14, "o", ms=7, color=AZUL, mec="white", mew=1.3, zorder=3)
    ax.plot([r.ic_inf_aj, r.ic_sup_aj], [yi - .16] * 2, color=AZUL, lw=1.2, alpha=.55, solid_capstyle="round")
    ax.plot(r.cociente_ajustado, yi - .16, "D", ms=6, mfc="white", mec=AZUL, mew=1.6, zorder=3)
    ax.text(r.ic_sup + .02, yi + .14, f2(r.cociente), va="center", fontsize=8, color=INK)
    ax.text(r.ic_sup_aj + .02, yi - .16, f2(r.cociente_ajustado), va="center", fontsize=7.5, color=INK2)
    ax.text(1.345, yi, f"{r.cuenta_condicion*100:.0f} % frente a {r.cuenta_referencia*100:.0f} %\n{int(r.economias)} economías".replace(".", ","),
            va="center", ha="right", fontsize=7.5, color=INK2)
ax.axvline(1, color="#d0d5dd", lw=.9); ax.axvline(.8, color=INK2, lw=.9, ls=(0, (2, 2)))
ax.set_yticks(range(len(t)), [ET[k] for k in t.condicion], fontsize=8.5, color=INK); ax.tick_params(axis="y", length=0)
ax.set_xlim(.3, 1.35)
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.1f}".replace(".", ",")))
ax.set_xticks([.4, .5, .6, .7, .8, .9, 1.0])
ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
ax.set_xlabel("Cuenta en una entidad financiera: cociente frente a la referencia (1 = igualdad)", color=INK2, fontsize=8.5)
h = [plt.Line2D([], [], marker="o", ls="-", color=AZUL, ms=7, mec="white", label="Descriptivo (IC 95 %)"),
     plt.Line2D([], [], marker="D", ls="-", color=AZUL, mfc="white", mec=AZUL, lw=1.2, ms=6,
                label="Ajustado por economía, sexo, edad, educación, ingreso, empleo y ruralidad"),
     plt.Line2D([], [], color=INK2, lw=.9, ls=(0, (2, 2)), label="Umbral de revisión (0,80)")]
fig.legend(handles=h, loc="lower center", ncol=1, frameon=False, fontsize=8, bbox_to_anchor=(.5, -.01))
fig.tight_layout(rect=(0, .15, 1, 1))
out = RAIZ / "figures/fig5_findex_condiciones.png"; fig.savefig(out, dpi=220, facecolor="white"); print(out)

"""Figura 8 del ensayo: acceso a cuenta sin documento de identidad frente a con documento (Global Findex 2025)."""
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[2]
INK, INK2, GRID, AZUL = "#101828", "#475467", "#eaecf0", "#2a78d6"
REG = {"Todas las economías con la pregunta": "Total (economías con la pregunta)",
       "Sub-Saharan Africa (excluding high income)": "África subsahariana",
       "South Asia": "Asia meridional",
       "East Asia & Pacific (excluding high income)": "Asia oriental y Pacífico",
       "Europe & Central Asia (excluding high income)": "Europa y Asia central",
       "Latin America & Caribbean (excluding high income)": "América Latina y Caribe",
       "Middle East & North Africa (excluding high income)": "Oriente Medio y Norte de África",
       "High income": "Economías de ingreso alto"}
f2 = lambda v: f"{v:.2f}".replace(".", ",")

a = pd.read_csv(RAIZ / "data/encuestas/findex2025_documento_agregado.csv")
j = pd.read_csv(RAIZ / "data/encuestas/findex2025_documento_ajustado.csv")
d = a.merge(j[["ambito", "cociente_ajustado", "ic_inf", "ic_sup"]], on="ambito", suffixes=("", "_aj"))
tot = d[d.ambito.str.startswith("Todas")]
reg = d[~d.ambito.str.startswith("Todas")].sort_values("cociente_cuenta", ascending=False)
d = pd.concat([reg, tot])
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.spines.left": False, "axes.edgecolor": "#98a2b3"})
fig, ax = plt.subplots(figsize=(9.2, 5.0))
y = list(range(len(d)))
y[-1] = len(d) - 1 + 0.6
for yi, (_, r) in zip(y, d.iterrows()):
    ax.plot([r.ic_inf, r.ic_sup], [yi + 0.14] * 2, color=AZUL, lw=2, solid_capstyle="round")
    ax.plot(r.cociente_cuenta, yi + 0.14, "o", ms=7, color=AZUL, mec="white", mew=1.3, zorder=3)
    ax.plot([r.ic_inf_aj, r.ic_sup_aj], [yi - 0.16] * 2, color=AZUL, lw=1.2, alpha=.55, solid_capstyle="round")
    ax.plot(r.cociente_ajustado, yi - 0.16, "D", ms=6, mfc="white", mec=AZUL, mew=1.6, zorder=3)
    ax.text(max(r.ic_sup, r.cociente_cuenta) + 0.025, yi + 0.14, f2(r.cociente_cuenta), va="center", fontsize=8, color=INK)
    ax.text(max(r.ic_sup_aj, r.cociente_ajustado) + 0.025, yi - 0.16, f2(r.cociente_ajustado), va="center", fontsize=7.5, color=INK2)
ax.axvline(1, color="#d0d5dd", lw=0.9)
ax.axvline(0.8, color=INK2, lw=0.9, ls=(0, (2, 2)))
ax.axhline(len(d) - 1.7 + 0.6, color="#d0d5dd", lw=0.6)
et = [f"{REG[r.ambito]}  (n = {r.n_sin_documento:,})".replace(",", ".") for _, r in d.iterrows()]
ax.set_yticks(y, et, fontsize=8.5, color=INK)
ax.get_yticklabels()[-1].set_fontweight("bold")
ax.tick_params(axis="y", length=0)
ax.set_xlim(0, 1.32)
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.1f}".replace(".", ",")))
ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
ax.set_xlabel("Cuenta en una entidad financiera: cociente sin documento / con documento de identidad (1 = igualdad)", color=INK2, fontsize=8.5)
h = [plt.Line2D([], [], marker="o", ls="-", color=AZUL, ms=7, mec="white", label="Descriptivo (cálculo del kit, IC 95 %)"),
     plt.Line2D([], [], marker="D", ls="-", color=AZUL, alpha=1, mfc="white", mec=AZUL, lw=1.2, ms=6,
                label="Ajustado por economía, sexo, edad, educación, ingreso, empleo y ruralidad"),
     plt.Line2D([], [], color=INK2, lw=0.9, ls=(0, (2, 2)), label="Umbral de revisión (0,80)")]
fig.legend(handles=h, loc="lower center", ncol=1, frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.01))
fig.tight_layout(rect=(0, 0.15, 0.98, 1))
out = RAIZ / "figures/fig8_findex_documento.png"
fig.savefig(out, dpi=220, facecolor="white")
print(out)

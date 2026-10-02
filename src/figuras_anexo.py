"""Figuras del anexo C (resultados estadísticos complementarios) a partir de los agregados de Global Findex 2025.
python src/figuras_anexo.py   (requiere haber ejecutado antes src/encuestas/findex_*.py)
Usa la misma paleta y tipografía que src/figuras.py para que todas las figuras del ensayo sean coherentes.
"""
import pathlib
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from figuras import (BLUE, ORANGE, INK, INK2, MUTED, GRID, LIGHT_BLUE, LIGHT_ORANGE, NEUTRAL, W, es)  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENC, FIG = ROOT / "data" / "encuestas", ROOT / "figures"


def save(fig, name):
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


# ------------------------------------------------------------ Figura C.1: un punto por economía
def fig_c1():
    t = pd.read_csv(ENC / "findex2025_documento_por_economia.csv")
    t = t[t.n_sin_documento >= 30].copy()
    fig, ax = plt.subplots(figsize=(W, 4.6))
    x = np.linspace(0, 1, 50)
    ax.plot(x, x, color=MUTED, lw=0.8, ls="--", zorder=1)
    ax.plot(x, 0.8 * x, color=MUTED, lw=0.8, ls=":", zorder=1)
    ax.text(0.60, 0.635, "igualdad (cociente 1)", fontsize=7.2, color=INK2, ha="center", va="bottom", rotation=34)
    ax.text(0.80, 0.615, "umbral de revisión (cociente 0,80)", fontsize=7.2, color=INK2, ha="center", va="top", rotation=28)
    estilo = {"Señal clara": dict(fc=ORANGE, ec="white"), "A confirmar": dict(fc=LIGHT_ORANGE, ec=ORANGE),
              "Sin señal": dict(fc=LIGHT_BLUE, ec=BLUE)}
    for s, st in estilo.items():
        d = t[t.senal == s]
        ax.scatter(d.cuenta_con_documento, d.cuenta_sin_documento, s=12 + d.n_sin_documento / 4, facecolor=st["fc"],
                   edgecolor=st["ec"], linewidth=0.8, zorder=3)
    # etiquetas selectivas: los cocientes más bajos con señal clara y las economías de ingreso alto con más casos
    # etiquetas selectivas, con desplazamientos fijos para evitar solapes: cocientes más bajos con señal clara
    lab = t[t.senal == "Señal clara"].nsmallest(6, "cociente_cuenta").sort_values("cuenta_con_documento")
    offs = [(-14, -14), (8, -12), (6, 8), (8, -12), (6, 8), (8, -4)]
    for (_, r), o in zip(lab.iterrows(), offs):
        ax.annotate(r.codigo, (r.cuenta_con_documento, r.cuenta_sin_documento), xytext=o,
                    textcoords="offset points", fontsize=7, color=INK,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5, shrinkA=0, shrinkB=3))
    ax.annotate("Economías de ingreso alto:\ncasi todos tienen cuenta,\ncon o sin documento", (0.97, 0.93),
                xytext=(0.66, 0.84), fontsize=7.2, color=INK2, ha="center",
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5))
    ax.set_xlim(0, 1.02); ax.set_ylim(0, 1.02)
    ax.set_xticks(np.arange(0, 1.01, 0.2)); ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_xticklabels([f"{int(v*100)} %" for v in np.arange(0, 1.01, 0.2)])
    ax.set_yticklabels([f"{int(v*100)} %" for v in np.arange(0, 1.01, 0.2)])
    ax.set_xlabel("Con cuenta, adultos con documento de identidad")
    ax.set_ylabel("Con cuenta, adultos sin documento")
    ax.grid(color=GRID, lw=0.5); ax.set_axisbelow(True)
    h = [Line2D([], [], marker="o", ls="", markerfacecolor=st["fc"], markeredgecolor=st["ec"], markersize=7, label=s)
         for s, st in estilo.items()]
    h.append(Line2D([], [], marker="o", ls="", markerfacecolor="none", markeredgecolor=MUTED, markersize=4,
                    label="Tamaño: adultos sin documento"))
    ax.legend(handles=h, loc="upper left", frameon=False, fontsize=7.5)
    save(fig, "figC1_findex_economias")
    return len(t), int((t.senal == "Señal clara").sum()), int((t.cociente_cuenta < 0.8).sum())


# ------------------------------------------------------------ Figura C.2: descomposición de la brecha
def fig_c2():
    g = pd.read_csv(ENC / "findex2025_descomposicion.csv").set_index("condicion")
    u = pd.read_csv(ENC / "findex2025_descomposicion_ue.csv")
    u = u[(u.condicion == "sin_internet") & u.ambito.str.startswith("UE-4")].iloc[0]
    filas = [("Sin documento de identidad", g.loc["sin_documento"]), ("Sólo teléfono básico", g.loc["telefono_basico"]),
             ("Sin teléfono móvil", g.loc["sin_telefono"]), ("Sin uso de internet", g.loc["sin_internet"]),
             ("Sin uso de internet, UE-4", u)]
    fig, ax = plt.subplots(figsize=(W, 2.9))
    y = np.array([5, 4, 3, 2, 0.6])
    for yi, (lab, r) in zip(y, filas):
        ax.barh(yi, r.acceso_pp, height=0.55, color=BLUE, edgecolor="white", linewidth=1.5)
        ax.barh(yi, r.posterior_pp, left=r.acceso_pp, height=0.55, color=LIGHT_BLUE, edgecolor="white", linewidth=1.5)
        ax.text(r.brecha_pp + 0.15, yi, f"{es(r.brecha_pp)} p. p.; {es(100*r.pct_acceso,0)} % en el acceso "
                f"[{es(100*r.pct_acceso_inf,0)}-{es(100*r.pct_acceso_sup,0)}]", va="center", fontsize=7.5, color=INK)
    ax.axhline(1.3, color=GRID, lw=0.8)
    ax.text(0.05, 1.22, "Unión Europea (Bulgaria, Croacia, Polonia, Rumanía)", fontsize=7.2, color=INK2, ha="left", va="top")
    ax.set_yticks(y); ax.set_yticklabels([f[0] for f in filas])
    ax.set_xlim(0, 15); ax.set_xlabel("Brecha de crédito formal frente a la referencia (puntos porcentuales)")
    ax.legend(handles=[Patch(color=BLUE, label="Se produce en el acceso a la cuenta (antes de cualquier evaluación)"),
                       Patch(color=LIGHT_BLUE, label="Se produce entre quienes ya tienen cuenta")],
              loc="upper center", bbox_to_anchor=(0.45, -0.22), ncol=1, frameon=False, fontsize=7.5)
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    save(fig, "figC2_descomposicion")


# ------------------------------------------------------------ Figura C.3: el dinero que no se registra
def fig_c3():
    t = pd.read_csv(ENC / "findex2025_efectivo_ue4.csv")
    ind = [("ingreso_regular_solo_efectivo", "Ingreso regular sólo en efectivo\n(salario, pensión o transferencia)"),
           ("suministros_solo_efectivo", "Suministros pagados\nsólo en efectivo"),
           ("ahorro_fuera_de_entidad", "Ahorro fuera de una\nentidad financiera")]
    pares = [("Sin uso de internet", "Con uso de internet", "A. Según el uso de internet"),
             ("Sin cuenta", "Con cuenta", "B. Según la tenencia de cuenta")]
    fig, axes = plt.subplots(1, 2, figsize=(W, 2.7), sharey=True, gridspec_kw=dict(wspace=0.12))
    for ax, (gp, gr, tit) in zip(axes, pares):
        for i, (k, lab) in enumerate(ind):
            yi = len(ind) - 1 - i
            a = t[(t.grupo == gp) & (t.indicador == k)].iloc[0]
            b = t[(t.grupo == gr) & (t.indicador == k)].iloc[0]
            ax.plot([b.proporcion, a.proporcion], [yi, yi], color=NEUTRAL, lw=2, zorder=1)
            for r, c, dy in [(a, ORANGE, 0), (b, BLUE, 0)]:
                ax.errorbar(r.proporcion, yi + dy, xerr=[[r.proporcion - r.ic_inf], [r.ic_sup - r.proporcion]],
                            fmt="o", color=c, ms=6.5, mec="white", mew=1, elinewidth=1, capsize=0, zorder=3)
            ax.text(a.proporcion, yi + 0.22, f"{es(100*a.proporcion,0)} %", ha="center", fontsize=7.2, color=INK)
            ax.text(b.proporcion, yi + 0.22, f"{es(100*b.proporcion,0)} %", ha="center", fontsize=7.2, color=INK)
        ax.set_title(tit, fontsize=8.2, color=INK, loc="left")
        ax.set_xlim(0, 1.05); ax.set_xticks([0, .25, .5, .75, 1]); ax.set_xticklabels(["0", "25", "50", "75", "100 %"])
        ax.grid(axis="x", color=GRID, lw=0.5); ax.set_axisbelow(True)
        ax.set_ylim(-0.6, len(ind) - 0.3)
        ax.legend(handles=[Line2D([], [], marker="o", ls="", color=ORANGE, label=gp),
                           Line2D([], [], marker="o", ls="", color=BLUE, label=gr)],
                  loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False, fontsize=7.5)
    axes[0].set_yticks(range(len(ind))); axes[0].set_yticklabels([l for _, l in ind][::-1])
    axes[0].tick_params(axis="y", length=0)
    save(fig, "figC3_efectivo_ue4")


if __name__ == "__main__":
    print(fig_c1()); fig_c2(); fig_c3()

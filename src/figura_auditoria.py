"""Figura 4: revisión documental de la información pública de 15 entidades, en agregado (datos anonimizados en auditoria/).

Se muestra cuántas entidades cumplen cada indicador, sin identificar a ninguna. El detalle codificado por
entidad (con códigos anónimos) sigue disponible en auditoria/auditoria_cpb_codificacion.csv para su réplica."""
import pathlib
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
d = pd.read_csv(ROOT / "auditoria" / "auditoria_cpb_codificacion.csv")
BLUE, ORANGE, NEUTRAL, INK, INK2 = "#2a78d6", "#eb6834", "#e4e7ec", "#101828", "#475467"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "savefig.dpi": 300})
cols = [("I2_menciona_asilo", "Nombra a los solicitantes de asilo"),
        ("I10_gratuidad_vulnerables", "Informa de la gratuidad para personas vulnerables"),
        ("I9_via_reclamacion", "Informa de la vía de reclamación"),
        ("I3_lista_documentos_cpb", "Publica los documentos que admite"),
        ("I4_admite_doc_proteccion", "Admite el documento de protección internacional"),
        ("I7_formulario_publico", "Tiene un formulario de solicitud público"),
        ("I8_denegacion_por_escrito", "Informa de que la negativa será por escrito"),
        ("I6_alta_digital_admite_doc_proteccion", "Su alta digital admite ese documento")]
fig, ax = plt.subplots(figsize=(8.6, 4.2))
for i, (c, lab) in enumerate(cols):
    y = len(cols) - 1 - i
    si, no = (d[c] == "Sí").sum(), (d[c] == "No").sum(); nc = len(d) - si - no
    x = 0
    for v, col in ((si, BLUE), (no, ORANGE), (nc, NEUTRAL)):
        if v:
            ax.barh(y, v, left=x, height=.62, color=col, edgecolor="white", linewidth=2)
            ax.text(x + v / 2, y, str(v), ha="center", va="center", fontsize=8.5,
                    color="white" if col != NEUTRAL else INK2, fontweight="bold")
        x += v
ax.set_yticks(range(len(cols)), [lab for _, lab in cols][::-1], fontsize=9, color=INK)
ax.set_xlim(0, 15); ax.set_xticks([0, 5, 10, 15]); ax.tick_params(axis="y", length=0)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#98a2b3")
ax.set_xlabel("Número de entidades (de 15)", color=INK2)
ax.legend(handles=[Patch(facecolor=BLUE, label="Sí (con cita pública)"), Patch(facecolor=ORANGE, label="No (la información publicada lo excluye)"),
                   Patch(facecolor=NEUTRAL, label="No consta en la información pública")],
          loc="upper center", bbox_to_anchor=(0.4, -0.16), ncol=3, frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(ROOT / "figures" / "fig4_auditoria_entidades.png", bbox_inches="tight", pad_inches=0.08, facecolor="white")
print("ok")

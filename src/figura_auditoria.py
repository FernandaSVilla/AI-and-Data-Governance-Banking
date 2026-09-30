"""Figura 5: matriz de la auditoría documental de 15 entidades (datos en auditoria/)."""
import pathlib
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
d = pd.read_csv(ROOT / "auditoria" / "auditoria_cpb_codificacion.csv")
BLUE, ORANGE, NEUTRAL, INK, INK2, SURF = "#2a78d6", "#eb6834", "#e9e8e4", "#0b0b0b", "#52514e", "#ffffff"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "savefig.dpi": 300})

cols = [("I2_menciona_asilo", "Nombra a solicitantes de asilo"),
        ("I3_lista_documentos_cpb", "Publica los documentos admitidos"),
        ("I4_admite_doc_proteccion", "Admite doc. de protección internacional"),
        ("I6_alta_digital_admite_doc_proteccion", "Su alta digital admite ese documento"),
        ("I7_formulario_publico", "Formulario de solicitud público"),
        ("I8_denegacion_por_escrito", "Informa de negativa por escrito"),
        ("I9_via_reclamacion", "Informa de la vía de reclamación"),
        ("I10_gratuidad_vulnerables", "Informa de gratuidad (vulnerables)")]
score = sum((d[c] == "Sí").astype(int) for c, _ in cols)
d = d.assign(score=score).sort_values(["score", "codigo"], ascending=[False, True]).reset_index(drop=True)

n, m = len(d), len(cols)
fig, ax = plt.subplots(figsize=(6.5, 6.6))
style = {"Sí": (BLUE, "✓", "white"), "No": (ORANGE, "✗", "white"), "No consta": (NEUTRAL, "–", INK2)}
for i, row in d.iterrows():
    y = n - 1 - i
    for j, (c, _) in enumerate(cols):
        fc, sym, tc = style[row[c]]
        ax.add_patch(Rectangle((j + 0.04, y + 0.06), 0.92, 0.88, facecolor=fc, edgecolor=SURF, linewidth=0))
        ax.text(j + 0.5, y + 0.5, sym, ha="center", va="center", fontsize=9, color=tc, fontweight="bold")
    ch = row["I5_canal_contratacion_cpb"]
    ax.text(m + 0.15, y + 0.5, ch, ha="left", va="center", fontsize=7.4, color=INK)
    ax.text(-0.15, y + 0.5, row["codigo"], ha="right", va="center", fontsize=8, color=INK)
# totales
for j, (c, lab) in enumerate(cols):
    k = (d[c] == "Sí").sum()
    ax.text(j + 0.35, n + 0.15, lab, ha="left", va="bottom", fontsize=7.2, color=INK, rotation=50, rotation_mode="anchor")
    ax.text(j + 0.5, -0.45, f"{k}/15", ha="center", va="center", fontsize=7.6, color=INK, fontweight="bold")
ax.text(m + 0.15, n + 0.15, "Canal para contratar la CPB", ha="left", va="bottom", fontsize=7.2, color=INK, rotation=50, rotation_mode="anchor")
ax.text(-0.15, -0.45, "Entidades con «Sí»", ha="right", va="center", fontsize=7.4, color=INK2)
ax.set_xlim(-2.6, m + 3.4); ax.set_ylim(-0.9, n + 4.2)
ax.axis("off")
ax.legend(handles=[Patch(facecolor=BLUE, label="Sí (con cita pública)"), Patch(facecolor=ORANGE, label="No (la lista publicada lo excluye)"),
                   Patch(facecolor=NEUTRAL, label="No consta en la información pública")],
          loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False, fontsize=7)
fig.savefig(ROOT / "figures" / "fig4_auditoria_entidades.png", bbox_inches="tight", pad_inches=0.08)
print("ok")

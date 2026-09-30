"""Figura 6 del ensayo: informe del kit «evaluabilidad» v0.3 sobre los datos sintéticos de ejemplo."""
import pathlib, sys
raiz = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(raiz / "kit")); sys.path.insert(0, str(raiz / "kit" / "demo"))
from generar_datos_demo import generar
from evaluabilidad.metricas import calcular_todo
from evaluabilidad.informe import fig_cocientes

altas, credito = generar()
r = calcular_todo(altas, credito)
fig = fig_cocientes(r["cocientes"], figsize=(11.5, 4.1))
fig.savefig(raiz / "figures" / "fig6_kit_informe_demo.png", dpi=220, bbox_inches="tight")
print(r["cocientes"].round(2).to_string())

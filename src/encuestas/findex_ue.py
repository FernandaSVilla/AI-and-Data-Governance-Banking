"""Global Findex 2025 en la Unión Europea (sección 3.4 del ensayo).

Repite el análisis de findex_condiciones.py sólo con las economías de la UE-27 incluidas en la encuesta
(26; Luxemburgo no figura). Se publican las condiciones con datos en la mayoría de esas economías:
sin documento de identidad y sin uso de internet. El módulo de conectividad (teléfono) y la pregunta sobre
necesitar ayuda sólo existen en 2-4 economías de la UE y no se usan.
Uso: python src/encuestas/findex_ue.py [ruta al .dta]  ->  data/encuestas/findex2025_ue_condiciones.csv
"""
import pathlib
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import findex_condiciones as F  # noqa: E402
from leer import leer  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parents[2]
UE = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia", "Denmark", "Estonia", "Finland", "France",
      "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands",
      "Poland", "Portugal", "Romania", "Slovak Republic", "Slovenia", "Spain", "Sweden"]


def main(ruta):
    w, _, _ = leer(ruta)
    d = F.base(w[w.economy.isin(UE)].copy())
    c = F.condiciones(d)
    filas = []
    for k in ("sin_documento", "sin_internet"):
        x = np.asarray(c[k], float)
        f = dict(condicion=k, nombre=F.NOMBRES[k], referencia=F.REFS[k], ambito="UE-27 (26 economías en Findex)")
        f.update(F.descriptivo(d, x)); f.update(F.ajustado(d, x))
        filas.append(f)
    out = pd.DataFrame(filas)
    out["pct_sin_internet_adultos"] = F.proporcion((d.internet_use == 0).astype(float), d.peso_pob)
    out.round(4).to_csv(RAIZ / "data/encuestas/findex2025_ue_condiciones.csv", index=False)
    print(out.round(3).to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "microdatos/wld/findex_microdata_2025_labelled_update112425.dta")

"""Escenarios anclados en la auditoría: acceso a la cuenta del perfil «documento de protección internacional».

Cociente = acceso del perfil / acceso del perfil de referencia, con
  acceso del perfil = d · a_digital + (1 − d) · a_oficina
  d          proporción de intentos que empiezan en el canal digital (supuesto, se hace variar)
  a_digital  0,05  (auditoría: 0 de 11 altas digitales publicadas admiten el documento; 5 % residual)
  a_oficina  0,33 – 0,87 (5/15 entidades publican que lo admiten; 13/15 reconocen el derecho)
  referencia 0,958 (acceso del perfil estándar en el escenario de ejemplo)
Supuesto conservador a favor de la entidad: no se modela a quien, tras fallar en digital, acude después a
una oficina y lo consigue; si ocurre, el cociente real sería algo mayor.
Uso: python src/escenarios_anclados.py -> data/escenarios_anclados.csv
"""
import pathlib
import numpy as np
import pandas as pd

raiz = pathlib.Path(__file__).resolve().parents[1]
A_DIG, REF = 0.05, 0.958
filas = []
for a_of in (5 / 15, 0.60, 13 / 15):
    for d in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
        filas.append(dict(acceso_oficina=round(a_of, 3), prop_digital=d, cociente=(d * A_DIG + (1 - d) * a_of) / REF))
df = pd.DataFrame(filas)
df.to_csv(raiz / "data" / "escenarios_anclados.csv", index=False)
print(df.pivot(index="prop_digital", columns="acceso_oficina", values="cociente").round(2).to_string())
d_umbral = (13 / 15 - 0.8 * REF) / (13 / 15 - A_DIG)
print(f"\nEn el mejor caso de oficina (0,87), el cociente cae bajo 0,80 si más del {d_umbral:.0%} de los intentos empieza en digital.")

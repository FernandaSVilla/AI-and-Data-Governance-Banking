"""¿Qué auditoría detecta qué? Comparación con verdad conocida (tabla 11 del ensayo).

Se simulan registros agregados de un perfil de entrada y del perfil de referencia en las tres etapas del proceso
(alta, llegada al modelo y decisión). En cada escenario se introduce una pérdida real en UNA etapa
(cociente 0,7 o 0,6 frente a la referencia) o en ninguna, y se comprueba qué detecta cada auditoría:

- Calidad de datos convencional (nulos, duplicados, dominios, formatos, rangos): revisa columnas, no compara
  resultados entre perfiles, por lo que no puede detectar ninguna de estas pérdidas. Aplicada a los 40.000
  intentos del ejemplo, sólo señala nulos estructurales (la causa de no acceso está vacía cuando hubo cuenta).
- Equidad del modelo: la práctica habitual, que compara la aprobación entre quienes el modelo evalúa.
- Kit: las tres vistas por etapa; se registra si detecta y si identifica la etapa correcta como primera señal.

Las reglas de señal son las del kit (umbral 0,80, IC 95 % por debajo de 1 y al menos 100 casos) y no se
ajustan durante la evaluación. Tasas de referencia tomadas del ejemplo del kit: alta 0,95; llegada al modelo 0,80;
aprobación 0,55. Perfil de referencia: 5.000 intentos.
"""
import pathlib
import sys
import numpy as np
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "kit"))
from evaluabilidad.metricas import cociente_ic, senal, UMBRAL, N_MINIMO  # noqa: E402

REPS, N_REF, SEMILLA = 2000, 5000, 2026
BASE = dict(alta=0.95, datos=0.80, decision=0.55)
ETAPAS = ["alta", "datos", "decision"]


def una(rng, n1, etapa, r):
    t = {k: BASE[k] * (r if k == etapa else 1.0) for k in ETAPAS}
    a0 = rng.binomial(N_REF, BASE["alta"]); e0 = rng.binomial(a0, BASE["datos"]); p0 = rng.binomial(e0, BASE["decision"])
    a1 = rng.binomial(n1, t["alta"]); e1 = rng.binomial(a1, t["datos"]); p1 = rng.binomial(e1, t["decision"])
    sen = {}
    for k, (x1, m1, x0, m0) in dict(alta=(a1, n1, a0, N_REF), datos=(e1, a1, e0, a0), decision=(p1, e1, p0, e0)).items():
        c, lo, hi = cociente_ic(x1, m1, x0, m0)
        sen[k] = senal(c, hi, m1, UMBRAL, N_MINIMO) == "Señal clara"
    primera = next((k for k in ETAPAS if sen[k]), None)
    return dict(modelo=sen["decision"], kit=primera is not None, kit_etapa=(primera == etapa) if etapa else primera is None)


def main():
    rng = np.random.default_rng(SEMILLA)
    filas = []
    for n1 in (300, 1000):
        for etapa in ETAPAS + [None]:
            for r in ((0.7, 0.6) if etapa else (1.0,)):
                res = pd.DataFrame([una(rng, n1, etapa, r) for _ in range(REPS)])
                filas.append(dict(intentos_perfil=n1, etapa_real=etapa or "ninguna", cociente_real=r,
                                  calidad_datos=0.0, equidad_modelo=res.modelo.mean(), kit_detecta=res.kit.mean(),
                                  kit_etapa_correcta=res.kit_etapa.mean()))
    t = pd.DataFrame(filas)
    out = RAIZ / "data" / "comparacion_auditorias.csv"
    t.round(4).to_csv(out, index=False)
    print(t.round(3).to_string(index=False))


if __name__ == "__main__":
    main()

"""Validación estadística del método del kit «evaluabilidad».

Comprueba, por simulación, tres propiedades de los cocientes que calcula la herramienta:
  1. Cobertura: ¿el intervalo de confianza del 95 % contiene el cociente real el 95 % de las veces?
  2. Potencia: si un perfil tiene de verdad un cociente bajo (0,7, 0,6…), ¿con qué frecuencia lo marca
     la herramienta como «Señal clara»?
  3. Falsas alarmas: si no hay diferencia real (cociente 1), ¿con qué frecuencia marca «Señal clara»
     o «A confirmar» por azar?

Usa exactamente las funciones del paquete (cociente_ic y senal), no una reimplementación.
Uso: python src/validacion_metodo.py  -> data/validacion_metodo.csv (tabla 12 del ensayo)
"""
import pathlib, sys
import numpy as np
import pandas as pd

raiz = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(raiz / "kit"))
from evaluabilidad.metricas import cociente_ic, senal, UMBRAL  # noqa: E402

REPS = 4000
N_REF = 5000                        # intentos del perfil de referencia (suele ser el grupo mayor)
N_PERFIL = [50, 100, 200, 300, 500, 1000, 2000]
COCIENTES = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
TASAS_REF = {"Acceso a la cuenta (tasa de referencia 0,95)": 0.95,
             "Acceso efectivo al crédito (tasa de referencia 0,40)": 0.40}


def simular(p0, r, n1, reps, rng):
    x0 = rng.binomial(N_REF, p0, reps)
    x1 = rng.binomial(n1, min(1.0, p0 * r), reps)
    cub, clara, alguna = 0, 0, 0
    for a, b in zip(x1, x0):
        c, lo, hi = cociente_ic(int(a), n1, int(b), N_REF)
        cub += lo <= r <= hi
        s = senal(c, hi, n1, UMBRAL)
        clara += s == "Señal clara"
        alguna += s in ("Señal clara", "A confirmar")
    return cub / reps, clara / reps, alguna / reps


def main():
    rng = np.random.default_rng(20260929)
    filas = []
    for vista, p0 in TASAS_REF.items():
        for r in COCIENTES:
            for n1 in N_PERFIL:
                cob, clara, alguna = simular(p0, r, n1, REPS, rng)
                filas.append(dict(vista=vista, tasa_referencia=p0, cociente_real=r, intentos_perfil=n1,
                                  cobertura_ic95=cob, prob_senal_clara=clara, prob_alguna_senal=alguna))
    df = pd.DataFrame(filas)
    df.to_csv(raiz / "data" / "validacion_metodo.csv", index=False)
    return df



if __name__ == "__main__":
    df = main()
    pd.set_option("display.width", 200)
    for vista, d in df.groupby("vista", sort=False):
        print("\n==", vista)
        print("Cobertura media del IC 95 %:", round(d.cobertura_ic95.mean(), 3), "(mín.", round(d.cobertura_ic95.min(), 3), ")")
        print(d.pivot(index="cociente_real", columns="intentos_perfil", values="prob_senal_clara").round(2).to_string())
        print("Falsas alarmas (cociente 1, alguna señal):")
        print(d[d.cociente_real == 1.0].set_index("intentos_perfil")[["prob_senal_clara", "prob_alguna_senal"]].round(3).T.to_string())

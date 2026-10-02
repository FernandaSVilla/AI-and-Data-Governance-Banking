"""El dinero que no se registra: ingresos y pagos sólo en efectivo en los Estados miembros de la UE con datos
(Global Findex 2025).

Findex 2025 sólo formula las preguntas sobre la forma de cobro y de pago en cuatro Estados miembros: Bulgaria,
Croacia, Polonia y Rumanía. Para cada grupo (todos, sin/con cuenta, sin/con uso de internet) se calcula:
  · ingreso regular sólo en efectivo: entre quienes reciben un salario, una transferencia pública o una pensión,
    proporción que no recibe ninguno de ellos en una cuenta (receive_wages, receive_transfers, receive_pensions);
  · adultos con ingreso regular sólo en efectivo, sobre todos los adultos del grupo;
  · suministros pagados sólo en efectivo, entre quienes pagan suministros (fin30, fin31d);
  · ahorro fuera de una entidad financiera, entre quienes ahorran (saved, fin17a);
  · salario sólo en efectivo, entre quienes cobran un salario (receive_wages).
Pesos reescalados a la población adulta de cada economía. Sólo agregados; celdas con < 30 observaciones suprimidas.
Asociaciones descriptivas, no efectos causales.

Uso: python src/encuestas/findex_efectivo.py [ruta al .dta]
Salida: data/encuestas/findex2025_efectivo_ue4.csv
"""
import pathlib
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from leer import leer  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parents[2]
OUT = RAIZ / "data" / "encuestas"
UE4 = ["Bulgaria", "Croatia", "Poland", "Romania"]
N_MIN = 30
Z = 1.96


def prop(num, den, w):
    """Proporción ponderada con IC 95 % (aproximación normal con tamaño efectivo de Kish)."""
    m = den.to_numpy(bool)
    n = int(m.sum())
    if n < N_MIN:
        return dict(p=np.nan, inf=np.nan, sup=np.nan, n=n)
    ww = w[m]
    x = num[m].astype(float)
    p = float((ww * x).sum() / ww.sum())
    neff = ww.sum() ** 2 / (ww ** 2).sum()
    se = np.sqrt(p * (1 - p) / neff)
    return dict(p=p, inf=max(0.0, p - Z * se), sup=min(1.0, p + Z * se), n=n)


def calcular(d):
    for v in ["receive_wages", "receive_transfers", "receive_pensions", "fin30", "fin31d", "fin17a", "saved"]:
        d[v] = pd.to_numeric(d[v], errors="coerce")
    w = (d.wgt * d.pop_adult / d.groupby("economy").wgt.transform("sum")).to_numpy()
    recibe = d.receive_wages.isin([1, 2, 3]) | d.receive_transfers.isin([1, 2, 3]) | d.receive_pensions.isin([1, 2, 3])
    en_cuenta = (d.receive_wages == 1) | (d.receive_transfers == 1) | (d.receive_pensions == 1)
    solo_efectivo = recibe & ~en_cuenta
    grupos = {"Todos": d.account_fin.notna(), "Sin cuenta": d.account_fin == 0, "Con cuenta": d.account_fin == 1,
              "Sin uso de internet": d.internet_use == 0, "Con uso de internet": d.internet_use == 1}
    filas = []
    for nombre, g in grupos.items():
        ind = {
            "ingreso_regular_solo_efectivo": prop(solo_efectivo, g & recibe, w),
            "adultos_ingreso_solo_efectivo": prop(solo_efectivo, g, w),
            "suministros_solo_efectivo": prop(d.fin31d == 1, g & (d.fin30 == 1), w),
            "ahorro_fuera_de_entidad": prop(d.fin17a != 1, g & (d.saved == 1), w),
            "salario_solo_efectivo": prop(d.receive_wages == 2, g & d.receive_wages.isin([1, 2, 3]), w),
        }
        for k, r in ind.items():
            filas.append(dict(ambito="UE-4 (Bulgaria, Croacia, Polonia, Rumanía)", grupo=nombre, indicador=k,
                              proporcion=r["p"], ic_inf=r["inf"], ic_sup=r["sup"], n=r["n"]))
    return pd.DataFrame(filas)


def main(ruta):
    w, _, _ = leer(ruta)
    t = calcular(w[w.economy.isin(UE4)].copy())
    t.round(4).to_csv(OUT / "findex2025_efectivo_ue4.csv", index=False)
    print(t.pivot(index="grupo", columns="indicador", values="proporcion").round(3).to_string())


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "microdatos/wld/findex_microdata_2025_labelled_update112425.dta")

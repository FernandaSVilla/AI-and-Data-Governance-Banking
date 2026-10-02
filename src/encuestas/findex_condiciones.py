"""Global Findex 2025: acceso a una cuenta según varias condiciones de entrada (figura 5 del ensayo).

Condiciones comparadas con su referencia (cuenta en una entidad financiera, account_fin):
  - sin documento de identidad (fin46 = 2)       frente a con documento (fin46 = 1)      · economías con la pregunta ID4D
  - sólo teléfono básico (con9 = 2)              frente a smartphone (con9 = 1)          · módulo de conectividad
  - sin teléfono móvil (con1 = 2)                frente a smartphone (con9 = 1)          · módulo de conectividad
  - sin uso de internet en 3 meses (internet_use = 0) frente a con uso (= 1)             · todas las economías
Además: entre adultos sin cuenta en una entidad financiera, porcentaje que no podría usarla sin ayuda (fin11_2 = 2).

Para cada condición: cociente descriptivo (pesos reescalados a la población adulta de cada economía; economía como
estrato; IC por linealización) y cociente ajustado (Poisson ponderada con efectos fijos de economía y controles de sexo,
edad, educación, quintil de ingreso, empleo y ruralidad). Asociaciones, no efectos causales. «No sabe / no responde» se excluye.
Uso: python src/encuestas/findex_condiciones.py [ruta al .dta]
"""
import pathlib
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm

RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "kit"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from evaluabilidad.encuestas import cociente_ponderado, proporcion, n_efectivo, wilson_eff  # noqa: E402
from leer import leer  # noqa: E402

Z = 1.959964


def condiciones(w):
    c = {}
    c["sin_documento"] = np.select([w.fin46 == 2, w.fin46 == 1], [1, 0], np.nan)
    smart = w.con9 == 1
    modulo = w.economy.isin(w.loc[w.con9.notna(), "economy"].unique())   # economías con el módulo de conectividad
    c["telefono_basico"] = np.select([w.con9 == 2, smart], [1, 0], np.nan)
    c["sin_telefono"] = np.select([modulo & (w.con1 == 2), smart], [1, 0], np.nan)
    c["sin_internet"] = w.internet_use.map({0: 1.0, 1: 0.0}).to_numpy()
    return c


NOMBRES = {"sin_documento": "Sin documento de identidad", "telefono_basico": "Sólo teléfono básico (sin smartphone)",
           "sin_telefono": "Sin teléfono móvil", "sin_internet": "Sin uso de internet (3 meses)"}
REFS = {"sin_documento": "con documento", "telefono_basico": "con smartphone", "sin_telefono": "con smartphone",
        "sin_internet": "con uso de internet"}


def base(w):
    d = w.copy()
    d["peso_pob"] = d.wgt * d.pop_adult / d.groupby("economy").wgt.transform("sum")
    return d


def descriptivo(d, x):
    m = ~np.isnan(x)
    dd, xx = d[m].copy(), x[m]
    # pesos reescalados a la población adulta dentro de quienes responden a la condición (igual que findex_documento.py)
    dd["peso_pob"] = dd.wgt * dd.pop_adult / dd.groupby("economy").wgt.transform("sum")
    y, ww = dd.account_fin.to_numpy(float), dd.peso_pob.to_numpy()
    en1, en0 = xx == 1, xx == 0
    r, lo, hi = cociente_ponderado(y, ww, en1, en0, upm=np.arange(len(dd)), estrato=dd.economy.to_numpy())
    return dict(economias=dd.economy.nunique(), n=int(m.sum()), n_condicion=int(en1.sum()),
                cuenta_condicion=proporcion(y[en1], ww[en1]), cuenta_referencia=proporcion(y[en0], ww[en0]),
                cociente=r, ic_inf=lo, ic_sup=hi)


def ajustado(d, x):
    dd = d.assign(cond=x)
    dd = dd.dropna(subset=["cond", "account_fin", "female", "age", "educ", "inc_q", "emp_in", "urbanicity"])
    dd = dd[dd.educ.isin([1, 2, 3])]
    dd = dd[dd.groupby("economy").cond.transform("nunique") == 2]
    ww = dd.peso_pob * len(dd) / dd.peso_pob.sum()
    X = pd.concat([dd[["cond"]], (dd.female == 1).astype(float).rename("mujer"), dd.age.rename("edad"),
                   (dd.age ** 2 / 100).rename("edad2"),
                   pd.get_dummies(dd.educ.astype(int), prefix="educ", drop_first=True, dtype=float),
                   pd.get_dummies(dd.inc_q.astype(int), prefix="q", drop_first=True, dtype=float),
                   (dd.emp_in == 1).astype(float).rename("trabaja"), (dd.urbanicity == 1).astype(float).rename("rural"),
                   pd.get_dummies(dd.economy, prefix="e", drop_first=True, dtype=float)], axis=1)
    res = sm.GLM(dd.account_fin.astype(float), sm.add_constant(X), family=sm.families.Poisson(),
                 var_weights=ww).fit(cov_type="HC1")
    b, se = res.params["cond"], res.bse["cond"]
    return dict(cociente_ajustado=np.exp(b), ic_inf_aj=np.exp(b - Z * se), ic_sup_aj=np.exp(b + Z * se))


def main(ruta):
    w, _, _ = leer(ruta)
    d = base(w)
    filas = []
    for k, x in condiciones(w).items():
        f = dict(condicion=k, nombre=NOMBRES[k], referencia=REFS[k])
        f.update(descriptivo(d, x)); f.update(ajustado(d, x))
        filas.append(f)
    t = pd.DataFrame(filas)
    out = RAIZ / "data" / "encuestas"
    t.round(4).to_csv(out / "findex2025_condiciones.csv", index=False)
    # necesitaría ayuda para usar una cuenta (sólo preguntado a quienes no tienen cuenta en una entidad financiera)
    a = d[d.fin11_2.isin([1, 2])]
    filas = []
    for amb, g in [("Todas las economías con la pregunta", a)] + list(a.groupby("regionwb")):
        y = (g.fin11_2 == 2).astype(float)
        p = proporcion(y, g.peso_pob); lo, hi = wilson_eff(p, n_efectivo(g.peso_pob))
        filas.append(dict(ambito=amb, economias=g.economy.nunique(), n=len(g), necesitaria_ayuda=p, ic_inf=lo, ic_sup=hi))
    ayuda = pd.DataFrame(filas)
    ayuda.round(4).to_csv(out / "findex2025_necesita_ayuda.csv", index=False)
    pd.set_option("display.width", 250)
    print(t.round(3).to_string(index=False)); print(); print(ayuda.round(3).to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "microdatos/wld/findex_microdata_2025_labelled_update112425.dta")

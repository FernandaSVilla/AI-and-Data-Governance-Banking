"""Comprobación de robustez: ¿se mantiene la brecha de acceso sin documento al ajustar por características?

Regresión de Poisson ponderada (Poisson «modificada», con errores robustos) de account_fin sobre no tener
documento de identidad, con efectos fijos de economía y controles de sexo, edad (y su cuadrado), educación,
quintil de ingreso, participación laboral y ruralidad. exp(coef) es un cociente de proporciones ajustado,
comparable al cociente descriptivo del kit. Los pesos se reescalan a la población adulta de cada economía.
Sigue siendo una asociación, no un efecto causal.
"""
import pathlib
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm

RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from leer import leer  # noqa: E402


def ajustar(w, ambito, regiones=None):
    d = w[w.fin46.isin([1, 2])].copy()
    if regiones is not None:
        d = d[d.regionwb.isin(regiones)]
    d = d.dropna(subset=["account_fin", "female", "age", "educ", "inc_q", "emp_in", "urbanicity"])
    d = d[d.educ.isin([1, 2, 3])]
    d["sin_doc"] = (d.fin46 == 2).astype(float)
    d["peso_pob"] = d.wgt * d.pop_adult / d.groupby("economy").wgt.transform("sum")
    d["peso_pob"] *= len(d) / d.peso_pob.sum()
    X = pd.concat([d[["sin_doc"]], (d.female == 1).astype(float).rename("mujer"),
                   d.age.rename("edad"), (d.age ** 2 / 100).rename("edad2"),
                   pd.get_dummies(d.educ.astype(int), prefix="educ", drop_first=True, dtype=float),
                   pd.get_dummies(d.inc_q.astype(int), prefix="q", drop_first=True, dtype=float),
                   (d.emp_in == 1).astype(float).rename("trabaja"), (d.urbanicity == 1).astype(float).rename("rural"),
                   pd.get_dummies(d.economy, prefix="e", drop_first=True, dtype=float)], axis=1)
    X = sm.add_constant(X)
    res = sm.GLM(d.account_fin.astype(float), X, family=sm.families.Poisson(), var_weights=d.peso_pob).fit(cov_type="HC1")
    b, se = res.params["sin_doc"], res.bse["sin_doc"]
    return dict(ambito=ambito, n=len(d), economias=d.economy.nunique(), cociente_ajustado=np.exp(b),
                ic_inf=np.exp(b - 1.959964 * se), ic_sup=np.exp(b + 1.959964 * se))


if __name__ == "__main__":
    w, _, _ = leer(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "microdatos/wld/findex_microdata_2025_labelled_update112425.dta")
    filas = [ajustar(w, "Todas las economías con la pregunta")]
    for r in sorted(w.regionwb.dropna().unique()):
        filas.append(ajustar(w, r, [r]))
    t = pd.DataFrame(filas)
    t.round(4).to_csv(RAIZ / "data/encuestas/findex2025_documento_ajustado.csv", index=False)
    print(t.round(3).to_string(index=False))

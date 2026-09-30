"""
Simulación ilustrativa: equidad de la evaluación frente a equidad de la evaluabilidad.

Qué muestra
-----------
Dos grupos con la MISMA distribución de solvencia real solicitan una cuenta.
El grupo B presenta documentación no estándar (p. ej., credenciales de asilo o
protección internacional) y supera el alta (KYC) con una tasa r_B inferior a la
del grupo A. Quien no supera el alta puede quedarse sin cuenta o entrar tarde por
una vía alternativa, con menos meses de historial. Un año después, la entidad
evalúa el crédito con un modelo entrenado con el historial interno.

Se comparan dos vistas:
  * Vista de auditoría del modelo: métricas de equidad calculadas sólo sobre
    quienes llegaron a ser evaluados (la práctica habitual).
  * Vista de población completa: qué proporción de las personas solventes de
    cada grupo obtiene finalmente crédito.

Es una simulación del MECANISMO, no una estimación empírica. Todos los
parámetros son supuestos explícitos (ver PARAMS) y pueden modificarse.

Reproducibilidad: python simulacion_evaluabilidad.py  (numpy, pandas, scikit-learn)
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

PARAMS = dict(
    n=200_000,            # personas elegibles que intentan abrir una cuenta
    share_b=0.20,         # proporción del grupo B (documentación no estándar)
    r_a=0.97,             # tasa de éxito del alta (KYC) del grupo A
    late_share=0.50,      # de quienes no superan el alta, fracción que entra tarde por otra vía
    hist_ok=(6, 24),      # meses de historial si el alta fue exitosa (uniforme)
    hist_late=(1, 6),     # meses de historial si la entrada fue tardía (uniforme)
    min_months=3,         # historial mínimo para ser evaluable por el modelo
    base_logit=-2.2,      # intercepto del riesgo de impago (~10 % de impago medio)
    risk_slope=1.2,       # efecto de la solvencia latente sobre el impago
    noise=1.6,            # ruido de las señales de historial con 6 meses de datos
    pd_cutoff=0.12,       # se aprueba si la probabilidad estimada de impago < 12 %
)


def simulate(r_b, seed, p=PARAMS):
    rng = np.random.default_rng(seed)
    n = p["n"]
    group = np.where(rng.random(n) < p["share_b"], "B", "A")
    z = rng.standard_normal(n)                                   # solvencia latente, idéntica en ambos grupos
    pdef = 1 / (1 + np.exp(-(p["base_logit"] - p["risk_slope"] * z)))
    default = rng.random(n) < pdef                              # impago realizado
    solvent = ~default

    r = np.where(group == "A", p["r_a"], r_b)
    onboard = rng.random(n) < r                                 # 1) alta / KYC
    late = (~onboard) & (rng.random(n) < p["late_share"])       # 2) entrada tardía por vía alternativa
    months = np.zeros(n)
    months[onboard] = rng.uniform(*p["hist_ok"], onboard.sum())
    months[late] = rng.uniform(*p["hist_late"], late.sum())
    evaluable = months >= p["min_months"]                       # 3) evaluabilidad

    # 4) señales de historial: más meses de datos = señal menos ruidosa
    sd = p["noise"] / np.sqrt(np.maximum(months, 1e-9) / 6)
    X = np.column_stack([z + rng.standard_normal(n) * sd for _ in range(3)] + [months])

    df = pd.DataFrame(dict(group=group, solvent=solvent, default=default,
                           onboard=onboard, late=late, evaluable=evaluable, months=months))
    ev = np.where(evaluable)[0]
    rng.shuffle(ev)
    train, test = ev[: len(ev) // 2], ev[len(ev) // 2:]
    model = LogisticRegression(max_iter=500).fit(X[train], default[train])  # modelo ciego al grupo
    df["pd_hat"] = np.nan
    df.loc[test, "pd_hat"] = model.predict_proba(X[test])[:, 1]
    df["approved"] = False
    df.loc[test, "approved"] = df.loc[test, "pd_hat"] < p["pd_cutoff"]

    # para la vista de población completa se usa la mitad de test de los evaluables
    # y la totalidad de los no evaluables (que no obtienen crédito del modelo)
    in_scope = np.zeros(n, bool)
    in_scope[test] = True
    in_scope[~evaluable] = True
    return df[in_scope].copy()


def metrics(df):
    out = {}
    for g in ["A", "B"]:
        d = df[df.group == g]
        e = d[d.evaluable]
        out[g] = dict(
            eval_rate=d.evaluable.mean(),
            appr_eval=e.approved.mean(),
            tpr_eval=e[e.solvent].approved.mean(),
            auc_eval=roc_auc_score(e.default, e.pd_hat),
            access_full=d[d.solvent].approved.mean(),
            months_eval=e.months.mean(),
        )
    return out


def run(r_grid=np.round(np.arange(0.40, 0.975, 0.05), 2), seeds=range(20)):
    rows = []
    for r_b in list(r_grid) + [0.97]:
        for s in seeds:
            m = metrics(simulate(r_b, seed=1000 + s))
            rows.append(dict(
                r_b=r_b, seed=s,
                eval_A=m["A"]["eval_rate"], eval_B=m["B"]["eval_rate"],
                appr_eval_A=m["A"]["appr_eval"], appr_eval_B=m["B"]["appr_eval"],
                tpr_eval_A=m["A"]["tpr_eval"], tpr_eval_B=m["B"]["tpr_eval"],
                auc_A=m["A"]["auc_eval"], auc_B=m["B"]["auc_eval"],
                access_A=m["A"]["access_full"], access_B=m["B"]["access_full"],
                months_A=m["A"]["months_eval"], months_B=m["B"]["months_eval"],
            ))
    res = pd.DataFrame(rows).drop_duplicates(["r_b", "seed"])
    res["ratio_appr_eval"] = res.appr_eval_B / res.appr_eval_A
    res["ratio_tpr_eval"] = res.tpr_eval_B / res.tpr_eval_A
    res["ratio_access"] = res.access_B / res.access_A
    return res


if __name__ == "__main__":
    import pathlib
    out = pathlib.Path(__file__).resolve().parents[1] / "data"
    res = run()
    res.to_csv(out / "simulacion_resultados_por_semilla.csv", index=False)
    summ = res.groupby("r_b").agg(["mean", lambda x: x.quantile(0.025), lambda x: x.quantile(0.975)])
    summ.columns = [f"{a}_{ {'mean':'mean','<lambda_0>':'p025','<lambda_1>':'p975'}[b] }" for a, b in summ.columns]
    summ.drop(columns=[c for c in summ.columns if c.startswith("seed")]).to_csv(out / "simulacion_resumen.csv")
    print(res.groupby("r_b")[["eval_B", "ratio_appr_eval", "ratio_tpr_eval", "ratio_access", "auc_A", "auc_B"]].mean().round(3))

"""Análisis de sensibilidad de la simulación (escenario r_B = 0,60)."""
import pathlib, pandas as pd
import simulacion_evaluabilidad as s
rows = []
variants = [("base", {}), ("sin entrada tardía", {"late_share": 0.0}), ("toda entrada tardía", {"late_share": 1.0}),
            ("umbral 8 %", {"pd_cutoff": 0.08}), ("umbral 20 %", {"pd_cutoff": 0.20}),
            ("grupo B 5 %", {"share_b": 0.05}), ("señal más ruidosa", {"noise": 2.5})]
for name, over in variants:
    p = dict(s.PARAMS, **over)
    for seed in range(5):
        m = s.metrics(s.simulate(0.60, seed=500 + seed, p=p))
        rows.append(dict(variante=name, seed=seed,
                         ratio_tpr_eval=m["B"]["tpr_eval"] / m["A"]["tpr_eval"],
                         ratio_access=m["B"]["access_full"] / m["A"]["access_full"],
                         auc_A=m["A"]["auc_eval"], auc_B=m["B"]["auc_eval"]))
df = pd.DataFrame(rows).groupby("variante", sort=False).mean().drop(columns="seed").round(3)
df.to_csv(pathlib.Path(__file__).resolve().parents[1] / "data" / "simulacion_sensibilidad.csv")
print(df)

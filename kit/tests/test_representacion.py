import pathlib
import pandas as pd
from evaluabilidad import representacion

KIT = pathlib.Path(__file__).resolve().parents[1]


def test_cociente_de_representacion():
    df = pd.DataFrame(dict(grupo=["mayores", "igual"], intentos_grupo=[20, 100], intentos_total=[1000, 1000],
                           poblacion_pct=[10, 0.10]))   # acepta porcentaje o tanto por uno
    r = representacion(df).set_index("grupo")
    assert abs(r.loc["mayores", "cociente"] - 0.2) < 1e-9      # 2 % de los intentos frente al 10 % de la población
    assert r.loc["mayores", "senal"] == "Señal clara"
    assert r.loc["mayores", "ic_inf"] < 0.2 < r.loc["mayores", "ic_sup"] < 1
    assert abs(r.loc["igual", "cociente"] - 1.0) < 1e-9 and r.loc["igual", "senal"] == "Sin señal"


def test_muestra_pequena_no_da_senal_clara():
    df = pd.DataFrame(dict(grupo=["g"], intentos_grupo=[1], intentos_total=[50], poblacion_pct=[0.2]))
    assert representacion(df).senal.iloc[0] == "A confirmar"


import math
import numpy as np
import pandas as pd
from evaluabilidad.encuestas import analizar_encuesta, cociente_ponderado, n_efectivo, tabla_publicable
from evaluabilidad.metricas import cociente_ic


def _encuesta(n=4000, semilla=1, efecto_upm=0.0):
    rng = np.random.default_rng(semilla)
    upm = rng.integers(0, 200, n)
    u = rng.normal(0, efecto_upm, 200)[upm]
    perfil = np.where(rng.random(n) < .3, "sin_documento", "con_documento")
    base = np.where(perfil == "con_documento", .8, .5)
    p = 1 / (1 + np.exp(-(np.log(base / (1 - base)) + u)))
    cuenta = (rng.random(n) < p).astype(int)
    credito = ((rng.random(n) < .3) & (cuenta == 1)).astype(int)
    peso = rng.uniform(.5, 2, n)
    sin_id = ((cuenta == 0) & (rng.random(n) < np.where(perfil == "sin_documento", .6, .1))).astype(int)
    return pd.DataFrame(dict(perfil=perfil, cuenta=cuenta, credito=credito, peso=peso, upm=upm, estrato=0, razon_id=sin_id))


def test_pesos_iguales_equivale_a_katz():
    d = _encuesta()
    y = d.cuenta.to_numpy()
    m1, m0 = (d.perfil == "sin_documento").to_numpy(), (d.perfil == "con_documento").to_numpy()
    r, lo, hi = cociente_ponderado(y, np.ones(len(d)), m1, m0)
    rk, lok, hik = cociente_ic(int(y[m1].sum()), int(m1.sum()), int(y[m0].sum()), int(m0.sum()))
    assert math.isclose(r, rk, rel_tol=1e-12)
    assert math.isclose(lo, lok, rel_tol=1e-3) and math.isclose(hi, hik, rel_tol=1e-3)


def test_kish():
    assert n_efectivo(np.ones(100)) == 100
    assert n_efectivo(np.r_[np.ones(50), 3 * np.ones(50)]) < 100


def test_conglomerados_ensanchan_el_intervalo():
    d = _encuesta(efecto_upm=0.8)
    y, w = d.cuenta.to_numpy(), d.peso.to_numpy()
    m1, m0 = (d.perfil == "sin_documento").to_numpy(), (d.perfil == "con_documento").to_numpy()
    _, lo_i, hi_i = cociente_ponderado(y, w, m1, m0)
    _, lo_c, hi_c = cociente_ponderado(y, w, m1, m0, upm=d.upm.to_numpy(), estrato=d.estrato.to_numpy())
    assert (hi_c - lo_c) > (hi_i - lo_i)


def test_analisis_completo_y_supresion():
    d = _encuesta()
    r = analizar_encuesta(d, "con_documento", credito="credito", upm="upm", estrato="estrato",
                          razones={"razon_id": "falta_documentacion"})
    c = r["cocientes"].set_index("vista")
    assert 0.55 < c.loc["tiene_cuenta", "cociente"] < 0.70 and c.loc["tiene_cuenta", "senal"] == "Señal clara"
    assert set(c.index) == {"tiene_cuenta", "credito_formal", "credito_con_cuenta"}
    assert r["razones"].loc["sin_documento", "falta_documentacion"] > r["razones"].loc["con_documento", "falta_documentacion"]
    t, cp = tabla_publicable(r, n_publicar=10_000)
    assert t["tiene_cuenta"].isna().all() and (cp.senal == "Suprimido (n pequeño)").all()


def test_perfil_sin_casos_positivos():
    y = np.r_[np.zeros(50), np.ones(80), np.zeros(20)]
    en1 = np.r_[np.ones(50), np.zeros(100)].astype(bool)
    r, lo, hi = cociente_ponderado(y, np.ones(150), en1, ~en1)
    assert r == 0 and math.isfinite(hi) and hi < 1

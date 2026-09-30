"""Global Findex 2025: acceso a una cuenta según se tenga o no documento de identidad.

Aplica el modo encuesta del kit a los microdatos públicos de Findex 2025 (Banco Mundial, uso público):
    perfil de referencia  = tiene documento de identidad fundacional (fin46 = 1)
    perfil comparado      = no lo tiene (fin46 = 2); «no sabe / no responde» se excluye
Variables: account_fin (cuenta en una entidad financiera, sin dinero móvil), fin22a (préstamo de una entidad
financiera formal), fin49b (sin documento: no ha podido usar servicios financieros por no tenerlo),
fin11a-f (razones para no tener cuenta en una entidad financiera), fin48a (sin documento fundacional, pero
con otro documento oficial). Pesos: wgt. Findex no publica estrato ni conglomerado en el archivo de uso
público: los intervalos reflejan el efecto de los pesos, no el del diseño por conglomerados.

Agregados regionales y mundial: cada persona se pondera por wgt reescalado a la población adulta de su
economía (pop_adult), y la economía se trata como estrato.

Uso: python src/encuestas/findex_documento.py microdatos/wld/findex_microdata_2025_labelled_update112425.dta
Salidas (sólo agregados, celdas con < 30 observaciones suprimidas): data/encuestas/findex2025_*.csv
"""
import pathlib
import sys

import numpy as np
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "kit"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from evaluabilidad.encuestas import analizar_encuesta, cociente_ponderado, proporcion, n_efectivo, wilson_eff, N_PUBLICAR  # noqa: E402
from evaluabilidad.metricas import senal, UMBRAL, N_MINIMO  # noqa: E402
from leer import leer  # noqa: E402

REF, SIN = "con_documento_identidad", "sin_documento_identidad"
RAZONES = {"fin11a": "lejania", "fin11b": "coste", "fin11c": "falta_documentacion", "fin11d": "falta_dinero",
           "fin11e": "familiar_ya_tiene", "fin11f": "desconfianza"}
OUT = RAIZ / "data" / "encuestas"


def sino(s):
    """1 = sí, 2 = no; «no sabe» (3) y «no responde» (4) se tratan como no disponibles."""
    x = pd.to_numeric(s, errors="coerce")
    return x.map({1: 1.0, 2: 0.0})


def adaptar(w: pd.DataFrame) -> pd.DataFrame:
    d = pd.DataFrame(dict(
        economia=w.economy, codigo=w.economycode, region=w.regionwb, peso=w.wgt.astype(float),
        pop_adult=w.pop_adult.astype(float),
        perfil=w.fin46.map({1: REF, 2: SIN}),
        cuenta=w.account_fin.astype(float), credito=sino(w.fin22a),
        otro_documento=sino(w.fin48a), no_pudo_usar_servicios=sino(w.fin49b)))
    for v, n in RAZONES.items():
        d["razon_" + n] = sino(w[v])
    d = d[d.perfil.notna()].copy()
    # peso poblacional para agregados entre economías
    d["peso_pob"] = d.peso * d.pop_adult / d.groupby("economia").peso.transform("sum")
    return d


def por_economia(d: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for (eco, cod, reg), g in d.groupby(["economia", "codigo", "region"]):
        if g.perfil.nunique() < 2:
            continue
        cred = "credito" if g.credito.notna().mean() > 0.5 else None
        r = analizar_encuesta(g, REF, credito=cred)
        t, c = r["tasas"], r["cocientes"].set_index("vista")
        sin = g[g.perfil == SIN]
        f = dict(economia=eco, codigo=cod, region=reg, n=len(g), n_sin_documento=len(sin),
                 pct_sin_documento=proporcion((g.perfil == SIN).astype(float), g.peso),
                 cuenta_con_documento=t.loc[REF, "tiene_cuenta"], cuenta_sin_documento=t.loc[SIN, "tiene_cuenta"],
                 cociente_cuenta=c.loc["tiene_cuenta", "cociente"], ic_inf=c.loc["tiene_cuenta", "ic_inf"],
                 ic_sup=c.loc["tiene_cuenta", "ic_sup"], senal=c.loc["tiene_cuenta", "senal"])
        if cred:
            f.update(cociente_credito=c.loc["credito_formal", "cociente"], senal_credito=c.loc["credito_formal", "senal"],
                     cociente_credito_con_cuenta=c.loc["credito_con_cuenta", "cociente"])
        m = sin.no_pudo_usar_servicios.notna()
        f["sin_doc_no_pudo_usar_servicios"] = proporcion(sin.no_pudo_usar_servicios[m], sin.peso[m]) if m.sum() else np.nan
        f["n_fin49b"] = int(m.sum())
        filas.append(f)
    return pd.DataFrame(filas)


def agregado(d: pd.DataFrame, nombre: str) -> dict:
    """Cociente agregado ponderado por población adulta, con la economía como estrato."""
    y, w = d.cuenta.to_numpy(), d.peso_pob.to_numpy()
    en1, en0 = (d.perfil == SIN).to_numpy(), (d.perfil == REF).to_numpy()
    r, lo, hi = cociente_ponderado(y, w, en1, en0, upm=np.arange(len(d)), estrato=d.economia.to_numpy())
    sin = d[en1]
    m = sin.no_pudo_usar_servicios.notna()
    p49 = proporcion(sin.no_pudo_usar_servicios[m], sin.peso_pob[m]) if m.sum() else np.nan
    return dict(ambito=nombre, economias=d.economia.nunique(), n=len(d), n_sin_documento=int(en1.sum()),
                pct_sin_documento=proporcion(en1.astype(float), w),
                cuenta_con_documento=proporcion(y[en0], w[en0]), cuenta_sin_documento=proporcion(y[en1], w[en1]),
                cociente_cuenta=r, ic_inf=lo, ic_sup=hi, senal=senal(r, hi, int(en1.sum()), UMBRAL, N_MINIMO),
                sin_doc_no_pudo_usar_servicios=p49,
                ic49=wilson_eff(p49, n_efectivo(sin.peso_pob[m])) if m.sum() else (np.nan, np.nan), n_fin49b=int(m.sum()))


def main(ruta):
    w, _, _ = leer(ruta)
    d = adaptar(w)
    OUT.mkdir(parents=True, exist_ok=True)

    eco = por_economia(d)
    pub = eco.copy()
    peq = pub.n_sin_documento < N_PUBLICAR
    pub.loc[peq, ["cuenta_sin_documento", "cociente_cuenta", "ic_inf", "ic_sup"]] = np.nan
    pub.loc[peq, "senal"] = "Suprimido (n < 30)"
    pub.loc[pub.n_fin49b < N_PUBLICAR, "sin_doc_no_pudo_usar_servicios"] = np.nan
    pub.round(4).to_csv(OUT / "findex2025_documento_por_economia.csv", index=False)

    ag = [agregado(d, "Todas las economías con la pregunta")]
    for reg, g in d.groupby("region"):
        ag.append(agregado(g, reg))
    ag = pd.DataFrame(ag)
    ag[["ic49_inf", "ic49_sup"]] = pd.DataFrame(ag.pop("ic49").tolist(), index=ag.index)
    ag.round(4).to_csv(OUT / "findex2025_documento_agregado.csv", index=False)

    # razones para no tener cuenta en una entidad financiera, por perfil (donde se preguntaron)
    sc = d[(d.cuenta == 0) & d.razon_falta_documentacion.notna()]
    filas = []
    for p, g in sc.groupby("perfil"):
        f = dict(perfil=p, economias=g.economia.nunique(), n_sin_cuenta=len(g))
        for n in RAZONES.values():
            m = g["razon_" + n].notna()
            f[n] = proporcion(g["razon_" + n][m], g.peso_pob[m])
        filas.append(f)
    pd.DataFrame(filas).round(4).to_csv(OUT / "findex2025_razones_sin_cuenta.csv", index=False)

    pd.set_option("display.width", 250)
    print(ag.round(3).to_string(index=False))
    v = eco[eco.n_sin_documento >= N_PUBLICAR]
    print(f"\nEconomías con la pregunta: {len(eco)}; con al menos {N_PUBLICAR} personas sin documento: {len(v)}")
    print(v.senal.value_counts().to_string())
    print("\nMediana del cociente:", round(v.cociente_cuenta.median(), 3))
    print(pd.DataFrame(filas).round(3).to_string(index=False))
    return eco, ag


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "microdatos/wld/findex_microdata_2025_labelled_update112425.dta")

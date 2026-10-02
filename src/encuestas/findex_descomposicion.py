"""¿Qué parte de la brecha de crédito formal se produce antes de cualquier evaluación? (Global Findex 2025)

Para cada condición de entrada (sin documento, sin teléfono, sólo teléfono básico, sin internet) frente a su
referencia, en las economías donde existen la condición y la pregunta de crédito formal (fin22a, «ha obtenido un
préstamo de un banco o institución financiera formal en los últimos 12 meses»):

  C = a · c1 + (1 − a) · c0
      a  = proporción con cuenta en una entidad financiera (account_fin)
      c1 = crédito formal entre quienes tienen cuenta;  c0 = crédito formal entre quienes no la tienen

La brecha de crédito entre la referencia (r) y el perfil (p), C_r − C_p, se descompone de forma exacta en
  · etapa de acceso:   (a_r − a_p) · (c1 − c0)         la parte que desaparecería si el perfil tuviera la tasa
                                                       de cuenta de la referencia
  · etapa posterior:   a · (c1_r − c1_p) + (1 − a) · (c0_r − c0_p)
Como el resultado depende de qué grupo se toma para ponderar, se usa el promedio de las dos ordenaciones
(descomposición de Shapley), que suma exactamente la brecha.

Tres especificaciones:
  · agregada: pesos reescalados a la población adulta de cada economía;
  · intra-economía: la descomposición se calcula dentro de cada economía y se agrega con la población del perfil,
    de modo que las diferencias entre países no contaminan el resultado (equivalente a efectos fijos de economía);
  · ajustada por características: cocientes de acceso a la cuenta y de crédito entre quienes tienen cuenta
    estimados con Poisson ponderada, efectos fijos de economía y controles (sexo, edad, educación, quintil de
    ingreso, empleo, ruralidad), errores HC1.
Intervalos: bootstrap de Poisson (pesos multiplicados por variables Poisson(1), equivalente a remuestrear
personas dentro de cada economía), 300 réplicas, percentiles 2,5 y 97,5.

Límites: el crédito obtenido depende también de la demanda, que la encuesta no observa; la etapa posterior mezcla
demanda, solvencia y decisión. La etapa de acceso no tiene esa ambigüedad: es lo que el perfil pierde por no tener
cuenta. Asociaciones, no efectos causales.

Uso: python src/encuestas/findex_descomposicion.py [ruta al .dta]
Salidas (sólo agregados, celdas con < 30 observaciones suprimidas): data/encuestas/findex2025_descomposicion*.csv,
incluida la versión para los cuatro Estados miembros de la UE con la pregunta de crédito (_ue.csv)
"""
import pathlib
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import findex_condiciones as F  # noqa: E402
from leer import leer  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parents[2]
OUT = RAIZ / "data" / "encuestas"
B = 300
N_MIN = 30
# Estados miembros de la UE en los que Global Findex 2025 formula la pregunta de crédito formal (fin22a)
UE_CREDITO = ["Bulgaria", "Croatia", "Poland", "Romania"]


def tasas(a, c, w, g):
    """Proporciones ponderadas para un grupo: acceso, crédito total, crédito con y sin cuenta."""
    wg = w * g
    W = wg.sum()
    if W == 0:
        return (np.nan,) * 4
    acc = (wg * a).sum() / W
    tot = (wg * c).sum() / W
    w1, w0 = (wg * a).sum(), (wg * (1 - a)).sum()
    c1 = (wg * a * c).sum() / w1 if w1 > 0 else np.nan
    c0 = (wg * (1 - a) * c).sum() / w0 if w0 > 0 else 0.0
    return acc, tot, c1, c0


def descomponer(tr, tp):
    """Shapley de dos etapas. Devuelve brecha total, parte de acceso y parte posterior (en puntos)."""
    ar, Cr, c1r, c0r = tr
    ap, Cp, c1p, c0p = tp
    acc1 = (ar - ap) * (c1p - c0p)          # ordenación 1: primero se iguala el acceso con las tasas del perfil
    acc2 = (ar - ap) * (c1r - c0r)          # ordenación 2: con las tasas de la referencia
    acceso = (acc1 + acc2) / 2
    gap = Cr - Cp
    return gap, acceso, gap - acceso


def calcular(d, x, w):
    a = d.account_fin.to_numpy(float)
    c = d.cred.to_numpy(float)
    gp, gr = (x == 1).astype(float), (x == 0).astype(float)
    tp, tr = tasas(a, c, w, gp), tasas(a, c, w, gr)
    gap, acceso, post = descomponer(tr, tp)
    return dict(cuenta_perfil=tp[0], cuenta_ref=tr[0], credito_perfil=tp[1], credito_ref=tr[1],
                credito_con_cuenta_perfil=tp[2], credito_con_cuenta_ref=tr[2],
                credito_sin_cuenta_perfil=tp[3], credito_sin_cuenta_ref=tr[3],
                brecha_pp=gap * 100, acceso_pp=acceso * 100, posterior_pp=post * 100,
                pct_acceso=acceso / gap if gap > 0 else np.nan,
                reduccion_contrafactual=acceso / gap if gap > 0 else np.nan)


def intra(d, x, w):
    """Descomposición dentro de cada economía, agregada con la población adulta del perfil en cada una."""
    tot = dict(gap=0.0, acc=0.0, peso=0.0)
    for _, idx in d.groupby("economy").indices.items():
        xi, wi = x[idx], w[idx]
        if (xi == 1).sum() < 5 or (xi == 0).sum() < 5:
            continue
        di = d.iloc[idx]
        r = calcular(di, xi, wi)
        pw = (wi * (xi == 1)).sum()
        if np.isnan(r["brecha_pp"]) or np.isnan(r["acceso_pp"]):
            continue
        tot["gap"] += pw * r["brecha_pp"]; tot["acc"] += pw * r["acceso_pp"]; tot["peso"] += pw
    g, ac = tot["gap"] / tot["peso"], tot["acc"] / tot["peso"]
    return dict(brecha_pp_intra=g, acceso_pp_intra=ac, pct_acceso_intra=ac / g if g > 0 else np.nan)


def ajustados(d, x):
    """Cocientes ajustados: acceso a la cuenta y crédito entre quienes tienen cuenta (Poisson, EF de economía)."""
    r_acc = F.ajustado(d, x)
    con = (d.account_fin == 1).to_numpy()
    dd = d[con].copy()
    dd["account_fin"] = dd.cred          # reutiliza la especificación de findex_condiciones con otro resultado
    r_c1 = F.ajustado(dd, x[con])
    return dict(cociente_cuenta_aj=r_acc["cociente_ajustado"], cociente_cuenta_aj_inf=r_acc["ic_inf_aj"],
                cociente_cuenta_aj_sup=r_acc["ic_sup_aj"],
                cociente_credito_con_cuenta_aj=r_c1["cociente_ajustado"], cociente_credito_con_cuenta_aj_inf=r_c1["ic_inf_aj"],
                cociente_credito_con_cuenta_aj_sup=r_c1["ic_sup_aj"])


def preparar(w):
    w = w.copy()
    w["cred"] = pd.to_numeric(w.fin22a, errors="coerce").map({1: 1.0, 2: 0.0})
    return w


def analizar(w, etiqueta, rng, ajustar=True, boot=True):
    filas = []
    conds = F.condiciones(w)
    for k, xall in conds.items():
        xall = np.asarray(xall, float)
        m = ~np.isnan(xall) & w.cred.notna().to_numpy() & w.account_fin.notna().to_numpy()
        d = w[m].copy()
        x = xall[m]
        d["peso_pob"] = d.wgt * d.pop_adult / d.groupby("economy").wgt.transform("sum")
        wt = d.peso_pob.to_numpy()
        n_p = int((x == 1).sum())
        f = dict(ambito=etiqueta, condicion=k, nombre=F.NOMBRES[k], referencia=F.REFS[k],
                 economias=d.economy.nunique(), n=len(d), n_perfil=n_p)
        if n_p < N_MIN:
            filas.append(f); continue
        f.update(calcular(d, x, wt))
        f.update(intra(d, x, wt))
        if boot:
            bs = []
            for _ in range(B):
                wb = wt * rng.poisson(1.0, len(wt))
                bs.append(calcular(d, x, wb)["pct_acceso"])
            bs = np.array([b for b in bs if not np.isnan(b)])
            f["pct_acceso_inf"], f["pct_acceso_sup"] = np.percentile(bs, [2.5, 97.5])
        if ajustar:
            try:
                f.update(ajustados(d, x))
            except Exception as e:  # pocas observaciones en algún subgrupo
                f["nota_ajuste"] = str(e)[:80]
        filas.append(f)
    return filas


def main(ruta):
    w, _, _ = leer(ruta)
    w = preparar(w)
    rng = np.random.default_rng(2026)
    filas = analizar(w, "Economías con la pregunta de crédito", rng)
    t = pd.DataFrame(filas)
    t.round(4).to_csv(OUT / "findex2025_descomposicion.csv", index=False)
    # heterogeneidad: ingreso alto frente al resto, y regiones (sin ajuste ni bootstrap, sólo descriptivo)
    het = []
    for reg, g in w.groupby("regionwb"):
        het += analizar(g, reg, rng, ajustar=False, boot=False)
    h = pd.DataFrame(het)
    h.round(4).to_csv(OUT / "findex2025_descomposicion_regiones.csv", index=False)
    # Unión Europea: sólo cuatro Estados miembros tienen la pregunta de crédito; agregado y por país
    ue = analizar(w[w.economy.isin(UE_CREDITO)].copy(), "UE-4 (Bulgaria, Croacia, Polonia, Rumanía)", rng)
    for e in UE_CREDITO:
        ue += analizar(w[w.economy == e].copy(), e, rng, ajustar=False)
    u = pd.DataFrame(ue)
    u.round(4).to_csv(OUT / "findex2025_descomposicion_ue.csv", index=False)
    pd.set_option("display.width", 260)
    cols = ["condicion", "economias", "n_perfil", "cuenta_perfil", "cuenta_ref", "credito_perfil", "credito_ref",
            "brecha_pp", "acceso_pp", "pct_acceso", "pct_acceso_inf", "pct_acceso_sup", "pct_acceso_intra",
            "cociente_cuenta_aj", "cociente_credito_con_cuenta_aj"]
    print(t[[c for c in cols if c in t]].round(3).to_string(index=False))
    print()
    print(h[["ambito", "condicion", "economias", "n_perfil", "brecha_pp", "pct_acceso"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "microdatos/wld/findex_microdata_2025_labelled_update112425.dta")

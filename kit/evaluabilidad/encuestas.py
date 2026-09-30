"""Modo encuesta (v0.4): aplica la lógica del kit a microdatos públicos de encuestas de hogares o personas.

Diferencia con el modo de registros
-----------------------------------
El kit está diseñado para registros de intentos de alta de una entidad. Una encuesta no registra intentos:
pregunta a personas si *tienen* cuenta. Por eso, en modo encuesta:

- la unidad es la persona encuestada, no el intento, y quien nunca lo intentó cuenta igual que quien fue rechazado;
- sólo se mide con rigor la primera etapa (tenencia de cuenta). El crédito formal se muestra como indicador
  descriptivo: depende de la demanda de cada persona y no equivale a «ser evaluado por un modelo»;
- no se localiza la etapa de la diferencia ni se atribuyen causas: las razones declaradas son autodeclaradas;
- se usan los pesos muestrales y, si la encuesta los publica, el estrato y la unidad primaria de muestreo (UPM).

Estadística
-----------
Proporciones ponderadas. El intervalo del cociente se calcula sobre el logaritmo del cociente con varianza
por linealización de Taylor (estimador de conglomerados «último conglomerado», con reemplazo), la aproximación
estándar para encuestas complejas. Sin UPM, cada persona es su propio conglomerado (varianza robusta con pesos).
Si el perfil no tiene ningún caso positivo, se usa la corrección de Haldane-Anscombe sobre el tamaño efectivo
de Kish. Con pesos iguales y sin conglomerados, el resultado converge al intervalo de Katz del modo de registros.

Control de divulgación: `tabla_publicable` suprime las celdas con menos de `n_publicar` observaciones.
"""
from __future__ import annotations
import math
import numpy as np
import pandas as pd
from .metricas import Z, UMBRAL, N_MINIMO, senal, cociente_ic

VISTAS_ENCUESTA = {
    "tiene_cuenta": ("¿Tiene cuenta?", "cuenta", None),
    "credito_formal": ("¿Ha obtenido crédito formal? (todas las personas)", "credito", None),
    "credito_con_cuenta": ("Con cuenta, ¿ha obtenido crédito formal?", "credito", "cuenta"),
}
N_PUBLICAR = 30


def n_efectivo(w: np.ndarray) -> float:
    """Tamaño efectivo de Kish: (Σw)² / Σw²."""
    w = np.asarray(w, float)
    return float(w.sum() ** 2 / (w ** 2).sum()) if len(w) and (w ** 2).sum() > 0 else 0.0


def proporcion(y, w) -> float:
    y, w = np.asarray(y, float), np.asarray(w, float)
    return float((w * y).sum() / w.sum()) if w.sum() > 0 else float("nan")


def wilson_eff(p: float, n_eff: float) -> tuple[float, float]:
    """Intervalo de Wilson con el tamaño efectivo (aproximación para proporciones ponderadas)."""
    if not n_eff or math.isnan(p):
        return (float("nan"), float("nan"))
    d = 1 + Z ** 2 / n_eff
    c = (p + Z ** 2 / (2 * n_eff)) / d
    h = Z * math.sqrt(p * (1 - p) / n_eff + Z ** 2 / (4 * n_eff ** 2)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def _var_linealizada(z: np.ndarray, upm: np.ndarray, estrato: np.ndarray) -> float:
    """Varianza del total de z con el estimador de último conglomerado (con reemplazo) por estratos."""
    df = pd.DataFrame(dict(z=z, upm=upm, h=estrato)).groupby(["h", "upm"], sort=False).z.sum().reset_index()
    v = 0.0
    for _, g in df.groupby("h", sort=False):
        n_h = len(g)
        if n_h > 1:
            v += n_h / (n_h - 1) * ((g.z - g.z.mean()) ** 2).sum()
    return v


def cociente_ponderado(y, w, en1, en0, upm=None, estrato=None) -> tuple[float, float, float]:
    """Cociente de proporciones ponderadas p1/p0 (dominios en1 y en0) con IC 95 % por linealización."""
    y = np.asarray(y, float)
    w = np.asarray(w, float)
    en1, en0 = np.asarray(en1, bool), np.asarray(en0, bool)
    W1, W0 = w[en1].sum(), w[en0].sum()
    if W1 == 0 or W0 == 0:
        return (float("nan"),) * 3
    p1, p0 = (w * y * en1).sum() / W1, (w * y * en0).sum() / W0
    if p0 == 0:
        return (float("nan"),) * 3
    r = p1 / p0
    if p1 == 0:   # sin casos positivos en el perfil: Haldane-Anscombe con tamaños efectivos
        n1, n0 = n_efectivo(w[en1]), n_efectivo(w[en0])
        _, lo, hi = cociente_ic(0, max(1, round(n1)), max(1, round(p0 * n0)), max(1, round(n0)))
        return (0.0, lo, hi)
    upm = np.arange(len(y)) if upm is None else np.asarray(upm)
    estrato = np.zeros(len(y)) if estrato is None else np.asarray(estrato)
    z = w * en1 * (y - p1) / (p1 * W1) - w * en0 * (y - p0) / (p0 * W0)
    se = math.sqrt(max(0.0, _var_linealizada(z, upm, estrato)))
    return (r, math.exp(math.log(r) - Z * se), math.exp(math.log(r) + Z * se))


def analizar_encuesta(df: pd.DataFrame, referencia: str, perfil: str = "perfil", cuenta: str = "cuenta",
                      peso: str | None = "peso", credito: str | None = None, upm: str | None = None,
                      estrato: str | None = None, razones: dict[str, str] | None = None,
                      umbral: float = UMBRAL, n_min: int = N_MINIMO) -> dict:
    """Analiza una encuesta ya adaptada: una fila por persona, con columnas de perfil, cuenta (0/1),
    peso y, opcionalmente, crédito formal (0/1), UPM, estrato y razones de no tener cuenta (0/1 cada una)."""
    d = df[df[perfil].notna() & df[cuenta].notna()].copy()
    avisos = []
    descartadas = len(df) - len(d)
    if descartadas:
        avisos.append(f"{descartadas} filas sin perfil o sin respuesta sobre la cuenta se excluyen.")
    w = d[peso].astype(float).to_numpy() if peso else np.ones(len(d))
    if peso and (w <= 0).any():
        avisos.append(f"{int((w <= 0).sum())} pesos nulos o negativos.")
    if not upm:
        avisos.append("Sin unidad primaria de muestreo: el intervalo sólo refleja el efecto de los pesos, "
                      "no el del muestreo por conglomerados, y puede ser algo estrecho.")
    U = d[upm].to_numpy() if upm else None
    H = d[estrato].to_numpy() if estrato else None
    if referencia not in set(d[perfil]):
        raise ValueError(f"No hay casos del perfil de referencia «{referencia}»")
    perfiles = [referencia] + sorted(set(d[perfil]) - {referencia}, key=str)

    filas_t, filas_c = [], []
    vistas = ["tiene_cuenta"] + (["credito_formal", "credito_con_cuenta"] if credito else [])
    for p in perfiles:
        m = (d[perfil] == p).to_numpy()
        fila = dict(perfil=p, n=int(m.sum()), n_efectivo=round(n_efectivo(w[m]), 1),
                    poblacion_ponderada=float(w[m].sum()))
        for v in vistas:
            _, var, cond = VISTAS_ENCUESTA[v]
            mc = m & (d[cond].astype(float).to_numpy() == 1) if cond else m
            y = d[var].astype(float).to_numpy()
            pv = proporcion(y[mc], w[mc])
            lo, hi = wilson_eff(pv, n_efectivo(w[mc]))
            fila.update({f"{v}": pv, f"{v}_ic_inf": lo, f"{v}_ic_sup": hi, f"{v}_n": int(mc.sum())})
        filas_t.append(fila)
        if p == referencia:
            continue
        m0 = (d[perfil] == referencia).to_numpy()
        for v in vistas:
            _, var, cond = VISTAS_ENCUESTA[v]
            base = d[cond].astype(float).to_numpy() == 1 if cond else np.ones(len(d), bool)
            y = d[var].astype(float).fillna(0).to_numpy()
            r, lo, hi = cociente_ponderado(y, w, m & base, m0 & base, U, H)
            n = int((m & base).sum())
            filas_c.append(dict(perfil=p, vista=v, cociente=r, ic_inf=lo, ic_sup=hi, n=n,
                                senal=senal(r, hi, n, umbral, n_min)))
        if m.sum() < n_min:
            avisos.append(f"El perfil «{p}» sólo tiene {int(m.sum())} observaciones: resultados orientativos.")

    raz = pd.DataFrame()
    if razones:
        sin = d[cuenta].astype(float) == 0
        filas_r = []
        for p in perfiles:
            m = (d[perfil] == p) & sin
            if not m.any():
                continue
            ww = w[m.to_numpy()]
            fila = dict(perfil=p, n_sin_cuenta=int(m.sum()))
            for col, etiqueta in razones.items():
                fila[etiqueta] = proporcion(d.loc[m, col].astype(float).fillna(0), ww)
            filas_r.append(fila)
        raz = pd.DataFrame(filas_r).set_index("perfil")

    return dict(tasas=pd.DataFrame(filas_t).set_index("perfil"), cocientes=pd.DataFrame(filas_c),
                razones=raz, avisos=avisos, umbral=umbral, referencia=referencia)


def tabla_publicable(r: dict, n_publicar: int = N_PUBLICAR) -> pd.DataFrame:
    """Tabla agregada lista para publicar: suprime (NaN) las estimaciones con menos de n_publicar observaciones."""
    t = r["tasas"].copy()
    for v in VISTAS_ENCUESTA:
        if f"{v}_n" in t:
            bajo = t[f"{v}_n"] < n_publicar
            t.loc[bajo, [v, f"{v}_ic_inf", f"{v}_ic_sup"]] = np.nan
    c = r["cocientes"].copy()
    if not c.empty:
        c.loc[c.n < n_publicar, ["cociente", "ic_inf", "ic_sup"]] = np.nan
        c.loc[c.n < n_publicar, "senal"] = "Suprimido (n pequeño)"
    return t.drop(columns=["poblacion_ponderada"]), c

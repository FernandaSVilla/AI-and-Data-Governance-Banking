"""Representación: ¿quién ni siquiera lo intenta? (v0.4)

El registro de intentos sólo ve a quien empieza el alta. Para acercarse a quien no lo intenta se compara la
composición de los intentos de un periodo con la de la población del área que atiende la entidad (padrón del INE
u otra fuente oficial):

    Rᴿ(g) = (x_g / N) / π_g

  x_g : intentos de alta del grupo g en el periodo (o altas, si sólo se conoce la composición de las altas)
  N   : intentos con el dato del grupo disponible
  π_g : proporción del grupo g en la población adulta del área de servicio

Rᴿ = 1 indica que el grupo intenta abrir una cuenta en la misma proporción en que está en la población; Rᴿ < 1,
que está infrarrepresentado. El intervalo de confianza del 95 % se obtiene con el de Wilson para x_g / N, tratando
π_g como conocido (dato censal). La regla de señal es la del resto del kit: «señal clara» si Rᴿ < umbral, el límite
superior del intervalo es menor que 1 y N ≥ n_min.

Entrada (agregada; no exige datos individuales): CSV con columnas
    grupo, intentos_grupo, intentos_total, poblacion_pct [, fuente_poblacion]
poblacion_pct puede darse en tanto por uno (0,12) o en porcentaje (12).

Límites. Una menor representación es una señal, no una prueba: puede deberse a una menor demanda del producto y no a
que el canal disuada. Si se usa la composición de las altas, el cociente mezcla el no intento y el no acceso. Los
grupos (edad, municipio rural, discapacidad reconocida…) se analizan sólo en agregado y con base jurídica propia.
"""
from __future__ import annotations
import pandas as pd
from .metricas import wilson, senal, UMBRAL, N_MINIMO

COLUMNAS = ["grupo", "intentos_grupo", "intentos_total", "poblacion_pct"]


def leer_representacion(df: pd.DataFrame) -> pd.DataFrame:
    falta = [c for c in COLUMNAS if c not in df.columns]
    if falta:
        raise ValueError("Faltan columnas en el archivo de representación: " + ", ".join(falta))
    d = df.copy()
    for c in ("intentos_grupo", "intentos_total", "poblacion_pct"):
        d[c] = pd.to_numeric(d[c].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    d.loc[d.poblacion_pct > 1, "poblacion_pct"] = d.poblacion_pct / 100
    return d


def representacion(df: pd.DataFrame, umbral: float = UMBRAL, n_min: int = N_MINIMO) -> pd.DataFrame:
    """Cociente de representación por grupo, con IC 95 % y señal."""
    d = leer_representacion(df)
    filas = []
    for _, r in d.iterrows():
        x, n, pi = int(r.intentos_grupo), int(r.intentos_total), float(r.poblacion_pct)
        if n <= 0 or not pi > 0:
            filas.append(dict(grupo=r.grupo, cuota_intentos=float("nan"), poblacion_pct=pi, cociente=float("nan"),
                              ic_inf=float("nan"), ic_sup=float("nan"), n=n, senal="Sin datos"))
            continue
        p = x / n
        lo, hi = wilson(x, n)
        rr, rlo, rhi = p / pi, lo / pi, hi / pi
        filas.append(dict(grupo=r.grupo, cuota_intentos=p, poblacion_pct=pi, cociente=rr, ic_inf=rlo, ic_sup=rhi,
                          n=n, senal=senal(rr, rhi, n, umbral, n_min),
                          fuente_poblacion=r.get("fuente_poblacion", "")))
    return pd.DataFrame(filas)

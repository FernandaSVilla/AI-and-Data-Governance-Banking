"""Adaptadores: convierten cada encuesta al formato del modo encuesta del kit.

Cada adaptador devuelve un DataFrame con una fila por persona y las columnas
    perfil (str), cuenta (0/1), peso (float) y, si la encuesta los tiene, credito (0/1), upm, estrato
    y razones de no tener cuenta (razon_*: 0/1).

Los nombres de variables marcados «VERIFICAR» deben confirmarse con el diccionario de datos de la
versión descargada (use `python src/encuestas/ejecutar.py --explorar ARCHIVO`). Si una variable no existe,
el adaptador falla con un mensaje claro en lugar de producir resultados erróneos.

El perfil describe la credencial o la situación documental, no la nacionalidad ni el origen de la persona,
igual que en el modo de registros. Donde la encuesta sólo permite distinguir población refugiada y de acogida,
se indica expresamente en la etiqueta del perfil.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def _exigir(df: pd.DataFrame, cols):
    faltan = [c for c in cols if c and c not in df.columns]
    if faltan:
        raise KeyError(f"Variables no encontradas: {faltan}. Revise los nombres con --explorar y actualice "
                       f"el adaptador en src/encuestas/fuentes.py.")


def _si(s: pd.Series, valores_si=(1,)) -> pd.Series:
    """1 si la respuesta está en valores_si, 0 si es otra respuesta válida, NaN si falta o es «no sabe/no responde»."""
    x = pd.to_numeric(s, errors="coerce")
    out = x.isin(valores_si).astype(float)
    out[x.isna()] = np.nan
    return out


# ---------------------------------------------------------------- Global Findex 2025 (Banco Mundial)
# Nombres tomados de las ediciones anteriores de Findex. VERIFICAR con el diccionario de 2025.
FINDEX = dict(
    peso="wgt",                      # VERIFICAR
    cuenta="account",                # 1 = tiene cuenta (institución financiera o dinero móvil) · VERIFICAR
    credito=None,                    # p. ej. préstamo de institución financiera formal · COMPLETAR tras explorar
    documento=None,                  # variable ID4D sobre documento de identidad (fin46-fin51) · COMPLETAR
    documento_si=(1,),               # códigos que significan «tiene documento» · COMPLETAR
    razones={},                      # {variable: 'razon_...'} razones de no tener cuenta · COMPLETAR si existen
)


def findex(df: pd.DataFrame, c: dict = FINDEX) -> tuple[pd.DataFrame, str]:
    _exigir(df, [c["peso"], c["cuenta"], c["credito"], c["documento"], *c["razones"]])
    if not c["documento"]:
        raise KeyError("Findex: falta indicar la variable de documento de identidad (FINDEX['documento']). "
                       "Sin ella no hay perfiles que comparar.")
    doc = _si(df[c["documento"]], c["documento_si"])
    out = pd.DataFrame(dict(
        perfil=np.where(doc == 1, "con_documento_identidad", np.where(doc == 0, "sin_documento_identidad", None)),
        cuenta=_si(df[c["cuenta"]]), peso=pd.to_numeric(df[c["peso"]], errors="coerce")))
    if c["credito"]:
        out["credito"] = _si(df[c["credito"]])
    for v, nombre in c["razones"].items():
        out[nombre] = _si(df[v])
    return out, "con_documento_identidad"


# ---------------------------------------------------------------- ACNUR
# Dos formas de definir el perfil, según lo que permita cada encuesta:
#  a) perfil_var + perfil_map: una variable categórica cuyos códigos se asignan a perfiles
#     (p. ej. tipo de documento que posee la persona). Es la opción para Jordania 2024, que sólo
#     encuesta a población refugiada: se compara quien tiene un documento que el banco suele aceptar
#     (referencia) con quien sólo tiene el documento de ACNUR o ninguno.
#  b) poblacion + refugiado/acogida (+ documento opcional): refugiados frente a comunidad de acogida.
#     Es la opción para la FDS de Sudán del Sur 2023, que incluye ambas poblaciones.
# Todos los nombres y códigos son provisionales: COMPLETAR tras --explorar con el diccionario de datos.
_BASE = dict(peso=None, upm=None, estrato=None, cuenta=None, cuenta_si=(1,), credito=None,
             perfil_var=None, perfil_map={}, referencia=None,
             poblacion=None, refugiado=(), acogida=(), documento=None, documento_si=(1,), razones={})
JORDANIA = dict(_BASE)     # Refugee Financial Inclusion and Financial Health, Baseline Survey 2024 → opción a)
SUDAN_SUR = dict(_BASE)    # Forced Displacement Survey 2023 → opción b); usar el peso de la persona encuestada (15+)


def acnur(df: pd.DataFrame, c: dict) -> tuple[pd.DataFrame, str]:
    if not (c["peso"] and c["cuenta"] and (c["perfil_var"] or c["poblacion"])):
        raise KeyError("Adaptador ACNUR incompleto: indique peso, cuenta y perfil_var o poblacion "
                       "(ejecute --explorar y complete JORDANIA o SUDAN_SUR en src/encuestas/fuentes.py).")
    _exigir(df, [c["peso"], c["cuenta"], c["perfil_var"], c["poblacion"], c["upm"], c["estrato"],
                 c["credito"], c["documento"], *c["razones"]])
    if c["perfil_var"]:
        if not c["referencia"] or c["referencia"] not in c["perfil_map"].values():
            raise KeyError("Con perfil_var, indique perfil_map {código: perfil} y un perfil de referencia incluido en él.")
        perfil = pd.to_numeric(df[c["perfil_var"]], errors="coerce").map(c["perfil_map"])
        ref = c["referencia"]
    else:
        pob = pd.to_numeric(df[c["poblacion"]], errors="coerce")
        es_ref, es_acog = pob.isin(c["refugiado"]), pob.isin(c["acogida"])
        if c["documento"]:
            doc = _si(df[c["documento"]], c["documento_si"])
            perfil = np.select([es_acog, es_ref & (doc == 1), es_ref & (doc == 0)],
                               ["acogida", "refugiado_con_documentacion", "refugiado_sin_documentacion"], None)
        else:
            perfil = np.select([es_acog, es_ref], ["acogida", "refugiado"], None)
        ref = "acogida"
    out = pd.DataFrame(dict(perfil=perfil, cuenta=_si(df[c["cuenta"]], c["cuenta_si"]),
                            peso=pd.to_numeric(df[c["peso"]], errors="coerce")))
    for k in ("upm", "estrato"):
        if c[k]:
            out[k] = df[c[k]].to_numpy()
    if c["credito"]:
        out["credito"] = _si(df[c["credito"]])
    for v, nombre in c["razones"].items():
        out[nombre] = _si(df[v])
    return out, ref


FUENTES = {
    "findex_espana": (findex, FINDEX, "Global Findex 2025 · España (Banco Mundial, uso público)"),
    "acnur_jordania": (lambda d: acnur(d, JORDANIA), JORDANIA, "ACNUR · Jordania 2024, inclusión financiera de población refugiada (microdatos públicos)"),
    "acnur_sudan_sur": (lambda d: acnur(d, SUDAN_SUR), SUDAN_SUR, "ACNUR · FDS Sudán del Sur 2023 (microdatos públicos)"),
}

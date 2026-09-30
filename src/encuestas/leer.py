"""Lectura de microdatos (CSV, Stata .dta, SPSS .sav) y explorador de variables."""
from __future__ import annotations
import pathlib
import re
import pandas as pd

CLAVES = {
    "peso": r"\bw(ei)?g(h)?t|weight|factor|pondera",
    "diseno": r"strat|psu|cluster|\bea\b|enumeration|conglomer|upm",
    "cuenta": r"account|bank|mobile money|cuenta",
    "credito": r"borrow|loan|credit|prést|prest",
    "documento": r"\bid\b|identif|identity|document|passport|card|permit|registrat",
    "poblacion": r"refugee|displac|asylum|host|national|citizen|migra|idp|status|population",
    "razon": r"reason|why|razón|motivo",
}


def leer(ruta: str | pathlib.Path) -> tuple[pd.DataFrame, dict, dict]:
    """Devuelve (datos, etiquetas de variables, etiquetas de valores). Los códigos numéricos se conservan."""
    ruta = pathlib.Path(ruta)
    suf = ruta.suffix.lower()
    if suf == ".csv":
        return pd.read_csv(ruta, low_memory=False), {}, {}
    if suf in (".dta", ".sav", ".zsav", ".por"):
        import pyreadstat
        f = {".dta": pyreadstat.read_dta, ".sav": pyreadstat.read_sav, ".zsav": pyreadstat.read_sav,
             ".por": pyreadstat.read_por}[suf]
        df, meta = f(str(ruta))
        etiquetas = dict(zip(meta.column_names, meta.column_labels or [None] * len(meta.column_names)))
        valores = {v: meta.value_labels.get(k, {}) for v, k in (meta.variable_to_label or {}).items()}
        return df, etiquetas, valores
    if suf in (".xlsx", ".xls"):
        return pd.read_excel(ruta), {}, {}
    raise ValueError(f"Formato no soportado: {suf}")


def explorar(ruta, max_valores: int = 6) -> pd.DataFrame:
    """Lista las variables cuyo nombre o etiqueta sugiere peso, diseño, cuenta, crédito, documento,
    población o razones. Sirve para completar el adaptador de cada fuente."""
    df, etq, val = leer(ruta)
    filas = []
    for c in df.columns:
        texto = f"{c} {etq.get(c) or ''}".lower()
        temas = [k for k, rx in CLAVES.items() if re.search(rx, texto)]
        if not temas:
            continue
        if df[c].nunique() > 20 and pd.api.types.is_numeric_dtype(df[c]):
            filas.append(dict(variable=c, etiqueta=etq.get(c) or "", temas=",".join(temas), distintos=df[c].nunique(),
                              valores=f"continua: mín {df[c].min():.3g}, mediana {df[c].median():.3g}, máx {df[c].max():.3g}"))
            continue
        vc = df[c].value_counts(dropna=False).head(max_valores)
        vals = "; ".join(f"{k}={val.get(c, {}).get(k, '') or ''} ({n})".replace("= (", " (") for k, n in vc.items())
        filas.append(dict(variable=c, etiqueta=etq.get(c) or "", temas=",".join(temas),
                          distintos=df[c].nunique(), valores=vals))
    print(f"{len(df):,} filas, {df.shape[1]} columnas")
    return pd.DataFrame(filas)

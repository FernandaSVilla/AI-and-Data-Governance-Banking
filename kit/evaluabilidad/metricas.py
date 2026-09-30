"""Métricas de evaluabilidad y trazabilidad del no acceso (v0.3).

Entradas
--------
altas : DataFrame, una fila por intento de alta (esquema/registro_no_acceso.schema.json).
        Mínimo (modo básico): id_intento, canal, perfil_entrada, resultado.
        Completo: además causa_no_acceso, alternativa_ofrecida, revision_humana,
        revertida_tras_revision, negativa_escrita, dias_resolucion.
credito : DataFrame opcional, una fila por persona evaluada por el sistema de solvencia
          (id_intento, aprobado). Sin él, sólo se calcula el acceso a la cuenta.

Cada perfil se compara con el perfil de referencia («estandar»). Los cocientes llevan
un intervalo de confianza del 95 % y una señal en tres niveles:
  - «Señal clara»: cociente por debajo del umbral y diferencia estadísticamente clara;
  - «A confirmar»: cociente por debajo del umbral, pero con incertidumbre o muestra pequeña;
  - «Sin señal».
"""
from __future__ import annotations
import math
import pandas as pd
from .perfiles import PERFILES, REFERENCIA, EQUIVALENCIA_V01

CAUSAS = ["documentacion_insuficiente", "documento_no_reconocido", "informacion_aml_adicional",
          "alerta_escalada", "duplicidad", "desistimiento", "fallo_tecnico",
          "derivacion_alternativa", "rechazo_definitivo"]
UMBRAL = 0.8          # umbral de revisión por defecto (referencia de cuatro quintos); configurable
N_MINIMO = 100        # por debajo, la muestra se considera pequeña
ACCESO = ["alta_completada", "alternativa_aceptada"]
Z = 1.959964


def preparar(altas: pd.DataFrame) -> pd.DataFrame:
    """Normaliza el registro: acepta la columna v0.1 «categoria_documental»."""
    a = altas.copy()
    if "perfil_entrada" not in a.columns:
        if "categoria_documental" in a.columns:
            a["perfil_entrada"] = a["categoria_documental"].map(EQUIVALENCIA_V01).fillna(a["categoria_documental"])
        else:
            raise ValueError("Falta la columna obligatoria 'perfil_entrada' en el registro de altas")
    for c in ["id_intento", "canal", "resultado"]:
        if c not in a.columns:
            raise ValueError(f"Falta la columna obligatoria '{c}' en el registro de altas")
    a["id_intento"] = a["id_intento"].astype(str)
    return a


def perfiles_presentes(a: pd.DataFrame) -> list[str]:
    orden = [p for p in PERFILES if p in set(a.perfil_entrada)]
    return orden + sorted(set(a.perfil_entrada) - set(orden))


def wilson(x: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = x / n
    d = 1 + Z**2 / n
    c = (p + Z**2 / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z**2 / (4 * n**2)) / d
    return (max(0.0, c - h), min(1.0, c + h))


RESULTADOS = ["alta_completada", "alternativa_aceptada", "no_acceso"]
CANALES = ["oficina", "web", "app", "videollamada", "telefono", "intermediario"]


def cociente_ic(x1: int, n1: int, x0: int, n0: int) -> tuple[float, float, float]:
    """Cociente de proporciones (x1/n1)/(x0/n0) con IC 95 % por el método logarítmico de Katz.

    Coincide con scipy.stats.contingency.relative_risk (véanse las pruebas). Cuando el perfil no tiene
    ningún éxito (x1 = 0), SciPy no da límite superior; aquí se aplica la corrección de Haldane-Anscombe
    (se suma 0,5 a los éxitos y 1 a los totales) sólo para el intervalo, y el cociente sigue siendo 0.
    Si el perfil de referencia no tiene éxitos, el cociente no está definido."""
    if min(n1, n0) == 0 or x0 == 0:
        return (float("nan"),) * 3
    r = (x1 / n1) / (x0 / n0)
    if x1 > 0:
        a, b, m1, m0 = x1, x0, n1, n0
    else:
        a, b, m1, m0 = x1 + 0.5, x0 + 0.5, n1 + 1, n0 + 1
    se = math.sqrt(max(0.0, 1 / a - 1 / m1 + 1 / b - 1 / m0))
    rr = (a / m1) / (b / m0)
    return (r, math.exp(math.log(rr) - Z * se), math.exp(math.log(rr) + Z * se))


def senal(r: float, hi: float, n: int, umbral: float, n_min: int = N_MINIMO) -> str:
    """«Señal clara» exige cociente bajo el umbral, IC por debajo de 1 y al menos n_min casos.
    El mínimo por defecto (100) se justifica en src/validacion_metodo.py: con 50 casos, una diferencia
    inexistente produce alguna señal en torno al 13 % de las veces; con 100, en torno al 5 %."""
    if math.isnan(r):
        return "Sin datos"
    if r >= umbral:
        return "Sin señal"
    if hi < 1 and n >= n_min:
        return "Señal clara"
    return "A confirmar"


def _es_bool(v) -> bool:
    return str(v).strip().lower() in ("true", "false", "1", "0", "sí", "si", "no", "yes")


def validar(a: pd.DataFrame, credito: pd.DataFrame | None, n_min: int = N_MINIMO) -> list[str]:
    """Comprobaciones de calidad antes de calcular. Devuelve avisos legibles; no modifica los datos."""
    avisos = []
    if REFERENCIA not in set(a.perfil_entrada):
        avisos.append("No hay intentos con perfil 'estandar': no se pueden calcular cocientes.")
    desconocidos = set(a.perfil_entrada) - set(PERFILES)
    if desconocidos:
        avisos.append(f"Perfiles no reconocidos (se analizan igualmente): {sorted(desconocidos)}")
    dup = a.id_intento.duplicated().sum()
    if dup:
        avisos.append(f"{dup} identificadores de intento repetidos en el registro de altas: cada intento debe aparecer una sola vez.")
    res_mal = set(a.resultado) - set(RESULTADOS)
    if res_mal:
        avisos.append(f"Valores de 'resultado' no reconocidos: {sorted(map(str, res_mal))}. Sólo cuentan como acceso 'alta_completada' y 'alternativa_aceptada'.")
    can_mal = set(a.canal) - set(CANALES)
    if can_mal:
        avisos.append(f"Canales no previstos en el esquema (se analizan igualmente): {sorted(map(str, can_mal))}")
    if "fecha" in a.columns:
        malas = pd.to_datetime(a.fecha, errors="coerce", format="%Y-%m-%d").isna() & a.fecha.notna()
        if malas.sum():
            avisos.append(f"{malas.sum()} fechas no tienen el formato AAAA-MM-DD.")
    if "causa_no_acceso" in a.columns:
        sin = ((a.resultado == "no_acceso") & a.causa_no_acceso.isna()).sum()
        if sin:
            avisos.append(f"{sin} intentos sin acceso no tienen causa registrada.")
        incompat = ((a.resultado != "no_acceso") & a.causa_no_acceso.notna()).sum()
        if incompat:
            avisos.append(f"{incompat} intentos con cuenta tienen una causa de no acceso: revise la coherencia del registro.")
        caus_mal = set(a.causa_no_acceso.dropna()) - set(CAUSAS)
        if caus_mal:
            avisos.append(f"Causas no normalizadas: {sorted(map(str, caus_mal))}")
    for p in perfiles_presentes(a):
        n = (a.perfil_entrada == p).sum()
        if n < n_min:
            avisos.append(f"El perfil '{p}' sólo tiene {n} intentos: sus resultados son orientativos.")
    if credito is not None:
        ids = set(a.id_intento)
        c = credito.assign(id_intento=credito.id_intento.astype(str))
        huerf = set(c.id_intento) - ids
        if huerf:
            avisos.append(f"{len(huerf)} decisiones de crédito no enlazan con ningún intento de alta.")
        rep = c[c.id_intento.duplicated(keep=False)]
        if len(rep):
            conflict = rep.groupby("id_intento").aprobado.apply(lambda s: s.astype(str).str.lower().nunique() > 1).sum()
            avisos.append(f"{rep.id_intento.nunique()} intentos tienen más de una decisión de crédito"
                          + (f" ({conflict} con decisiones contradictorias)" if conflict else "")
                          + ": debe haber una sola decisión final por intento.")
        sin_cuenta = set(c.id_intento) & set(a.loc[a.resultado == "no_acceso", "id_intento"])
        if sin_cuenta:
            avisos.append(f"{len(sin_cuenta)} decisiones de crédito corresponden a intentos sin cuenta: revise el enlace entre registros.")
        no_bool = (~c.aprobado.map(_es_bool)).sum()
        if no_bool:
            avisos.append(f"{no_bool} valores de 'aprobado' no son verdadero/falso.")
    return avisos


def embudo(a: pd.DataFrame, credito: pd.DataFrame | None) -> pd.DataFrame:
    """Intentos → con cuenta → evaluados → aprobados, por perfil de entrada."""
    ev = set(credito.id_intento.astype(str)) if credito is not None else set()
    ap = set(credito.loc[credito.aprobado.astype(str).str.lower().isin(["true", "1", "sí", "si"]), "id_intento"].astype(str)) if credito is not None else set()
    filas = []
    for p in perfiles_presentes(a):
        x = a[a.perfil_entrada == p].drop_duplicates("id_intento")
        n = len(x)
        con_cuenta = x.resultado.isin(ACCESO)
        acc = int(con_cuenta.sum())
        e = int((x.id_intento.isin(ev) & con_cuenta).sum())   # sólo cuenta como evaluado quien tiene cuenta
        apr = int((x.id_intento.isin(ap) & x.id_intento.isin(ev) & con_cuenta).sum())
        filas.append(dict(perfil=p, intentos=n, acceso=acc, evaluados=e, aprobados=apr,
                          tasa_acceso=acc / n, tasa_llega_modelo=e / acc if acc else float("nan"),
                          tasa_evaluabilidad=e / n,
                          tasa_aprobacion_evaluados=apr / e if e else float("nan"),
                          tasa_acceso_efectivo=apr / n))
    return pd.DataFrame(filas).set_index("perfil")


# Vistas: (nombre, numerador, denominador, etapa)
# Las tres primeras son tasas de cada etapa (condicionales) y sirven para localizar la primera señal;
# las dos últimas son acumuladas desde el intento: la evaluabilidad es el concepto del ensayo
# (de quienes lo intentan, quién llega al modelo) y el acceso efectivo, el resultado de principio a fin.
VISTAS = {
    "acceso_cuenta": ("¿Consigue la cuenta?", "acceso", "intentos", "alta"),
    "llega_modelo": ("Con cuenta, ¿llega al modelo?", "evaluados", "acceso", "datos"),
    "aprobacion": ("Entre evaluados, ¿hay diferencia en la aprobación?", "aprobados", "evaluados", "decision"),
    "evaluabilidad": ("Evaluabilidad acumulada (llega al modelo / intentos)", "evaluados", "intentos", None),
    "acceso_efectivo": ("Acceso efectivo (obtiene crédito / intentos)", "aprobados", "intentos", None),
}
ETAPAS = {"alta": "En el alta", "datos": "Al llegar al modelo", "decision": "En la decisión"}


def cocientes(emb: pd.DataFrame, con_credito: bool = True, umbral: float = UMBRAL, n_min: int = N_MINIMO) -> pd.DataFrame:
    """Cociente de cada perfil frente al de referencia, por vista, con IC 95 % y señal."""
    if REFERENCIA not in emb.index:
        return pd.DataFrame()
    ref = emb.loc[REFERENCIA]
    vistas = list(VISTAS) if con_credito else ["acceso_cuenta"]
    filas = []
    for p in emb.index:
        if p == REFERENCIA:
            continue
        r_ = emb.loc[p]
        for v in vistas:
            _, num, den, _ = VISTAS[v]
            r, lo, hi = cociente_ic(int(r_[num]), int(r_[den]), int(ref[num]), int(ref[den]))
            filas.append(dict(perfil=p, vista=v, cociente=r, ic_inf=lo, ic_sup=hi, n=int(r_[den]),
                              senal=senal(r, hi, int(r_[den]), umbral, n_min)))
    return pd.DataFrame(filas)


def diagnostico(coc: pd.DataFrame) -> pd.DataFrame:
    """Etapas del proceso en las que se observa una señal, en orden. Describe dónde aparece la
    diferencia, no por qué: son asociaciones agregadas, no causas."""
    if coc.empty:
        return pd.DataFrame()
    filas = []
    for p, g in coc.groupby("perfil", sort=False):
        s = g.set_index("vista").senal
        etapas = [VISTAS[v][3] for v in ("acceso_cuenta", "llega_modelo", "aprobacion")
                  if s.get(v) in ("Señal clara", "A confirmar")]
        filas.append(dict(perfil=p, etapas=etapas,
                          donde=" · ".join(ETAPAS[e] for e in etapas) if etapas else "Sin señal"))
    return pd.DataFrame(filas).set_index("perfil")


def trazabilidad(a: pd.DataFrame) -> pd.DataFrame:
    def media(s):
        return s.astype(str).str.lower().isin(["true", "1", "sí", "si"]).mean() if len(s) else float("nan")
    filas = []
    for p in perfiles_presentes(a):
        x = a[a.perfil_entrada == p]
        na = x[x.resultado == "no_acceso"]
        rev = x[x.revision_humana.astype(str).str.lower().isin(["true", "1"])] if "revision_humana" in x else x.iloc[0:0]
        filas.append(dict(
            perfil=p, no_acceso=len(na),
            con_causa_registrada=na.causa_no_acceso.notna().mean() if len(na) and "causa_no_acceso" in na else float("nan"),
            negativa_escrita=media(na.negativa_escrita) if "negativa_escrita" in na else float("nan"),
            alternativa_ofrecida=media(na.alternativa_ofrecida) if "alternativa_ofrecida" in na else float("nan"),
            revisiones_humanas=len(rev),
            reversion_tras_revision=media(rev.revertida_tras_revision) if "revertida_tras_revision" in rev and len(rev) else float("nan"),
            dias_resolucion_mediana=pd.to_numeric(x.dias_resolucion, errors="coerce").median() if "dias_resolucion" in x else float("nan"),
        ))
    return pd.DataFrame(filas).set_index("perfil")


def causas_por_perfil(a: pd.DataFrame) -> pd.DataFrame:
    if "causa_no_acceso" not in a.columns:
        return pd.DataFrame()
    na = a[(a.resultado == "no_acceso") & a.causa_no_acceso.notna()]
    if na.empty:
        return pd.DataFrame()
    t = pd.crosstab(na.perfil_entrada, na.causa_no_acceso, normalize="index")
    return t.reindex(index=[p for p in perfiles_presentes(a) if p in t.index],
                     columns=[c for c in CAUSAS if c in t.columns]).fillna(0)


def por_canal(a: pd.DataFrame) -> pd.DataFrame:
    """% de intentos con cuenta, por perfil (filas) y canal (columnas)."""
    t = a.assign(ok=a.resultado.isin(ACCESO)).pivot_table(index="perfil_entrada", columns="canal", values="ok", aggfunc="mean")
    orden = [c for c in ["app", "web", "videollamada", "oficina", "telefono", "intermediario"] if c in t.columns]
    return t.reindex(index=perfiles_presentes(a), columns=orden + [c for c in t.columns if c not in orden])


def calcular_todo(altas: pd.DataFrame, credito: pd.DataFrame | None = None, umbral: float = UMBRAL,
                  n_min: int = N_MINIMO) -> dict:
    a = preparar(altas)
    if credito is not None:
        credito = credito.assign(id_intento=credito.id_intento.astype(str))
    emb = embudo(a, credito)
    coc = cocientes(emb, credito is not None, umbral, n_min)
    return dict(avisos=validar(a, credito, n_min), embudo=emb, cocientes=coc, diagnostico=diagnostico(coc),
                trazabilidad=trazabilidad(a), causas=causas_por_perfil(a), canal=por_canal(a),
                umbral=umbral, con_credito=credito is not None, modo="completo" if "causa_no_acceso" in a.columns else "básico")


def auditoria_convencional(altas: pd.DataFrame) -> pd.DataFrame:
    """Auditoría de calidad de datos convencional, como punto de comparación (no forma parte del diagnóstico).

    Revisa lo que suele revisar un control de calidad de datos: valores nulos por columna, identificadores
    duplicados, valores fuera del dominio, fechas con formato inválido y rangos anómalos. No compara resultados
    entre perfiles: por eso no puede ver quién se queda fuera, aunque los datos estén perfectamente limpios."""
    a = altas
    filas = []
    for c in a.columns:
        filas.append(dict(control="Valores nulos", columna=c, incidencias=int(a[c].isna().sum())))
    filas.append(dict(control="Identificadores duplicados", columna="id_intento", incidencias=int(a.id_intento.duplicated().sum())))
    dominios = {"resultado": RESULTADOS, "canal": CANALES, "causa_no_acceso": CAUSAS}
    for c, dom in dominios.items():
        if c in a.columns:
            filas.append(dict(control="Valores fuera de dominio", columna=c,
                              incidencias=int((a[c].notna() & ~a[c].isin(dom)).sum())))
    if "fecha" in a.columns:
        filas.append(dict(control="Formato de fecha inválido", columna="fecha",
                          incidencias=int(pd.to_datetime(a.fecha, errors="coerce", format="%Y-%m-%d").isna().sum())))
    if "dias_resolucion" in a.columns:
        d = pd.to_numeric(a.dias_resolucion, errors="coerce")
        filas.append(dict(control="Rango anómalo (días < 0 o > 365)", columna="dias_resolucion",
                          incidencias=int(((d < 0) | (d > 365)).sum())))
    return pd.DataFrame(filas)

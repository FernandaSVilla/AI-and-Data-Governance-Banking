"""Genera un registro SINTÉTICO de intentos de alta y decisiones de crédito para probar el kit (v0.3).

Diez perfiles de entrada con comportamientos ilustrativos: 40.000 intentos con los siete perfiles
originales y un bloque adicional de 6.000 intentos (semilla propia) con tres perfiles que afectan
también a personas con DNI: necesidad de ayuda digital, ajuste de accesibilidad y falta de una
oficina accesible. El bloque adicional no altera los 40.000 intentos originales. Los parámetros son supuestos,
no datos de ninguna entidad. El generador usa el mismo algoritmo pseudoaleatorio (mulberry32)
que la versión web, de modo que «Ver ejemplo» en el navegador y este script producen
exactamente los mismos datos.

Uso: python generar_datos_demo.py  -> escribe altas_demo.csv y credito_demo.csv
"""
import pathlib
import pandas as pd

N, SEMILLA = 40_000, 2026
N_EXTRA, SEMILLA_EXTRA = 6_000, 2027
M = 0xFFFFFFFF

# perfil: (peso, p_digital, acceso_digital, acceso_oficina, causas_digital, causas_oficina,
#          p_alternativa, p_reversion, p_negativa_escrita, p_evaluado, p_aprobado)
_EST_D = [("fallo_tecnico", .40), ("desistimiento", .35), ("informacion_aml_adicional", .15), ("duplicidad", .10)]
_EST_O = [("documentacion_insuficiente", .35), ("informacion_aml_adicional", .30), ("desistimiento", .25), ("rechazo_definitivo", .10)]
PARAM = {
    "estandar": (.70, .60, .95, .97, _EST_D, _EST_O, .40, .10, .60, .80, .55),
    "proteccion_internacional": (.05, .40, .05, .60,
        [("documento_no_reconocido", .70), ("fallo_tecnico", .20), ("desistimiento", .10)],
        [("documento_no_reconocido", .40), ("informacion_aml_adicional", .25), ("desistimiento", .15), ("rechazo_definitivo", .15), ("derivacion_alternativa", .05)],
        .15, .45, .30, .80, .55),
    "nie_provisional": (.06, .50, .45, .85,
        [("documento_no_reconocido", .60), ("documentacion_insuficiente", .25), ("desistimiento", .15)],
        [("documentacion_insuficiente", .50), ("documento_no_reconocido", .30), ("desistimiento", .20)],
        .15, .45, .30, .80, .55),
    "pasaporte_sin_chip": (.05, .50, .55, .92,
        [("fallo_tecnico", .65), ("documento_no_reconocido", .20), ("desistimiento", .15)],
        [("documento_no_reconocido", .40), ("informacion_aml_adicional", .40), ("desistimiento", .20)],
        .15, .45, .30, .80, .55),
    "sin_domicilio": (.04, .40, .60, .70,
        [("documentacion_insuficiente", .70), ("desistimiento", .30)],
        [("documentacion_insuficiente", .60), ("rechazo_definitivo", .20), ("desistimiento", .20)],
        .15, .45, .30, .80, .55),
    "dispositivo_conectividad": (.05, .45, .40, .95,
        [("fallo_tecnico", .55), ("desistimiento", .45)],
        [("desistimiento", .60), ("documentacion_insuficiente", .40)],
        .15, .45, .30, .80, .55),
    "sin_historial": (.05, .80, .94, .97, _EST_D, _EST_O, .40, .10, .60, .45, .42),
}

# Bloque adicional: barreras que afectan también a personas con DNI (supuestos ilustrativos)
PARAM_EXTRA = {
    "asistencia_digital": (.35, .55, .45, .92,
        [("desistimiento", .55), ("fallo_tecnico", .30), ("documentacion_insuficiente", .15)],
        [("desistimiento", .60), ("documentacion_insuficiente", .40)],
        .25, .45, .35, .80, .55),
    "accesibilidad": (.25, .55, .40, .85,
        [("fallo_tecnico", .60), ("desistimiento", .40)],
        [("desistimiento", .55), ("fallo_tecnico", .45)],
        .20, .45, .35, .80, .55),
    "zona_sin_oficina": (.40, .85, .60, .90,
        [("desistimiento", .45), ("derivacion_alternativa", .35), ("fallo_tecnico", .20)],
        [("desistimiento", .70), ("documentacion_insuficiente", .30)],
        .20, .45, .35, .80, .55),
}


# Procedencia de los parámetros. Todos son supuestos de escenario. Los del documento de protección internacional
# están orientados por la revisión documental (sección 3.3 del ensayo), pero no se estiman a partir de ella.
PARAM_FUENTES = {
    "proteccion_internacional": {
        "acceso_digital = 0,05": "Supuesto de escenario, coherente con la revisión documental (sección 3.3): ninguna de las 11 entidades "
                                  "que publican los documentos admitidos en su alta digital incluye el de protección internacional. "
                                  "La revisión mide la información publicada, no qué proporción de personas abre la cuenta.",
        "acceso_oficina = 0,60": "Supuesto de escenario. Ilustra el funcionamiento del informe; no mide la exclusión real.",
        "resto": "Supuestos ilustrativos (peso, canal, alternativas, revisión, negativa escrita, crédito).",
    },
    "otros perfiles": "Supuestos ilustrativos, sin fuente pública que permita calibrarlos.",
}


def mulberry32(a):
    a &= M
    def r():
        nonlocal a
        a = (a + 0x6D2B79F5) & M
        t = ((a ^ (a >> 15)) * (1 | a)) & M
        t = ((t + (((t ^ (t >> 7)) * (61 | t)) & M)) & M) ^ t
        return ((t ^ (t >> 14)) & M) / 4294967296
    return r


def elegir(u, pares):
    acum = 0.0
    for k, p in pares:
        acum += p
        if u < acum:
            return k
    return pares[-1][0]


def generar(n=N, semilla=SEMILLA, extra=True):
    altas, credito = _bloque(PARAM, n, semilla, 0)
    if extra:
        a2, c2 = _bloque(PARAM_EXTRA, N_EXTRA, SEMILLA_EXTRA, n)
        altas, credito = altas + a2, credito + c2
    return pd.DataFrame(altas), pd.DataFrame(credito)


def _bloque(param, n, semilla, inicio):
    rnd = mulberry32(semilla)
    pesos = [(k, v[0]) for k, v in param.items()]
    altas, credito = [], []
    for i in range(inicio, inicio + n):
        u = [rnd() for _ in range(13)]  # número fijo de extracciones por fila
        perfil = elegir(u[0], pesos)
        (_, p_dig, acc_d, acc_o, cau_d, cau_o, p_alt, p_rev, p_esc, p_ev, p_ap) = param[perfil]
        digital = u[1] < p_dig
        canal = ("app" if u[2] < .5 else "web") if digital else "oficina"
        ok = u[3] < (acc_d if digital else acc_o)
        causa, alt, rev, revert, escrita = None, False, False, False, None
        if ok:
            resultado = "alta_completada"
            dias = int(u[10] * 3)
        else:
            causa = elegir(u[4], cau_d if digital else cau_o)
            alt = u[5] < p_alt
            resultado = "alternativa_aceptada" if alt and u[6] < .5 else "no_acceso"
            if resultado == "alternativa_aceptada":
                causa = None
            rev = u[7] < .30
            revert = rev and u[8] < p_rev
            escrita = (u[9] < p_esc) if resultado == "no_acceso" else None
            dias = int(u[10] * 20)
        iid = f"I{i:06d}"
        altas.append(dict(id_intento=iid, fecha="2026-03-01", canal=canal, producto="cuenta_ordinaria",
                          perfil_entrada=perfil, resultado=resultado, causa_no_acceso=causa,
                          alternativa_ofrecida=alt, revision_humana=rev, revertida_tras_revision=revert,
                          negativa_escrita=escrita, dias_resolucion=dias))
        if resultado != "no_acceso" and u[11] < p_ev:
            credito.append(dict(id_intento=iid, aprobado=u[12] < p_ap))
    return altas, credito


if __name__ == "__main__":
    altas, credito = generar()
    out = pathlib.Path(__file__).parent
    altas.to_csv(out / "altas_demo.csv", index=False)
    credito.to_csv(out / "credito_demo.csv", index=False)
    print(len(altas), "intentos;", len(credito), "evaluaciones")

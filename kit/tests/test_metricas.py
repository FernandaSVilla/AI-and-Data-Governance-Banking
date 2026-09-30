import json, math, pathlib
import pandas as pd
import pytest
from evaluabilidad import calcular_todo, generar_informe
from evaluabilidad.metricas import cociente_ic, senal, wilson, validar, preparar

KIT = pathlib.Path(__file__).resolve().parents[1]


def _datos():
    altas = pd.DataFrame(dict(
        id_intento=[f"i{i}" for i in range(8)],
        canal=["app"] * 8,
        perfil_entrada=["estandar"] * 4 + ["proteccion_internacional"] * 4,
        resultado=["alta_completada"] * 4 + ["alta_completada", "no_acceso", "no_acceso", "no_acceso"],
        causa_no_acceso=[None] * 5 + ["documento_no_reconocido"] * 3,
        negativa_escrita=[None] * 5 + [False, False, True],
    ))
    credito = pd.DataFrame(dict(id_intento=["i0", "i1", "i2", "i3", "i4"], aprobado=[True, True, False, False, True]))
    return altas, credito


def _c(r, vista):
    return r["cocientes"].set_index("vista").loc[vista, "cociente"]


def test_vistas_por_etapa_y_acumuladas():
    r = calcular_todo(*_datos())
    assert abs(_c(r, "acceso_cuenta") - 0.25) < 1e-9     # 1/4 frente a 4/4
    assert abs(_c(r, "llega_modelo") - 1.0) < 1e-9       # 1/1 frente a 4/4: quien tiene cuenta llega igual
    assert abs(_c(r, "aprobacion") - 2.0) < 1e-9         # 1/1 frente a 2/4
    assert abs(_c(r, "evaluabilidad") - 0.25) < 1e-9     # acumulada: 1/4 frente a 4/4
    assert abs(_c(r, "acceso_efectivo") - 0.5) < 1e-9    # 1/4 frente a 2/4


def test_localizacion_no_arrastra_perdidas_previas(tmp_path):
    """En el ejemplo, la pérdida del documento de protección internacional está en el alta:
    la etapa «llega al modelo» no debe marcar señal por arrastre."""
    import sys; sys.path.insert(0, str(KIT / "demo"))
    from generar_datos_demo import generar
    altas, credito = generar()
    r = calcular_todo(altas, credito)
    coc = r["cocientes"].set_index(["perfil", "vista"])
    assert coc.loc[("proteccion_internacional", "acceso_cuenta"), "senal"] == "Señal clara"
    assert coc.loc[("proteccion_internacional", "llega_modelo"), "senal"] == "Sin señal"
    assert r["diagnostico"].loc["proteccion_internacional", "etapas"] == ["alta"]
    assert r["diagnostico"].loc["sin_historial", "etapas"][0] == "datos"


def test_muestra_pequena_no_da_senal_clara():
    r = calcular_todo(*_datos())
    assert set(r["cocientes"].senal) <= {"A confirmar", "Sin señal"}
    assert any("orientativos" in a for a in r["avisos"])


def test_modo_basico_y_compatibilidad_v01():
    altas, _ = _datos()
    altas = altas.rename(columns={"perfil_entrada": "categoria_documental"}).replace({"proteccion_internacional": "no_estandar"})
    r = calcular_todo(altas[["id_intento", "canal", "categoria_documental", "resultado"]])
    assert list(r["cocientes"].vista) == ["acceso_cuenta"]
    assert r["modo"] == "básico"


def test_intervalo_coincide_con_scipy():
    rel = pytest.importorskip("scipy.stats.contingency").relative_risk
    for x1, n1, x0, n0 in [(300, 1000, 500, 1000), (45, 120, 900, 1000), (12, 60, 480, 800), (7, 100, 30, 5000)]:
        r, lo, hi = cociente_ic(x1, n1, x0, n0)
        ref = rel(x1, n1, x0, n0)
        ci = ref.confidence_interval(0.95)
        assert math.isclose(r, ref.relative_risk, rel_tol=1e-9)
        assert math.isclose(lo, ci.low, rel_tol=1e-6) and math.isclose(hi, ci.high, rel_tol=1e-6)


def test_casos_limite_del_intervalo():
    r, lo, hi = cociente_ic(0, 100, 50, 100)      # perfil sin éxitos: cociente 0 e IC finito (Haldane-Anscombe)
    assert r == 0 and lo >= 0 and math.isfinite(hi) and hi < 1
    assert all(math.isnan(v) for v in cociente_ic(5, 100, 0, 100))   # referencia sin éxitos: no definido
    assert all(math.isnan(v) for v in cociente_ic(5, 0, 5, 100))


def test_senal_y_umbral_configurables():
    assert senal(0.6, 0.7, 1000, 0.8) == "Señal clara"
    assert senal(0.6, 1.2, 1000, 0.8) == "A confirmar"
    assert senal(0.6, 0.7, 80, 0.8) == "A confirmar"
    assert senal(0.6, 0.7, 80, 0.8, n_min=50) == "Señal clara"
    assert senal(0.9, 0.95, 1000, 0.8) == "Sin señal"
    lo, hi = wilson(50, 100)
    assert 0.40 < lo < 0.41 and 0.59 < hi < 0.60


def test_calidad_de_datos_detecta_errores():
    altas, credito = _datos()
    altas = pd.concat([altas, altas.iloc[[0]]])                                  # id repetido
    altas.loc[altas.index[1], "resultado"] = "abierta"                           # resultado desconocido
    credito = pd.concat([credito, pd.DataFrame(dict(id_intento=["i0", "i5"], aprobado=[False, True]))])  # contradicción y crédito sin cuenta
    av = " ".join(validar(preparar(altas), credito))
    assert "repetidos" in av and "no reconocidos" in av
    assert "contradictorias" in av and "sin cuenta" in av


def test_demo_cumple_el_esquema():
    js = pytest.importorskip("jsonschema")
    import sys; sys.path.insert(0, str(KIT / "demo"))
    from generar_datos_demo import generar
    esquema = json.load(open(KIT / "esquema" / "registro_no_acceso.schema.json", encoding="utf-8"))
    altas, _ = generar(n=3000)
    v = js.Draft202012Validator(esquema)
    for fila in altas.astype(object).where(altas.notna(), None).to_dict("records"):
        errores = list(v.iter_errors(fila))
        assert not errores, (fila, errores[0].message)
    malo = dict(id_intento="x", fecha="2026-03-01", canal="app", perfil_entrada="estandar", resultado="no_acceso", causa_no_acceso=None)
    assert list(v.iter_errors(malo)), "no_acceso sin causa debe ser inválido"


def test_informe():
    html = generar_informe(*_datos())
    assert "Informe de evaluabilidad" in html and "Por qué el alta puede fallar" in html
    assert "trata igual" not in html and "Dónde se produce" not in html


def test_auditoria_convencional_no_ve_la_exclusion():
    """Sobre el ejemplo, un control de calidad de datos sólo señala nulos estructurales: no compara perfiles."""
    import sys; sys.path.insert(0, str(KIT / "demo"))
    from generar_datos_demo import generar
    from evaluabilidad import auditoria_convencional
    altas, _ = generar(n=5000)
    r = auditoria_convencional(altas)
    inc = r[r.incidencias > 0]
    assert set(inc.control) == {"Valores nulos"}
    assert set(inc.columna) <= {"causa_no_acceso", "negativa_escrita"}

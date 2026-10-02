"""Genera docs/index.html (versión web del kit) a partir de la plantilla.

La página resultante es un único archivo autocontenido: incluye PapaParse (MIT) y las fuentes
Source Sans 3 y Source Serif 4 (SIL OFL 1.1) incrustadas, y no carga ningún recurso de terceros.
Inyecta desde el paquete Python los perfiles de entrada, los parámetros del generador de datos
de ejemplo y el esquema, para que la web y la versión Python usen la misma definición."""
import base64, json, pathlib, sys
aqui = pathlib.Path(__file__).parent
kit = aqui.parent
raiz = kit.parent
ven = aqui / "vendor"
sys.path.insert(0, str(kit)); sys.path.insert(0, str(kit / "demo"))
from evaluabilidad.perfiles import PERFILES
from evaluabilidad.perfiles_en import PERFILES_EN
from generar_datos_demo import PARAM, PARAM_EXTRA


def fuente(familia, peso, archivo):
    b64 = base64.b64encode((ven / archivo).read_bytes()).decode()
    return (f"@font-face{{font-family:'{familia}';font-style:normal;font-weight:{peso};font-display:swap;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")


fuentes = "\n".join([fuente("Source Sans 3", w, f"source-sans-3-latin-{w}-normal.woff2") for w in (400, 600, 700)]
                    + [fuente("Source Serif 4", 600, "source-serif-4-latin-600-normal.woff2")])
s = (aqui / "plantilla_web.html").read_text(encoding="utf-8")
s = s.replace("/*__FUENTES__*/", "/* Fuentes Source Sans 3 y Source Serif 4, SIL Open Font License 1.1 */\n" + fuentes)
s = s.replace("/*__PAPAPARSE__*/", (ven / "papaparse.min.js").read_text(encoding="utf-8").replace("</script", "<\\/script"))
try:
    import markdown
    import re as _re
    md2html = lambda t: markdown.markdown(_re.sub(r"_{2,}", lambda m: "\\_" * len(m.group()), t), extensions=["tables", "nl2br", "sane_lists"])
except ImportError:  # sin la librería, el visor muestra el texto tal cual
    import html as _h
    md2html = lambda t: "<pre>" + _h.escape(t) + "</pre>"
DOCS = {"es": {}, "en": {}}
for idioma, clave, archivo, titulo in [
        ("es", "form", "formulario_solicitud_CPB.md", "Formulario de solicitud de cuenta de pago básica"),
        ("es", "check", "checklist_alta_digital.md", "Lista de comprobación del alta por perfil"),
        ("en", "check", "checklist_alta_digital_en.md", "Onboarding checklist by entry profile")]:
    md = (kit / "plantillas" / archivo).read_text(encoding="utf-8")
    DOCS[idioma][clave] = dict(titulo=titulo, archivo=archivo, md=md, html=md2html(md).replace("[ ] ", "☐ ").replace("[x] ", "☑ "))
s = s.replace("__DOCS__", json.dumps(DOCS, ensure_ascii=False).replace("</", "<\\/"))
s = s.replace("__PERFILES__", json.dumps(PERFILES, ensure_ascii=False))
s = s.replace("__PERFILES_EN__", json.dumps(PERFILES_EN, ensure_ascii=False))
s = s.replace("__PARAM_EXTRA__", json.dumps(PARAM_EXTRA, ensure_ascii=False))
s = s.replace("__PARAM__", json.dumps(PARAM, ensure_ascii=False))
s = s.replace("__SCHEMA__", json.dumps(json.load(open(kit / "esquema/registro_no_acceso.schema.json", encoding="utf-8")), ensure_ascii=False))
import csv
with open(raiz / "data/encuestas/findex2025_condiciones.csv", encoding="utf-8") as fh:
    fila = next(r for r in csv.DictReader(fh) if r["condicion"] == "sin_documento")
n, n_p = int(fila["n"]), int(fila["n_condicion"]); n_ref = n - n_p
coma = lambda v: f"{float(v):.2f}".replace(".", ",")
FINDEX = dict(economias=int(fila["economias"]), n=n, n_p=n_p, n_ref=n_ref,
              acc_p=round(float(fila["cuenta_condicion"]) * n_p), acc_ref=round(float(fila["cuenta_referencia"]) * n_ref),
              r=coma(fila["cociente"]), lo=coma(fila["ic_inf"]), hi=coma(fila["ic_sup"]),
              r_en=f'{float(fila["cociente"]):.2f}', lo_en=f'{float(fila["ic_inf"]):.2f}', hi_en=f'{float(fila["ic_sup"]):.2f}')
with open(raiz / "data/encuestas/findex2025_condiciones.csv", encoding="utf-8") as fh:
    COND = [{k: (float(v) if k not in ("condicion", "nombre", "referencia") else v) for k, v in r.items()} for r in csv.DictReader(fh)]
orden = ["sin_documento", "sin_telefono", "sin_internet", "telefono_basico"]
COND.sort(key=lambda r: orden.index(r["condicion"]) if r["condicion"] in orden else 99)
with open(raiz / "data/encuestas/findex2025_necesita_ayuda.csv", encoding="utf-8") as fh:
    FINDEX["ayuda"] = float(next(csv.DictReader(fh))["necesitaria_ayuda"])
s = s.replace("__FINDEX_COND__", json.dumps(COND, ensure_ascii=False))
s = s.replace("__FINDEX__", json.dumps(FINDEX))
with open(kit / "demo" / "representacion_demo.csv", encoding="utf-8") as fh:
    s = s.replace("__REP_DEMO__", json.dumps(list(csv.DictReader(fh)), ensure_ascii=False))
for marca, archivo in (("__ES_ECF__", "bde_cuadro31_ecf2021.csv"), ("__ES_EST__", "eurostat_banca_internet_discapacidad_2024.csv")):
    with open(raiz / "data" / archivo, encoding="utf-8") as fh:
        s = s.replace(marca, json.dumps(list(csv.DictReader(fh)), ensure_ascii=False))
ver = kit / "verificacion"
s = s.replace("__VERIF_A__", json.dumps((ver / "verificacion_altas.csv").read_text(encoding="utf-8")))
s = s.replace("__VERIF_C__", json.dumps((ver / "verificacion_credito.csv").read_text(encoding="utf-8")))
import re
externos = re.findall(r'(?:src\s*=\s*["\']https?:|<link[^>]+href\s*=\s*["\']https?:|url\(\s*["\']?https?:|@import)', s)
assert not externos, f"recursos externos: {externos}"
(raiz / "docs" / "index.html").write_text(s, encoding="utf-8")
print("docs/index.html generado:", len(s) // 1024, "KB")

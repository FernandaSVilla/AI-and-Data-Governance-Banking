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
from generar_datos_demo import PARAM


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
s = s.replace("__PARAM__", json.dumps(PARAM, ensure_ascii=False))
s = s.replace("__SCHEMA__", json.dumps(json.load(open(kit / "esquema/registro_no_acceso.schema.json", encoding="utf-8")), ensure_ascii=False))
import re
externos = re.findall(r'(?:src\s*=\s*["\']https?:|<link[^>]+href\s*=\s*["\']https?:|url\(\s*["\']?https?:|@import)', s)
assert not externos, f"recursos externos: {externos}"
(raiz / "docs" / "index.html").write_text(s, encoding="utf-8")
print("docs/index.html generado:", len(s) // 1024, "KB")

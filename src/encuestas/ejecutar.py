"""Modo encuesta: aplica el kit a microdatos públicos y guarda sólo resultados agregados.

Uso
    python src/encuestas/ejecutar.py --explorar microdatos/archivo.dta
    python src/encuestas/ejecutar.py --fuente acnur_jordania --archivo microdatos/archivo.dta

Los microdatos se guardan en microdatos/ (excluida del repositorio) y no se redistribuyen.
Resultados: data/encuestas/<fuente>_{tasas,cocientes,razones}.csv, con supresión de celdas pequeñas.
"""
import argparse
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "kit"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pandas as pd  # noqa: E402
from evaluabilidad.encuestas import analizar_encuesta, tabla_publicable, N_PUBLICAR  # noqa: E402
from leer import leer, explorar  # noqa: E402
from fuentes import FUENTES  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--explorar", help="Lista variables candidatas de un archivo de microdatos")
    p.add_argument("--fuente", choices=list(FUENTES))
    p.add_argument("--archivo")
    p.add_argument("--n-publicar", type=int, default=N_PUBLICAR)
    a = p.parse_args()
    pd.set_option("display.width", 220, "display.max_colwidth", 90, "display.max_rows", 400)
    if a.explorar:
        print(explorar(a.explorar).to_string(index=False))
        return
    if not (a.fuente and a.archivo):
        p.error("indique --explorar ARCHIVO o bien --fuente y --archivo")
    adaptar, conf, titulo = FUENTES[a.fuente]
    df, _, _ = leer(a.archivo)
    d, ref = adaptar(df)
    razones = {c: c for c in d.columns if c.startswith("razon_")}
    r = analizar_encuesta(d, ref, credito="credito" if "credito" in d else None,
                          upm="upm" if "upm" in d else None, estrato="estrato" if "estrato" in d else None,
                          razones=razones or None)
    t, c = tabla_publicable(r, a.n_publicar)
    out = RAIZ / "data" / "encuestas"
    out.mkdir(parents=True, exist_ok=True)
    t.round(4).to_csv(out / f"{a.fuente}_tasas.csv")
    c.round(4).to_csv(out / f"{a.fuente}_cocientes.csv", index=False)
    if not r["razones"].empty:
        rz = r["razones"].copy()
        rz.loc[rz.n_sin_cuenta < a.n_publicar, [x for x in rz.columns if x != "n_sin_cuenta"]] = float("nan")
        rz.round(4).to_csv(out / f"{a.fuente}_razones.csv")
    print(titulo, "\n")
    print(t.round(3).to_string(), "\n")
    print(c.round(3).to_string(index=False), "\n")
    for x in r["avisos"]:
        print("Aviso:", x)


if __name__ == "__main__":
    main()

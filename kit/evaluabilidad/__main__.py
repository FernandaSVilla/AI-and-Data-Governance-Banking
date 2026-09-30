"""Uso: python -m evaluabilidad --altas altas.csv [--credito credito.csv] --salida informe.html [--entidad "Nombre"] [--umbral 0.8]

Sin --credito se ejecuta en modo básico: sólo compara el acceso a la cuenta por perfil y canal."""
import argparse
import pandas as pd
from .informe import generar_informe
from .metricas import calcular_todo, UMBRAL, N_MINIMO
from .perfiles import nombre


def main():
    p = argparse.ArgumentParser(description="Informe de evaluabilidad y gobernanza del no acceso")
    p.add_argument("--altas", required=True, help="CSV de intentos de alta (esquema/registro_no_acceso.schema.json)")
    p.add_argument("--credito", help="CSV de decisiones de crédito: id_intento, aprobado (opcional)")
    p.add_argument("--salida", default="informe_evaluabilidad.html")
    p.add_argument("--entidad", default="Entidad")
    p.add_argument("--umbral", type=float, default=UMBRAL, help="Umbral de revisión del cociente (por defecto 0,80)")
    p.add_argument("--n-min", type=int, default=N_MINIMO, help="Casos mínimos para emitir «Señal clara» (por defecto 100)")
    a = p.parse_args()
    altas = pd.read_csv(a.altas)
    credito = pd.read_csv(a.credito) if a.credito else None
    generar_informe(altas, credito, entidad=a.entidad, ruta=a.salida, umbral=a.umbral, n_min=a.n_min)
    r = calcular_todo(altas, credito, a.umbral, a.n_min)
    for perfil, d in r["diagnostico"].donde.items():
        print(f"{nombre(perfil):<50} {d}")
    print(f"\nInforme escrito en {a.salida}")


if __name__ == "__main__":
    main()

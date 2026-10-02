"""Archivo de verificación: 200 intentos de alta que se pueden contar a mano en una hoja de cálculo.

Dos perfiles de 100 intentos cada uno. Las cifras coinciden con el esquema del método de la web
(por cada 100 intentos: referencia 100 → 96 con cuenta → 77 evaluados → 42 con crédito;
perfil analizado 100 → 43 → 34 → 19), de modo que el cociente del alta es
R1 = (43/100) / (96/100) = 0,45.

Uso: python generar_verificacion.py  -> verificacion_altas.csv y verificacion_credito.csv
"""
import csv, pathlib

aqui = pathlib.Path(__file__).parent
altas, cred = [], []

def bloque(perfil, inicio, filas, evaluados, aprobados):
    """filas: lista de (n, canal, resultado, causa, negativa_escrita)."""
    i = inicio
    con_cuenta = []
    for n, canal, res, causa, esc in filas:
        for k in range(n):
            iid = f"V{i:03d}"
            e = "" if esc is None else ("true" if k < esc else "false")
            altas.append([iid, "2026-03-01", canal, perfil, res, causa or "", e])
            if res == "alta_completada":
                con_cuenta.append(iid)
            i += 1
    for j, iid in enumerate(con_cuenta[:evaluados]):
        cred.append([iid, "true" if j < aprobados else "false"])
    return i

i = bloque("estandar", 1, [
    (70, "app", "alta_completada", None, None),
    (26, "oficina", "alta_completada", None, None),
    (4, "app", "no_acceso", "desistimiento", 2),
], evaluados=77, aprobados=42)
bloque("proteccion_internacional", i, [
    (5, "app", "alta_completada", None, None),
    (38, "oficina", "alta_completada", None, None),
    (55, "app", "no_acceso", "documento_no_reconocido", 15),
    (2, "oficina", "no_acceso", "informacion_aml_adicional", 2),
], evaluados=34, aprobados=19)

with open(aqui / "verificacion_altas.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["id_intento", "fecha", "canal", "perfil_entrada", "resultado", "causa_no_acceso", "negativa_escrita"]); w.writerows(altas)
with open(aqui / "verificacion_credito.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["id_intento", "aprobado"]); w.writerows(cred)
print(len(altas), "intentos;", len(cred), "evaluaciones")

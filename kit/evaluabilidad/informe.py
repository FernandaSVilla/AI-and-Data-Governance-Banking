"""Genera un informe HTML autocontenido para anexar a la DPIA (RGPD art. 35),
la FRIA (Reglamento de IA art. 27) o la supervisión del responsable del despliegue (art. 26.5), que puede alimentar la vigilancia poscomercialización del proveedor (art. 72)."""
from __future__ import annotations
import base64, io, datetime, html
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from .metricas import calcular_todo, UMBRAL, N_MINIMO, VISTAS, ETAPAS
from .perfiles import PERFILES, REFERENCIA, nombre

INK, INK2, GRID = "#101828", "#475467", "#e4e7ec"
ESTADO = {"Señal clara": "#c2410c", "A confirmar": "#b7791f", "Sin señal": "#0f766e", "Sin datos": "#98a2b3"}
SEQ = LinearSegmentedColormap.from_list("azul", ["#eef4fc", "#9cc2ee", "#2a78d6", "#0a2240"])
NOMBRES_CAUSA = {"documentacion_insuficiente": "Documentación insuficiente", "documento_no_reconocido": "Documento no reconocido",
                 "informacion_aml_adicional": "Información AML adicional", "alerta_escalada": "Alerta escalada",
                 "duplicidad": "Duplicidad", "desistimiento": "Desistimiento", "fallo_tecnico": "Fallo técnico o de verificación",
                 "derivacion_alternativa": "Derivación a alternativa", "rechazo_definitivo": "Rechazo definitivo"}
CANAL = {"app": "App", "web": "Web", "videollamada": "Videollamada", "oficina": "Oficina", "telefono": "Teléfono", "intermediario": "Intermediario"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": "#98a2b3"})
f2 = lambda v: "—" if pd.isna(v) else f"{v:.2f}".replace(".", ",")
pc = lambda v, d=0: "—" if pd.isna(v) else f"{v*100:.{d}f} %".replace(".", ",")


def _png(fig) -> str:
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=160, bbox_inches="tight"); plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def fig_cocientes(coc: pd.DataFrame, umbral: float = UMBRAL, vistas=("acceso_cuenta", "llega_modelo", "aprobacion"),
                  titulos=("a) Alta: ¿consigue la cuenta?", "b) Con cuenta: ¿llega al modelo?", "c) Evaluados: ¿diferencia en la aprobación?"), figsize=None):
    """Cociente de cada perfil frente al de referencia, con IC 95 %, en cada etapa del proceso."""
    vistas = [v for v in vistas if v in set(coc.vista)]
    perfiles = list(dict.fromkeys(coc.perfil))
    figsize = figsize or (3.0 * len(vistas) + 2.6, 0.45 * len(perfiles) + 1.6)
    fig, axs = plt.subplots(1, len(vistas), figsize=figsize, sharey=True)
    axs = [axs] if len(vistas) == 1 else list(axs)
    y = list(range(len(perfiles)))[::-1]
    tit = dict(zip(("acceso_cuenta", "llega_modelo", "aprobacion"), titulos))
    for ax, v in zip(axs, vistas):
        d = coc[coc.vista == v].set_index("perfil").reindex(perfiles)
        ax.axvline(1, color="#d0d5dd", lw=0.8)
        ax.axvline(umbral, color=INK2, lw=0.9, ls=(0, (2, 2)))
        for yi, (p, r) in zip(y, d.iterrows()):
            c = ESTADO.get(r.senal, "#98a2b3")
            ax.plot([r.ic_inf, r.ic_sup], [yi, yi], color=c, lw=2, solid_capstyle="round")
            ax.plot(r.cociente, yi, "o", ms=6.5, color=c, mec="white", mew=1.2, zorder=3)
            ax.text(max(r.ic_sup, r.cociente) + 0.03, yi, f2(r.cociente), va="center", fontsize=8, color=INK)
        ax.set_xlim(0.2, 1.35); ax.set_ylim(-0.6, len(perfiles) - 0.4)
        ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:.1f}".replace(".", ",")))
        ax.set_title(tit.get(v, VISTAS[v][0]), loc="left", fontsize=9.5, fontweight="bold", color=INK)
        ax.tick_params(axis="y", length=0)
    axs[0].set_yticks(y, [nombre(p) for p in perfiles], fontsize=8.5)
    fig.tight_layout(rect=(0, 0.1, 1, 1), w_pad=1.2)
    hs = [plt.Line2D([], [], marker="o", ls="", color=c, label=k) for k, c in ESTADO.items() if k != "Sin datos"]
    hs.append(plt.Line2D([], [], color=INK2, lw=0.9, ls=(0, (2, 2)), label=f"Umbral de revisión ({f2(umbral)})"))
    fig.legend(handles=hs, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=4, frameon=False, fontsize=8)
    fig.text(0.5, -0.04, f"Cociente frente al perfil de referencia ({nombre(REFERENCIA).lower()}): 1 = igualdad. Punto: cociente; línea: intervalo de confianza del 95 %.",
             ha="center", fontsize=8, color=INK2)
    return fig


def fig_canal(canal: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(1.3 * canal.shape[1] + 3.2, 0.42 * canal.shape[0] + 0.9))
    ax.imshow(canal.values, cmap=SEQ, vmin=0, vmax=1, aspect="auto")
    for i in range(canal.shape[0]):
        for j in range(canal.shape[1]):
            v = canal.values[i, j]
            ax.text(j, i, pc(v), ha="center", va="center", fontsize=8.5, color="white" if v > 0.75 else INK)
    ax.set_xticks(range(canal.shape[1]), [CANAL.get(c, c) for c in canal.columns])
    ax.set_yticks(range(canal.shape[0]), [nombre(p) for p in canal.index], fontsize=8.5)
    ax.tick_params(length=0); ax.xaxis.tick_top()
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([x - .5 for x in range(1, canal.shape[1])], minor=True)
    ax.set_yticks([y - .5 for y in range(1, canal.shape[0])], minor=True)
    ax.grid(which="minor", color="white", lw=2); ax.tick_params(which="minor", length=0)
    return fig


def _tabla_html(filas, cabecera, alinear_izq=1) -> str:
    th = "".join(f"<th{' class=l' if i < alinear_izq else ''}>{h}</th>" for i, h in enumerate(cabecera))
    tr = "".join("<tr>" + "".join(f"<td{' class=l' if i < alinear_izq else ''}>{c}</td>" for i, c in enumerate(f)) + "</tr>" for f in filas)
    return f"<table class='t'><tr>{th}</tr>{tr}</table>"


def _chip(s):
    return f"<span class='chip' style='color:{ESTADO.get(s, INK2)}'>● {s}</span>"


CSS = """body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:1000px;margin:32px auto;padding:0 16px;color:#101828;background:#fff;line-height:1.5}
h1{font-size:1.6rem;margin-bottom:.2rem;color:#0a2240}h2{font-size:1.1rem;margin-top:2rem;border-bottom:2px solid #0a2240;padding-bottom:.3rem;color:#0a2240}
.sub{color:#475467}.alert{background:#fff4ed;border-left:4px solid #c2410c;padding:.6rem .9rem;margin:.5rem 0}
.ok{background:#effaf8;border-left:4px solid #0f766e;padding:.6rem .9rem;margin:.5rem 0}
table.t{border-collapse:collapse;font-size:.86rem;margin:.6rem 0;width:100%}table.t th,table.t td{border-bottom:1px solid #eaecf0;padding:.4rem .5rem;text-align:right;vertical-align:top}
table.t th{background:#f7f9fb;font-size:.78rem;text-transform:uppercase;letter-spacing:.04em;color:#475467}.l{text-align:left!important}
.chip{font-weight:600;white-space:nowrap}img{max-width:100%}small{color:#475467}"""


def generar_informe(altas: pd.DataFrame, credito: pd.DataFrame | None = None, entidad: str = "Entidad",
                    ruta: str | None = None, umbral: float = UMBRAL, n_min: int = N_MINIMO,
                    representacion: pd.DataFrame | None = None) -> str:
    r = calcular_todo(altas, credito, umbral, n_min)
    sec_rep = ""
    if representacion is not None:
        from .representacion import representacion as _rep
        rp = _rep(representacion, umbral, n_min)
        sec_rep = ("<h2>8 bis. ¿Quién ni siquiera lo intenta? Representación frente a la población</h2>"
                   "<p><small>Proporción del grupo en los intentos / proporción en la población adulta del área de servicio (1 = igualdad). "
                   "Una menor representación es una señal, no una prueba: puede deberse a menor demanda.</small></p>"
                   + _tabla_html([(html.escape(str(x.grupo)), pc(x.poblacion_pct, 1), pc(x.cuota_intentos, 1),
                                   f"{f2(x.cociente)} <small>[{f2(x.ic_inf)}-{f2(x.ic_sup)}]</small>", _chip(x.senal)) for x in rp.itertuples()],
                                 ["Grupo", "En la población", "En los intentos", "Representación", "Señal"]))
    emb, coc, diag, tr = r["embudo"], r["cocientes"], r["diagnostico"], r["trazabilidad"]
    # 1. conclusiones en lenguaje llano (señales observadas, no causas)
    concl = []
    if coc.empty:
        concl.append("<div class='alert'>No hay perfil de referencia («estandar»): no se pueden calcular comparaciones.</div>")
    else:
        vista_final = "acceso_efectivo" if r["con_credito"] else "acceso_cuenta"
        for p in diag.index:
            etapas = diag.loc[p, "etapas"]
            if not etapas:
                continue
            x = coc[(coc.perfil == p) & (coc.vista == vista_final)].iloc[0]
            ap = coc[(coc.perfil == p) & (coc.vista == "aprobacion")]
            extra = ""
            if etapas[0] == "alta" and len(ap) and ap.iloc[0].senal == "Sin señal":
                extra = (" Entre los casos evaluados no se observa una disparidad agregada de aprobación, por lo que una auditoría"
                         " limitada a la decisión no mostraría esta diferencia.")
            elif etapas[0] == "datos":
                extra = " Consigue la cuenta en proporción similar, pero una parte menor llega a ser evaluada."
            elif etapas[0] == "decision":
                extra = (" Se observa una diferencia de aprobación entre evaluados. Es descriptiva: puede reflejar diferencias de riesgo,"
                         " variables del sistema o la selección previa, y requiere una revisión técnica del propio sistema.")
            concl.append(f"<div class='alert'><b>{html.escape(nombre(p))}.</b> Por cada 100 personas del perfil de referencia que "
                         f"{'obtienen crédito' if r['con_credito'] else 'consiguen la cuenta'}, lo consiguen {x.cociente*100:.0f} de este perfil "
                         f"(IC 95 %: {x.ic_inf*100:.0f}-{x.ic_sup*100:.0f}). Primera etapa con señal: <b>{ETAPAS[etapas[0]].lower()}</b>.{extra}</div>")
        if not concl:
            concl.append(f"<div class='ok'>Ningún perfil queda por debajo del umbral de {f2(umbral)}.</div>")
    # 2. perfiles
    t_perf = _tabla_html([(f"<b>{html.escape(v[0])}</b>", html.escape(v[1]), html.escape(v[2]),
                           f"{int(emb.loc[k,'intentos']):,}".replace(",", ".") if k in emb.index else "—")
                          for k, v in PERFILES.items() if k in emb.index],
                         ["Perfil de entrada", "Por qué el alta puede fallar", "Ejemplo", "Intentos"], alinear_izq=3)
    # 3. tabla de cocientes
    vistas = [v for v in ("acceso_cuenta", "llega_modelo", "aprobacion", "acceso_efectivo") if v in set(coc.vista)] if not coc.empty else []
    filas = []
    for p in diag.index if not coc.empty else []:
        f = [html.escape(nombre(p))]
        for v in vistas:
            x = coc[(coc.perfil == p) & (coc.vista == v)].iloc[0]
            f.append(f"{f2(x.cociente)} <small>[{f2(x.ic_inf)}-{f2(x.ic_sup)}]</small><br>{_chip(x.senal)}")
        f.append(html.escape(diag.loc[p, "donde"]))
        filas.append(f)
    t_coc = _tabla_html(filas, ["Perfil"] + [VISTAS[v][0].split(" (")[0] for v in vistas] + ["Etapas con señal"])
    img_coc = _png(fig_cocientes(coc, umbral)) if not coc.empty else ""
    img_can = _png(fig_canal(r["canal"]))
    # embudo
    t_emb = _tabla_html([(html.escape(nombre(p)), f"{int(x.intentos):,}".replace(",", "."), pc(x.tasa_acceso, 1),
                          pc(x.tasa_llega_modelo, 1) if r["con_credito"] else "—", pc(x.tasa_aprobacion_evaluados, 1) if r["con_credito"] else "—",
                          pc(x.tasa_evaluabilidad, 1) if r["con_credito"] else "—", pc(x.tasa_acceso_efectivo, 1) if r["con_credito"] else "—")
                         for p, x in emb.iterrows()],
                        ["Perfil", "Intentos", "Con cuenta (de los intentos)", "Evaluados (de los que tienen cuenta)", "Aprobados (de los evaluados)",
                         "Evaluabilidad acumulada", "Obtiene crédito (de los intentos)"])
    # causas
    ca = r["causas"]
    t_cau = _tabla_html([[html.escape(nombre(p))] + [pc(ca.loc[p, c]) for c in ca.columns] for p in ca.index],
                        ["Perfil"] + [NOMBRES_CAUSA.get(c, c) for c in ca.columns]) if len(ca) else "<p><small>Modo básico: el registro no incluye causas de no acceso.</small></p>"
    t_tr = _tabla_html([(html.escape(nombre(p)), int(x.no_acceso), pc(x.recuperacion), pc(x.con_causa_registrada), pc(x.negativa_escrita), pc(x.alternativa_ofrecida),
                         pc(x.reversion_tras_revision), "—" if pd.isna(x.dias_resolucion_mediana) else f"{x.dias_resolucion_mediana:.0f}")
                        for p, x in tr.iterrows()],
                       ["Perfil", "Sin acceso", "Recuperación tras fallo", "Con causa registrada", "Negativa por escrito", "Alternativa ofrecida", "Revertidas tras revisión", "Días (mediana)"])
    avisos = "".join(f"<li>{html.escape(a)}</li>" for a in r["avisos"]) or "<li>Sin incidencias de calidad de datos.</li>"
    hoy = datetime.date.today().isoformat()
    modo = "completo" if r["modo"] == "completo" else "básico (sin causas de no acceso)"
    doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Informe de evaluabilidad</title><style>{CSS}</style></head><body>
<h1>Informe de evaluabilidad y gobernanza del no acceso</h1>
<p class="sub">{html.escape(entidad)} · generado el {hoy} · kit «evaluabilidad» v0.4 · modo {modo} · umbral de revisión {f2(umbral)}</p>
<h2>1. Conclusiones</h2>{''.join(concl)}
<h2>2. Perfiles de entrada analizados</h2><p><small>Un perfil describe la credencial o la situación del intento de alta, no a la persona. Cada perfil se compara con el de referencia.</small></p>{t_perf}
<h2>3. En qué etapa aparece la diferencia</h2>
{f'<img alt="Cocientes por perfil y vista" src="data:image/png;base64,{img_coc}">' if img_coc else ''}
{t_coc}
<p><small>Cociente = tasa del perfil / tasa del perfil de referencia. Entre corchetes, intervalo de confianza del 95 %. «Señal clara»: por debajo del umbral y diferencia estadísticamente clara. «A confirmar»: por debajo del umbral, pero con incertidumbre o menos de {n_min} casos. Cada etapa se mide sobre quienes superaron la anterior, para localizar dónde aparece la primera señal sin arrastrar las pérdidas previas.</small></p>
<h2>4. Acceso por canal</h2><p><small>% de intentos que terminan con cuenta.</small></p><img alt="Acceso por perfil y canal" src="data:image/png;base64,{img_can}">
<h2>5. Embudo por perfil</h2>{t_emb}
<h2>6. Causas de no acceso</h2><p><small>% de los casos sin acceso de cada perfil.</small></p>{t_cau}
<h2>7. Trazabilidad y proporcionalidad</h2><p><small>Recuperación tras fallo: de los intentos que no terminaron en un alta ordinaria, porcentaje que obtuvo una cuenta por una vía alternativa. Que la tecnología falle es inevitable; la señal de gobernanza es que no exista una vía proporcional para recuperar a la persona.</small></p>{t_tr}
<h2>8. Dónde incorporar cada resultado</h2>
{_tabla_html([("Perfiles con señal en el alta o al llegar al modelo", "FRIA, Reglamento (UE) 2024/1689, art. 27 (categorías de personas afectadas); DPIA, RGPD art. 35"),
              ("Representatividad de los datos de entrada que controla la entidad", "Reglamento de IA art. 26.4 (responsable del despliegue)"),
              ("Lagunas en los datos de entrenamiento, validación y prueba", "Reglamento de IA art. 10.2 f)-h) (proveedor del sistema)"),
              ("Perfiles con diferencia en la aprobación entre evaluados", "Gestión de riesgos, art. 9; pruebas técnicas del propio sistema"),
              ("Serie temporal de cocientes y causas", "Supervisión del funcionamiento por el responsable del despliegue, art. 26.5; vigilancia poscomercialización del proveedor, art. 72"),
              ("Alternativas ofrecidas antes del rechazo", "Directrices EBA/GL/2023/04 (párrs. 12 y 20-21); Reglamento (UE) 2024/1624"),
              ("Negativas por escrito y causas registradas", "Real Decreto-ley 19/2017, art. 5; RGPD arts. 15 y 22"),
              ("Revisión humana y reversión", "Reglamento de IA arts. 14 y 86; Directiva (UE) 2023/2225, art. 18")],
             ["Resultado", "Dónde se incorpora"], alinear_izq=2)}
{sec_rep}
<h2>9. Calidad de los datos</h2><ul>{avisos}</ul>
<h2>10. Límites</h2><p><small>El informe mide asociaciones agregadas, no causalidad ni discriminación. Indica en qué etapa se observa una diferencia, no por qué se produce. Requiere registros comparables de cada etapa (intento, cuenta, evaluación, decisión) enlazados por un identificador. El umbral de revisión (por defecto 0,80, referencia convencional de «cuatro quintos») es una regla práctica, no un criterio jurídico de la UE, y puede ajustarse. Un perfil describe la credencial o la situación del intento, no a la persona; el registro no debe incorporar nacionalidad ni categorías especiales de datos. Cualquier análisis adicional con esas categorías requiere base jurídica propia (RGPD; Reglamento de IA, art. 4 bis, antes art. 10.5, que sólo cubre la detección de sesgos en los sistemas de IA).</small></p>
</body></html>"""
    if ruta:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(doc)
    return doc

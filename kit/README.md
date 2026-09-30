# Evaluability · AI & Data Governance · Banking – Open Source

**Auditoría abierta del acceso antes del modelo de crédito** — kit abierto de gobernanza del no acceso (paquete Python `evaluabilidad`, v0.3)

**La industria ya audita cómo trata el modelo a quien evalúa. Este kit audita quién llegó a ser evaluado.**

Las pruebas de equidad de los sistemas de solvencia se calculan sobre las solicitudes que llegan al modelo. Si el documento, el domicilio, el canal o la forma de verificar la identidad filtran antes a una parte de las personas, el modelo puede superar esas pruebas y, aun así, la exclusión existe. Este kit hace visible esa etapa con los datos que la entidad ya tiene, e indica para cada perfil **en qué etapa** aparece la primera diferencia: en el alta, al llegar al modelo o en la decisión. Mide asociaciones, no causas.

## Perfiles de entrada

Cada intento de alta se registra con un perfil: la credencial o la situación que el proceso detecta primero, no la persona. Cada perfil se compara con el de referencia.

| Perfil (`perfil_entrada`) | Por qué el alta puede fallar | Ejemplo |
|---|---|---|
| Documento estándar (`estandar`) | Es la referencia: DNI, NIE/TIE o pasaporte con chip que el sistema lee sin incidencias. | Cliente con DNI que se da de alta desde la app. |
| Documento de protección internacional (`proteccion_internacional`) | El lector automático o la lista de documentos admitidos no lo contempla. | Solicitante de asilo con su documento de solicitante. |
| NIE en trámite o resguardo (`nie_provisional`) | Documento provisional, sin chip o sin foto estándar; la verificación automática lo rechaza. | Persona recién llegada, o con el permiso en renovación, que presenta el resguardo. |
| Pasaporte de fuera de la UE sin chip (`pasaporte_sin_chip`) | La verificación automática (lectura NFC o del documento) falla. | Estudiante o trabajador extracomunitario. |
| Sin domicilio fijo o sin justificante (`sin_domicilio`) | Se exige una prueba de dirección que la persona no puede aportar. | Persona que vive en un albergue o en un alquiler informal. |
| Necesita asistencia en la verificación digital (`asistencia_digital`) | Falla el selfie, la videoidentificación o el SMS, o la persona no puede completarlos sola. | Persona mayor o sin smartphone reciente. |
| Sin historial crediticio (`sin_historial`) | Suele abrir la cuenta sin problema, pero llega al modelo con pocos datos o no llega a ser evaluable. | Joven con su primer empleo o persona recién llegada al país. |
| Otro perfil no estándar (`otro`) | Cualquier otra credencial o situación válida que el proceso no reconoce bien. | Definirlo en la política interna antes de usarlo. |

La definición vive en `evaluabilidad/perfiles.py`; la web la toma de ahí al construirse.

## Qué mide

Vistas **por etapa**: cada una se mide sobre quienes superaron la anterior, para localizar dónde aparece la primera señal sin arrastrar las pérdidas previas.

| Etapa | Pregunta | Cálculo por perfil |
|---|---|---|
| Alta | ¿Consigue la cuenta? | con cuenta / intentos |
| Llegada al modelo | Con cuenta, ¿llega a ser evaluado? | evaluados / con cuenta |
| Decisión | Entre evaluados, ¿hay diferencia en la aprobación? | aprobados / evaluados |

Vistas **acumuladas**, que resumen el efecto total y alimentan las conclusiones:

| Vista | Cálculo por perfil |
|---|---|
| Evaluabilidad (concepto del ensayo) | evaluados / intentos |
| Acceso efectivo | aprobados / intentos |

Una diferencia en la decisión es descriptiva: puede reflejar diferencias de riesgo, variables del sistema o la selección previa, y requiere una revisión técnica del propio sistema.

Cada cociente (perfil / referencia) lleva un **intervalo de confianza del 95 %** y una señal: **Señal clara** (por debajo del umbral y diferencia estadísticamente clara), **A confirmar** (por debajo del umbral, pero con incertidumbre o menos de 100 casos, mínimo configurable con `--n-min`) o **Sin señal**. El intervalo es el de Katz para el cociente de riesgos (idéntico a `scipy.stats.contingency.relative_risk`; los tests lo comprueban), con corrección de Haldane-Anscombe cuando el perfil tiene cero éxitos. El **umbral de revisión** es 0,80 por defecto (la referencia convencional de «cuatro quintos») y es configurable: es una regla práctica, no un criterio jurídico de la UE.

## Dos modos

- **Básico** — con datos que casi cualquier entidad ya tiene: `id_intento`, `fecha`, `canal`, `perfil_entrada`, `resultado`. Sin decisiones de crédito, compara sólo el acceso a la cuenta por perfil y canal.
- **Completo** — añade la causa de no acceso (nueve causas normalizadas), la trazabilidad (negativa escrita, alternativa ofrecida, revisión humana y reversión) y las decisiones de crédito (`id_intento`, `aprobado`).

## Componentes

| Componente | Para qué sirve |
|---|---|
| `esquema/registro_no_acceso.schema.json` | Estándar de registro de cada intento de alta, con minimización de datos: sin nombre, número de documento, nacionalidad ni edad. |
| `evaluabilidad/` (Python) | Calcula embudo, cocientes con IC, diagnóstico de dónde se produce la diferencia, causas, canal y trazabilidad, y genera el informe. |
| Informe HTML | Autocontenido, con una tabla que indica dónde incorporar cada resultado: DPIA (RGPD art. 35), FRIA (Reglamento de IA art. 27), art. 10, art. 72, EBA/GL/2023/04, RDL 19/2017. |
| `plantillas/` | Formulario de solicitud de cuenta de pago básica y lista de comprobación del alta por perfil. |
| `demo/` | 40.000 intentos sintéticos con siete perfiles e informe de ejemplo. |
| `web/` | Plantilla de la versión web; `construir_web.py` genera `docs/index.html`. |

## Uso

**Sin instalar nada:** https://fernandasvilla.github.io/AI-and-Data-Governance-Banking/ — pulsa «Ver ejemplo» o carga tus CSV. Los cálculos se hacen en el navegador y los datos no salen del equipo.

**En Python:**

```bash
pip install pandas matplotlib
cd kit
python demo/generar_datos_demo.py                     # datos sintéticos (idénticos a los de la web)
python -m evaluabilidad --altas demo/altas_demo.csv --credito demo/credito_demo.csv \
       --salida informe.html --entidad "Mi entidad" --umbral 0.8
python -m evaluabilidad --altas mis_altas.csv --salida informe.html   # modo básico, sin crédito
python -m pytest tests
```

La columna `categoria_documental` de la v0.1 (`estandar` / `no_estandar`) se sigue aceptando.

## Cómo encaja con otras herramientas

Úsalo **antes** de las pruebas de equidad del modelo, no en su lugar. Primero comprueba si la población que llega al modelo está filtrada en la entrada; después, una prueba sobre el propio modelo —por ejemplo, con comparadores contrafactuales— comprueba si trata igual a quienes sí entraron.

## Comparación con una auditoría convencional

`auditoria_convencional()` aplica los controles habituales de calidad de datos (nulos, duplicados, dominios, formatos y rangos) para comparar. Sobre el ejemplo sólo encuentra nulos estructurales: revisa columnas, no compara resultados entre perfiles. `src/comparacion_auditorias.py` mide, con verdad conocida, qué detecta cada auditoría: la de equidad del modelo detecta menos del 1 % de las pérdidas producidas en el alta o antes de llegar al modelo; el kit, el 99-100 %.

## Modo encuesta (experimental)

Para probar la lógica del kit con **datos públicos** mientras no hay registros de una entidad, `evaluabilidad.encuestas` la aplica a microdatos de encuestas (por ejemplo, Global Findex o las encuestas de población desplazada de ACNUR publicadas en su biblioteca de microdatos).

- La unidad es la persona, no el intento: una encuesta pregunta quién *tiene* cuenta, no quién lo intentó y fue rechazado. Por eso sólo se mide con rigor la primera etapa; el crédito formal se muestra como indicador descriptivo, y las razones de no tener cuenta son autodeclaradas.
- Usa los **pesos muestrales** y, si la encuesta los publica, **estrato y conglomerado**: el intervalo del cociente se calcula por linealización de Taylor. Con pesos iguales y sin conglomerados coincide con el intervalo del modo de registros (los tests lo comprueban).
- **Control de divulgación**: sólo se guardan resultados agregados y se suprimen las celdas con menos de 30 observaciones. Los microdatos se descargan de su fuente, se guardan en `microdatos/` (excluida del repositorio) y no se redistribuyen.

```bash
python src/encuestas/ejecutar.py --explorar microdatos/archivo.dta        # variables candidatas
python src/encuestas/ejecutar.py --fuente acnur_jordania --archivo microdatos/archivo.dta
```

Los adaptadores de cada fuente están en `src/encuestas/fuentes.py`.

## Estado y límites

Prototipo funcional (v0.3) probado con datos sintéticos; no se ha validado aún con datos de una entidad. Mide asociaciones agregadas, no causalidad ni discriminación: indica en qué etapa se observa una diferencia, no por qué se produce. Requiere registros comparables de cada etapa (intento, cuenta, evaluación y decisión) enlazados por un identificador. Un perfil describe la credencial o la situación del intento, no a la persona. Cualquier análisis adicional con categorías especiales de datos requiere base jurídica propia (RGPD; Reglamento de IA art. 10.5).

Parte del ensayo *Gobernar antes del algoritmo: IA, Data Governance y prevención de la exclusión financiera ante el nuevo marco regulatorio europeo de la IA* (Sánchez Villa, 2026). Licencia Apache 2.0 (véanse `LICENSE` y `NOTICE` en la raíz del repositorio).

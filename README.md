# AI and Data Governance · Banking – Open Source

**Gobernar antes del algoritmo:** código, datos, simulación y kit abierto para auditar quién llega a ser evaluado por un modelo de crédito.

### 👉 [Abrir la herramienta web](https://fernandasvilla.github.io/AI-and-Data-Governance-Banking/) · [English version](https://fernandasvilla.github.io/AI-and-Data-Governance-Banking/?lang=en)

https://fernandasvilla.github.io/AI-and-Data-Governance-Banking/

El archivo de la web es [`docs/index.html`](docs/index.html): se puede descargar y abrir en cualquier navegador, sin instalar nada.

*Open toolkit to audit who reaches credit models: pre-model financial exclusion, evaluability and non-entry governance. Python + bilingual web (ES/EN). English overview: [`kit/README_EN.md`](kit/README_EN.md).*

Material reproducible del ensayo *Gobernar antes del algoritmo: IA, Data Governance y prevención de la exclusión financiera ante el nuevo marco regulatorio de la Unión Europea* (María Fernanda Sánchez Villa, 2026).


## Verificar en 3 minutos

1. **A mano:** abra `kit/verificacion/verificacion_altas.csv` en Excel (200 intentos, 100 por perfil). Con cuenta: 96 de 100 en el perfil de referencia y 43 de 100 con documento de protección internacional. R₁ = (43/100) / (96/100) = **0,45**; la calculadora web da 0,45 (IC 95 %: 0,36–0,56).
2. **Ejemplo del ensayo:** en la web, «Calcular con datos de ejemplo» reproduce la figura 7 (0,44 en el alta; 0,60 al llegar al modelo para el perfil sin historial).
3. **Datos reales:** «Calcular con datos del Banco Mundial» (en «Verificar») reproduce el 0,45 de Global Findex 2025 (sección 3.4). El apartado «La herramienta con datos españoles reales y abiertos» aplica el método a dos tablas oficiales españolas: Banco de España (Encuesta de Competencias Financieras 2021) y Eurostat (banca por internet, 2024).
4. **Con Python:** `pip install -r requirements.txt` y `pytest kit/tests` → 21 pruebas superadas.

## Contenido

Datos públicos adicionales: `data/eurostat_banca_internet_discapacidad_2024.csv` (Eurostat, dsb_ictiu07, banca por internet según limitación de actividad, España y UE-27, 2024).


| Carpeta | Qué contiene |
|---|---|
| `auditoria/` | Revisión documental de la información pública de 15 entidades (sección 3.3): libro de códigos y codificación anonimizada por tipo de entidad. La identificación, las citas textuales y los enlaces están a disposición del jurado y de revisores académicos que lo soliciten |
| `docs/` | **Versión web del kit, en español e inglés** (GitHub Pages): https://fernandasvilla.github.io/AI-and-Data-Governance-Banking/ (inglés: `?lang=en`) — todo se calcula en el navegador, sin recursos de terceros |
| `kit/` | **Kit abierto de gobernanza del no acceso** (`evaluabilidad` v0.4): mide, para nueve perfiles de entrada frente al de referencia (documentación, tecnología y competencias digitales, accesibilidad, territorio —zona sin oficina o movilidad reducida— y falta de historial; seis de ellos afectan también a personas con DNI), quién se queda sin cuenta, por qué y en qué etapa aparece la primera diferencia: en el alta, al llegar al modelo o en la decisión. Sirve para cualquier forma de decisión (regla de software, persona o IA). Compara además quién intenta abrir una cuenta con la población del área de servicio, para acercarse a quien ni siquiera lo intenta. Esquema, paquete Python, informe HTML, plantillas y demo (sección 7.5) |
| `data/` | Datos públicos transcritos de sus fuentes originales (CSV, con fuente y página por fila) y resultados de la simulación |
| `src/simulacion_evaluabilidad.py` | Simulación del mecanismo *evaluación frente a evaluabilidad* (sección 3.2 del ensayo) |
| `src/sensibilidad.py` | Siete variantes de la simulación para comprobar la robustez cualitativa |
| `src/figuras.py` | Genera las figuras 1, 2 y 3 y la figura D.1 (México, anexo D) del ensayo |
| `src/figura_auditoria.py` | Genera la figura 4 (matriz de la revisión documental) |
| `src/figura_kit.py` | Genera la figura 7 (informe del kit sobre datos sintéticos); `figura_metodo.py` genera la figura 6 (esquema del método) |
| `src/validacion_metodo.py` | Validación del método por simulación: cobertura del IC 95 %, potencia y falsas alarmas (tabla 12 del ensayo) |
| `src/encuestas/` | Modo encuesta: adaptadores y ejecución sobre microdatos públicos; sólo publica resultados agregados |
| `src/encuestas/findex_documento.py`, `findex_ajuste.py` | Global Findex 2025: acceso a cuenta con y sin documento de identidad en 123 economías, por región, descriptivo y ajustado. Resultados en `data/encuestas/` |
| `src/encuestas/findex_condiciones.py`, `figura_findex.py` | Global Findex 2025: acceso a cuenta según la condición de entrada (documento, teléfono, internet) y porcentaje de adultos sin cuenta que necesitarían ayuda (figura 5 y sección 3.4 del ensayo) |
| `src/encuestas/findex_descomposicion.py` | Descomposición en dos etapas de la brecha de crédito formal (Global Findex 2025): qué parte se produce ya en el acceso a la cuenta. Resultados en `data/encuestas/findex2025_descomposicion*.csv`, con la versión para los cuatro Estados miembros de la UE con la pregunta de crédito en `_ue.csv` (tabla 7 y sección 3.4) |
| `src/encuestas/findex_efectivo.py` | El dinero que no se registra: proporción de adultos que cobran su ingreso regular o pagan sus suministros sólo en efectivo en los cuatro Estados miembros de la UE con esas preguntas en Global Findex 2025. Resultados en `data/encuestas/findex2025_efectivo_ue4.csv` (secciones 3.4 y 5.5) |
| `src/figuras_anexo.py` | Figuras C.1 a C.3 del anexo C (un punto por economía, descomposición de la brecha de crédito y dinero que no se registra), con la misma paleta que `src/figuras.py` |
| `src/encuestas/findex_ue.py` | Global Findex 2025 sólo en la Unión Europea (26 economías): sin documento (0,96, sin señal) y sin uso de internet (0,74; 0,82 ajustado). Resultados en `data/encuestas/findex2025_ue_condiciones.csv` (sección 3.4) |
| `src/comparacion_auditorias.py` | Qué detecta cada auditoría (calidad de datos convencional, equidad del modelo y kit) en escenarios con verdad conocida (tabla C.3 del anexo C del ensayo) |
| `figures/` | Figuras en PNG (300 ppp) |

## Cómo reproducir

```bash
pip install numpy pandas scikit-learn matplotlib
cd src
python simulacion_evaluabilidad.py   # ~1 minuto; escribe data/simulacion_*.csv
python sensibilidad.py
python figuras.py
python figura_auditoria.py
python figura_kit.py
python validacion_metodo.py
python figura_metodo.py
python figuras_anexo.py
```

## Fuentes de datos

- Banco de España (2026). *Informe de Inclusión Financiera 2025*. Cuadro 3.1 (Encuesta de Competencias Financieras 2021), pp. 43-45; cuentas de pago básicas y cobertura, pp. 48-50 y nota 18. Estimaciones de población en situación irregular de Funcas (2026), citadas en la p. 48.
- Banorte (31 jul. 2024; 10 jul. 2026), comunicados sobre la cuenta Enlace Digital para personas refugiadas; El Universal (jul. 2026).
- Diario Oficial de la Federación: disposiciones del art. 115 de la Ley de Instituciones de Crédito (28 ago. 2024), límite de la cuenta nivel 2 (3.000 UDIS); valor de la UDI al 28/09/2026.

## Advertencia sobre la simulación

La simulación ilustra un **mecanismo**; no estima la situación de ninguna entidad ni colectivo real. Todos los parámetros son supuestos explícitos (`PARAMS` en `simulacion_evaluabilidad.py`) y pueden modificarse. Ambos grupos tienen, por construcción, la misma distribución de solvencia.

## Licencia

Código: Apache License 2.0 (véanse `LICENSE` y `NOTICE`). Figuras, textos y codificación de la auditoría: CC BY 4.0. Datos transcritos: se mantienen los términos de sus fuentes originales; cítense las fuentes primarias.

## Datos de terceros

Los microdatos de **Global Findex 2025** (Banco Mundial, uso público, DOI [10.48529/bk9n-8r43](https://doi.org/10.48529/bk9n-8r43)) no se incluyen en el repositorio: descárguelos en formato Stata desde la [Microdata Library del Banco Mundial](https://microdata.worldbank.org/catalog/7860/study-description) y guárdelos en `microdatos/wld/`. El repositorio sólo publica resultados agregados, con las celdas de menos de 30 observaciones suprimidas. Cita: Development Research Group, Finance and Private Sector Development Unit. (2025). *The Global Findex Database 2025: Connectivity and Financial Inclusion in the Digital Economy* [Dataset]. World Bank, Development Data Group. https://doi.org/10.48529/BK9N-8R43 (WLD_2024_FINDEX_v02_M).

La calculadora web incluye un conjunto de prueba con estos datos («Calcular con datos del Banco Mundial»). No contiene microdatos: se reconstruye con el número de personas encuestadas y la proporción ponderada con cuenta de `data/encuestas/findex2025_condiciones.csv`.

# AI and Data Governance · Banking – Open Source

**Gobernar antes del algoritmo:** código, datos, simulación y kit abierto para auditar quién llega a ser evaluado por un modelo de crédito.

*Open toolkit to audit who reaches credit models: pre-model financial exclusion, evaluability and non-entry governance. Python + bilingual web (ES/EN). English overview: [`kit/README_EN.md`](kit/README_EN.md).*

Material reproducible del ensayo *Gobernar antes del algoritmo: IA, Data Governance y prevención de la exclusión financiera ante el nuevo marco regulatorio europeo de la IA* (María Fernanda Sánchez Villa, 2026).

## Contenido

| Carpeta | Qué contiene |
|---|---|
| `auditoria/` | Auditoría documental de 15 entidades (sección 3.3): libro de códigos y codificación anonimizada por tipo de entidad. La identificación, las citas textuales y los enlaces están a disposición del jurado y de revisores académicos que lo soliciten |
| `docs/` | **Versión web del kit, en español e inglés** (GitHub Pages): https://fernandasvilla.github.io/AI-and-Data-Governance-Banking/ (inglés: `?lang=en`) — todo se calcula en el navegador, sin recursos de terceros |
| `kit/` | **Kit abierto de gobernanza del no acceso** (`evaluabilidad` v0.3): mide, para seis perfiles de entrada frente al de referencia (documento de protección internacional, NIE provisional, pasaporte sin chip, sin domicilio, asistencia digital, sin historial…), en qué etapa aparece la primera diferencia: en el alta, al llegar al modelo o en la decisión. Esquema, paquete Python, informe HTML, plantillas y demo (sección 8.6) |
| `data/` | Datos públicos transcritos de sus fuentes originales (CSV, con fuente y página por fila) y resultados de la simulación |
| `src/simulacion_evaluabilidad.py` | Simulación del mecanismo *evaluación frente a evaluabilidad* (sección 3.2 del ensayo) |
| `src/sensibilidad.py` | Siete variantes de la simulación para comprobar la robustez cualitativa |
| `src/figuras.py` | Genera las figuras 1, 2, 3 y 5 del ensayo |
| `src/figura_auditoria.py` | Genera la figura 4 (matriz de la auditoría) |
| `src/figura_kit.py` | Genera la figura 6 (informe del kit sobre datos sintéticos) |
| `src/validacion_metodo.py` | Validación del método por simulación: cobertura del IC 95 %, potencia y falsas alarmas (tabla 10 del ensayo) |
| `src/encuestas/` | Modo encuesta: adaptadores y ejecución sobre microdatos públicos; sólo publica resultados agregados |
| `src/encuestas/findex_documento.py`, `findex_ajuste.py`, `figura_findex.py` | Global Findex 2025: acceso a cuenta con y sin documento de identidad en 123 economías, descriptivo y ajustado (figura 8 del ensayo). Resultados en `data/encuestas/` |
| `src/comparacion_auditorias.py` | Qué detecta cada auditoría (calidad de datos convencional, equidad del modelo y kit) en escenarios con verdad conocida (tabla 11 del ensayo) |
| `src/escenarios_anclados.py` | Escenarios del perfil de protección internacional anclados en la auditoría (sección 8.6) |
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
python escenarios_anclados.py
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

Los microdatos de **Global Findex 2025** (Banco Mundial, uso público, DOI [10.48529/bk9n-8r43](https://doi.org/10.48529/bk9n-8r43)) no se incluyen en el repositorio: descárguelos en formato Stata desde la Microdata Library y guárdelos en `microdatos/wld/`. El repositorio sólo publica resultados agregados, con las celdas de menos de 30 observaciones suprimidas. Cita: World Bank (2025), *The Global Findex Database 2025: Connectivity and Financial Inclusion in the Digital Economy*, WLD_2024_FINDEX_v02_M.

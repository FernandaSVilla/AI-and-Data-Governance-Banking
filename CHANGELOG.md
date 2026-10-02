# Cambios

## v0.4 — octubre de 2026
- Nuevo: **¿quién ni siquiera lo intenta?** (`evaluabilidad/representacion.py`). Compara la composición de los intentos de alta con la de la población del área de servicio: Rᴿ = (x_g / N) / π_g, con intervalo de Wilson y la misma regla de señal. Entrada agregada (grupo, intentos_grupo, intentos_total, poblacion_pct); datos de ejemplo ilustrativos en `kit/demo/representacion_demo.csv`. Es una señal, no una prueba: un grupo puede intentarlo menos por menor demanda.
- Nuevo apartado en la web, **«La herramienta con datos españoles reales y abiertos»**, con dos botones: Banco de España (Encuesta de Competencias Financieras 2021, cuadro 3.1: nacidos fuera frente a nacidos en España, en cuenta, tarjeta, hipoteca, rechazo y autoexclusión por miedo al rechazo) y Eurostat (banca por internet en España en 2024 por limitación de actividad y edad, con la UE-27 como contraste). Son tablas publicadas sin tamaño de grupo: cociente descriptivo, sin intervalo.
- La web se abre en español, con el informe de ejemplo ya calculado y todas las secciones desplegadas; el título indica que sirve igual si decide una regla de software, una persona o una IA.
- Línea de comandos: `--representacion`. Dos pruebas nuevas (21 en total).

## v0.3.2 — octubre de 2026 (ensayo v38)
- Ajusté las referencias de la web, el kit y el README a la nueva numeración del ensayo: el kit está en la sección 7.5 y la taxonomía de causas en la 7.2; el esquema del método es la figura 6, el informe del kit la figura 7, la validación la tabla 12 y la comparación de auditorías la tabla C.3; la figura de México pasa al anexo D.
- La web dice ahora que el deber de comunicar por escrito una negativa nace con la solicitud completa (Real Decreto-ley 19/2017, art. 5), por lo que quien es disuadido antes sólo aparece si se registra cada intento, y que el informe es un instrumento interno de mejora que se comparte con el supervisor sólo en agregado.
- La habilitación para tratar categorías especiales con el fin de detectar sesgos se cita como art. 4 bis del Reglamento de IA (antes art. 10.5).
- Los parámetros del perfil de protección internacional en los datos de ejemplo se describen como supuestos de escenario orientados por la revisión documental, no estimados a partir de ella. Los datos no cambian.
- Quité el bloque BibTeX de la web; «Cómo citar» queda con la cita en texto de la herramienta y de los datos del Banco Mundial.
- El README empieza con un enlace directo a la herramienta web.
- Limpié el repositorio: quité capturas de pantalla de prueba, la figura de regiones y el gráfico de validación que el ensayo no usa, y el análisis de escenarios anclados, que la v38 ya no incluye. Las figuras se renombran con la numeración del ensayo (fig6_metodo, fig7_kit_informe_demo, figD1_mexico_uso_vs_tope).
- El README dice que seis perfiles afectan también a personas con DNI (antes decía cinco, por error) y que hay 19 pruebas.

## Octubre de 2026 (ensayo, v32)
- Las figuras se renumeraron porque Global Findex pasa a la sección 3.4 del ensayo: `fig5_findex_condiciones`, `fig6_mexico_uso_vs_tope`, `fig7_metodo`, `fig8_kit_informe_demo`.
- Nuevo `src/encuestas/findex_descomposicion.py`: qué parte de la brecha de crédito formal se produce ya en el acceso a la cuenta (descomposición de Shapley con intervalos por bootstrap), con su prueba automática. Las tablas del ensayo se renumeran (nueva tabla 7).
- Nuevo `src/encuestas/findex_ue.py`: el análisis de Findex repetido sólo con las economías de la UE.
- La descomposición se repite para los cuatro Estados miembros de la UE en los que Findex pregunta por el crédito formal (Bulgaria, Croacia, Polonia y Rumanía), agregados y por país, en `data/encuestas/findex2025_descomposicion_ue.csv` (última fila de la tabla 7). Sólo la condición «sin internet» tiene casos suficientes. Las cifras globales no cambian.
- Nuevo `src/encuestas/findex_efectivo.py`: en esos cuatro países, quién cobra su salario, pensión o transferencia y paga sus suministros sólo en efectivo, por tenencia de cuenta y uso de internet. Sostiene la nueva sección 5.5 del ensayo (el dinero que no se registra y sus consecuencias para la DPIA y la FRIA).
- Nuevo `src/figuras_anexo.py` y anexo C del ensayo: dos tablas en formato académico (cocientes descriptivos y ajustados; robustez de la descomposición con las dos ordenaciones de Shapley) y tres figuras. Al revisar la robustez vi que en la UE-4 el rango entre ordenaciones es amplio (13-54 %), y así lo digo en el ensayo.

## v0.3.1 — octubre de 2026
- Corregí un error en la simulación del ensayo (`src/simulacion_evaluabilidad.py`): la muestra final tomaba la mitad de las personas evaluables pero a todas las no evaluables, y eso exageraba la pérdida del grupo B. Con la corrección, el acceso al crédito baja de 4/5 cuando la tasa de alta del grupo B es inferior a 0,69 (antes salía 0,81). La conclusión se mantiene; el efecto es menor.
- Ajusté las referencias al Reglamento de IA: la vigilancia del art. 72 corresponde al proveedor; el banco que usa el sistema supervisa su funcionamiento (art. 26.5).
- La web es más sencilla: lo técnico (método, perfiles, detalle del informe) queda plegado. Añadí un botón y un CSV descargable con los datos públicos de Global Findex 2025 (reconstruidos a partir de los agregados, no microdatos) para que cualquiera pueda probar la herramienta con datos reales. Con esos datos el informe muestra sólo lo que una encuesta puede medir (tenencia de cuenta) y la cita oficial del Banco Mundial.
- El informe empieza ahora por el no acceso: cuántos intentos terminaron sin cuenta, en qué canal, por qué, si la negativa fue por escrito, si se ofreció una alternativa y cuántos se recuperaron. La evaluabilidad (si llegan al modelo de crédito) va después.
- Nuevo perfil «Sin oficina accesible (zona rural o movilidad reducida)». Los datos de ejemplo suman un bloque de 6.000 intentos con tres perfiles que afectan también a personas con DNI (ayuda digital, accesibilidad, sin oficina); los 40.000 intentos originales no cambian.
- La web muestra el método como un esquema con las fórmulas y un ejemplo numérico, y agrupa los perfiles por tipo de barrera.
- Añadí «Verificar en 3 minutos»: un archivo de 200 intentos que se puede contar a mano en Excel (`kit/verificacion/`), con su prueba automática, y las cifras esperadas para el ejemplo y para Global Findex. Las pruebas se pueden ejecutar ahora desde la raíz (`pytest kit/tests`).
- La web empieza ahora con la idea en una frase y tres cifras (96, 43 y 57 de cada 100), explica qué es la gobernanza del no acceso con ejemplos y de dónde salen los datos, destaca las negativas por escrito y cita el Reglamento de IA en la parte de evaluabilidad. Probé la página con lectores no técnicos y la ajusté.
- La web se centra en la herramienta: Global Findex 2025 queda como una comprobación dentro de «Verificar» y los datos de contexto (Banco Mundial por condiciones, Eurostat, Banco de España) se quedan en el ensayo. «Cómo citar» incluye la herramienta, los datos del Banco Mundial y BibTeX.
- Datos de contexto para el ensayo: banca por internet según discapacidad (Eurostat, 2024; `data/eurostat_banca_internet_discapacidad_2024.csv`).

## v0.3.0 — octubre de 2026
Primera versión pública. Antes hubo dos versiones de prueba que no publiqué.

- Cada etapa (alta, llegada al modelo y decisión) se compara ahora sólo con quienes pasaron la anterior, para ver dónde aparece la diferencia.
- Más avisos cuando el registro tiene errores (duplicados, valores raros, decisiones que no cuadran).
- Una prueba con datos públicos de Global Findex 2025.
- Versión web en español e inglés.

Sigue siendo un prototipo: todavía no lo he probado con datos de un banco. Si lo usas y algo no funciona o no tiene sentido, abre un *issue*.

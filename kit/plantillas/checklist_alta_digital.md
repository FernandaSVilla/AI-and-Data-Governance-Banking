# Lista de comprobación: un alta que reconoce a todos los perfiles de entrada

*Para equipos de producto, cumplimiento y experiencia de cliente. Cada «No» es un punto en el que el alta puede dejar fuera a personas con derecho a la cuenta antes de que exista cualquier modelo. Conviene documentarlo en la DPIA (RGPD art. 35) o en la FRIA (Reglamento de IA art. 27).*

## A. Reconocimiento de cada perfil de entrada
| Perfil | Comprobación |
|---|---|
| Documento de protección internacional | [ ] El selector de documentos del alta digital lo incluye y la lectura automática se ha probado con él. |
| NIE en trámite o resguardo | [ ] El proceso admite documentos provisionales y define qué verificación adicional aplica. |
| Pasaporte de fuera de la UE sin chip | [ ] Si falla la lectura NFC, existe una verificación alternativa (lectura óptica, videollamada, oficina). |
| Sin domicilio fijo o sin justificante | [ ] Se admiten alternativas al justificante (declaración responsable, certificado de un servicio social o de un albergue). |
| Móvil o conexión insuficientes para la verificación | [ ] Si falla el selfie, el NFC, el vídeo o el SMS, se ofrece otra vía (videollamada, código por otro medio, cita presencial), no un error genérico. |
| Necesita ayuda para completar el proceso digital | [ ] Hay asistencia humana (teléfono, chat u oficina) y el formulario usa lenguaje claro. |
| Necesita un ajuste de accesibilidad | [ ] El canal funciona con lector de pantalla y no depende sólo de instrucciones visuales o sonoras; se registra el ajuste requerido y si estaba disponible, nunca un diagnóstico (Directiva (UE) 2019/882). |
| Sin historial crediticio | [ ] Se conoce cuántas personas con cuenta no llegan a ser evaluables y se valora el uso de datos alternativos lícitos. |

- [ ] La lista de documentos admitidos está publicada y es coherente entre web, app y oficina.
- [ ] Cuando el canal digital no puede verificar una credencial válida, la pantalla lo explica y ofrece una ruta alternativa concreta.

## B. Registro del no acceso
- [ ] Cada intento de alta interrumpido genera un registro con su perfil de entrada y una de las nueve causas normalizadas (esquema `registro_no_acceso`).
- [ ] Existe un formulario de solicitud de cuenta básica en web y oficina, con número de registro y copia para el solicitante.
- [ ] Las negativas se comunican por escrito y con motivo concreto (RDL 19/2017, art. 5) y se mide el porcentaje que cumple.

## C. Proporcionalidad antes del rechazo
- [ ] Antes de rechazar por riesgo de blanqueo se valora y registra una alternativa (límites de operativa, verificación adicional, seguimiento reforzado) (EBA/GL/2023/04).
- [ ] La alternativa no sustituye el derecho a la cuenta de pago básica cuando se cumplen sus requisitos.

## D. Revisión humana y reversión
- [ ] Los rechazos automáticos del alta pueden escalarse a una persona con capacidad de decidir.
- [ ] Se mide la tasa de reversión tras revisión por perfil de entrada; una tasa alta indica falsos negativos del proceso.

## E. Conexión con la gobernanza de IA
- [ ] El informe de evaluabilidad (`python -m evaluabilidad` o la versión web) se ejecuta al menos semestralmente.
- [ ] Sus resultados se anexan a la FRIA de los sistemas de solvencia y a la vigilancia poscomercialización (Reglamento de IA arts. 27 y 72).
- [ ] Los perfiles con «Señal clara» activan una revisión documentada del paso del alta donde se pierden.

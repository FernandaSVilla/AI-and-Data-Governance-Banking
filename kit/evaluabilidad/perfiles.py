"""Perfiles de entrada (condiciones de entrada): situaciones en las que el proceso de alta puede no reconocer bien a una persona.

Un perfil describe la credencial o la situación del intento de alta, no a la persona:
no recoge nacionalidad, edad exacta ni otras categorías especiales de datos.
Cada intento se registra con un único perfil, el primero que el proceso detecta.
"""

REFERENCIA = "estandar"

# clave -> (nombre, por qué el alta puede fallar, ejemplo)
PERFILES = {
    "estandar": (
        "Documento estándar",
        "Es el perfil de referencia: DNI, NIE/TIE o pasaporte con chip que el sistema lee sin incidencias.",
        "Cliente con DNI que se da de alta desde la app.",
    ),
    "proteccion_internacional": (
        "Documento de protección internacional",
        "El lector automático o la lista de documentos admitidos no lo contempla.",
        "Solicitante de asilo con su documento de solicitante.",
    ),
    "nie_provisional": (
        "NIE en trámite o resguardo",
        "Es un documento provisional, sin chip o sin foto estándar, y la verificación automática lo rechaza.",
        "Persona recién llegada, o con el permiso en renovación, que presenta el resguardo.",
    ),
    "pasaporte_sin_chip": (
        "Pasaporte de fuera de la UE sin chip",
        "La verificación automática (lectura NFC o del documento) falla.",
        "Estudiante o trabajador extracomunitario.",
    ),
    "sin_domicilio": (
        "Sin domicilio fijo o sin justificante",
        "El proceso exige una prueba de dirección que la persona no puede aportar.",
        "Persona que vive en un albergue o en un alquiler informal.",
    ),
    "dispositivo_conectividad": (
        "Móvil o conexión insuficientes para la verificación",
        "La cámara no enfoca el documento, el móvil no tiene NFC, la videollamada se corta o el SMS no llega.",
        "Cliente con DNI y solvente, con un móvil antiguo o mala cobertura.",
    ),
    "asistencia_digital": (
        "Necesita ayuda para completar el proceso digital",
        "No puede completar sola el formulario o los pasos de verificación: lectura, comprensión o experiencia digital.",
        "Persona con baja alfabetización, persona mayor o sin experiencia con apps.",
    ),
    "accesibilidad": (
        "Necesita un ajuste de accesibilidad",
        "El canal no funciona con lector de pantalla, la biometría falla o las instrucciones son sólo visuales o sonoras.",
        "Persona con discapacidad visual o motora. Se registra el ajuste requerido, nunca un diagnóstico.",
    ),
    "zona_sin_oficina": (
        "Sin oficina accesible (zona rural o movilidad reducida)",
        "El alta exige un paso presencial (firma, entrega de tarjeta, verificación) y no hay oficina cercana o la persona no puede desplazarse.",
        "Persona mayor con DNI en un municipio sin sucursal, o persona que no puede salir de casa.",
    ),
    "sin_historial": (
        "Sin historial crediticio",
        "Suele abrir la cuenta sin problema, pero llega al modelo con pocos datos o no llega a ser evaluable.",
        "Joven con su primer empleo o persona recién llegada al país.",
    ),
    "otro": (
        "Otro perfil no estándar",
        "Cualquier otra credencial o situación válida que el proceso no reconoce bien.",
        "Definirlo en la política interna antes de usarlo.",
    ),
}

# Compatibilidad con la v0.1 (columna categoria_documental)
EQUIVALENCIA_V01 = {"estandar": "estandar", "no_estandar": "otro"}


def nombre(clave: str) -> str:
    return PERFILES.get(clave, (clave,))[0]

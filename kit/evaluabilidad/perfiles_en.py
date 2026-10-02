"""English version of the entry profiles (same keys as perfiles.PERFILES). Used by the bilingual web version."""

PERFILES_EN = {
    "estandar": (
        "Standard document",
        "Reference profile: national ID, residence card (NIE/TIE) or chip passport that the system reads without issues.",
        "Customer with a national ID card who signs up through the app.",
    ),
    "proteccion_internacional": (
        "International protection document",
        "The automatic document reader or the list of accepted documents does not include it.",
        "Asylum seeker presenting their applicant document.",
    ),
    "nie_provisional": (
        "Pending residence number or official receipt",
        "It is a provisional document, without a chip or a standard photo, and automatic verification rejects it.",
        "Newly arrived person, or one renewing their permit, who presents the official receipt.",
    ),
    "pasaporte_sin_chip": (
        "Non-EU passport without a chip",
        "Automatic verification (NFC or document reading) fails.",
        "Non-EU student or worker.",
    ),
    "sin_domicilio": (
        "No fixed address or no proof of address",
        "The process requires proof of address that the person cannot provide.",
        "Person living in a shelter or in informal housing.",
    ),
    "dispositivo_conectividad": (
        "Phone or connection not good enough for verification",
        "The camera cannot capture the document, the phone has no NFC, the video call drops or the SMS does not arrive.",
        "Creditworthy customer with a national ID card and an old phone or poor coverage.",
    ),
    "asistencia_digital": (
        "Needs help to complete the digital process",
        "Cannot complete the form or verification steps alone: reading, understanding or digital experience.",
        "Person with low literacy, an older person or someone new to apps.",
    ),
    "accesibilidad": (
        "Needs an accessibility adjustment",
        "The channel does not work with a screen reader, biometrics fail or instructions are only visual or audio.",
        "Person with a visual or motor impairment. The adjustment required is logged, never a diagnosis.",
    ),
    "zona_sin_oficina": (
        "No accessible branch (rural area or reduced mobility)",
        "Onboarding requires an in-person step (signature, card collection, verification) and there is no nearby branch or the person cannot travel.",
        "Older person with a national ID in a village without a branch, or a person who cannot leave home.",
    ),
    "sin_historial": (
        "No credit history",
        "Usually opens the account without problems, but reaches the model with little data or is not scorable.",
        "Young person in their first job or someone new to the country.",
    ),
    "otro": (
        "Other non-standard profile",
        "Any other valid credential or situation that the process does not recognise well.",
        "Define it in internal policy before using it.",
    ),
}

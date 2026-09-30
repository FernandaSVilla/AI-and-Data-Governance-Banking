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
    "asistencia_digital": (
        "Needs help with digital verification",
        "The selfie, video identification or SMS step fails, or the person cannot complete it alone.",
        "Older person or someone without a recent smartphone.",
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

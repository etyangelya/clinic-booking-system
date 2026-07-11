# Coarse keyword -> speciality lookup, not a triage system.
# Only Dermatology and Dentistry are specialists; everything else falls back to a general doctor.
SYMPTOM_SPECIALITY_MAP: dict[str, str] = {
    "skin rash": "Dermatology",
    "rash": "Dermatology",
    "acne": "Dermatology",
    "eczema": "Dermatology",
    "itchy skin": "Dermatology",
    "toothache": "Dentistry",
    "tooth pain": "Dentistry",
    "cavity": "Dentistry",
    "gum pain": "Dentistry",
    "bleeding gums": "Dentistry",
}


def match_speciality(symptom_text: str) -> str | None:
    """Returns the speciality for the longest matching keyword found as a
    substring of the symptom text, or None if nothing matches.
    """
    text = symptom_text.lower()

    best_keyword: str | None = None
    best_speciality: str | None = None
    for keyword, speciality in SYMPTOM_SPECIALITY_MAP.items():
        if keyword in text and (best_keyword is None or len(keyword) > len(best_keyword)):
            best_keyword = keyword
            best_speciality = speciality

    return best_speciality

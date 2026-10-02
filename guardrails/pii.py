import re


PII_PATTERNS = {
    "email": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),
    "phone": re.compile(
        r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b"
    ),
    "student_id": re.compile(
        r"\b(?:student\s*id|roll\s*no|roll\s*number|registration\s*no)"
        r"\s*[:#-]?\s*[A-Za-z0-9/-]{4,}\b",
        re.IGNORECASE,
    ),
    "aadhaar": re.compile(
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
    ),
}


def mask_pii(text: str) -> tuple[str, list[str]]:
    """
    Replace detected PII with typed placeholders.

    Returns:
        masked_text: sanitized text
        detected_types: list of PII categories detected
    """

    detected_types: list[str] = []

    masked_text = text

    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(masked_text):
            detected_types.append(pii_type)

            masked_text = pattern.sub(
                f"[REDACTED_{pii_type.upper()}]",
                masked_text,
            )

    return masked_text, detected_types
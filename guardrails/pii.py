from presidio_analyzer import (
    AnalyzerEngine,
    Pattern,
    PatternRecognizer,
)
from presidio_analyzer.predefined_recognizers import InAadhaarRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


# Presidio engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Indian Aadhaar recognizer
analyzer.registry.add_recognizer(
    InAadhaarRecognizer()
)

# Custom student ID recognizer
student_id_pattern = Pattern(
    name="student_id_pattern",
    regex=(
        r"\b(?:student\s*id|roll\s*no|roll\s*number|"
        r"registration\s*no)\s*"
        r"(?:is|=|:|#|-)?\s*"
        r"[A-Za-z0-9/-]{4,}\b"
    ),
    score=0.85,
)

student_id_recognizer = PatternRecognizer(
    supported_entity="STUDENT_ID",
    patterns=[student_id_pattern],
)

analyzer.registry.add_recognizer(
    student_id_recognizer
)

# Presidio → project entity mapping
ENTITY_MAP = {
    "EMAIL_ADDRESS": "email",
    "PHONE_NUMBER": "phone",
    "IN_AADHAAR": "aadhaar",
    "STUDENT_ID": "student_id",
}


def mask_pii(text: str) -> tuple[str, list[str]]:
    """
    Detect and redact PII using Microsoft Presidio.

    Returns:
        masked_text:
            Text with detected PII replaced by typed placeholders.

        detected_types:
            Project-level PII labels.
    """

    results = analyzer.analyze(
        text=text,
        language="en",
        entities=list(ENTITY_MAP.keys()),
        score_threshold=0.4,
    )

    detected_types = []

    for result in results:
        mapped_type = ENTITY_MAP.get(result.entity_type)

        if (
            mapped_type
            and mapped_type not in detected_types
        ):
            detected_types.append(mapped_type)

    operators = {
        entity_type: OperatorConfig(
            "replace",
            {
                "new_value": (
                    f"[REDACTED_{project_type.upper()}]"
                )
            },
        )
        for entity_type, project_type
        in ENTITY_MAP.items()
    }

    anonymized = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators=operators,
    )

    return anonymized.text, detected_types
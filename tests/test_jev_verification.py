from graph.nodes import verification


def base_state():
    return {
        "ticket_id": "TEST-001",
        "masked_message": ("When is the next public examination?"),
        "draft": ("The examination schedule is " "available in the official notice."),
        "citations": [
            "kb-001",
        ],
        "retrieved_documents": [
            {
                "content": (
                    "The examination schedule " "is available in the official notice."
                ),
                "metadata": {
                    "id": "kb-001",
                    "title": "Exam Schedule",
                    "category": "academic",
                },
            }
        ],
        "web_results": [],
        "retry_count": 0,
    }


def test_jev_pass(monkeypatch):

    def fake_verify_with_jev(
        *,
        ticket,
        draft,
        evidence,
        citations,
    ):
        return {
            "answers": {
                "grounded": {
                    "probability": 0.95,
                },
                "citation_supported": {
                    "probability": 0.92,
                },
            }
        }

    monkeypatch.setattr(
        verification.gateway,
        "verify_with_jev",
        fake_verify_with_jev,
    )

    result = verification.verify_response(base_state())

    assert result["verification_passed"] is True

    assert result["verification_grounded"] is True

    assert result["verification_citation_supported"] is True

    assert result["verification_grounding_probability"] == 0.95

    assert result["verification_citation_probability"] == 0.92


def test_jev_uncertain(monkeypatch):

    def fake_verify_with_jev(
        *,
        ticket,
        draft,
        evidence,
        citations,
    ):
        return {
            "answers": {
                "grounded": {
                    "probability": 0.77,
                },
                "citation_supported": {
                    "probability": 0.90,
                },
            }
        }

    monkeypatch.setattr(
        verification.gateway,
        "verify_with_jev",
        fake_verify_with_jev,
    )

    result = verification.verify_response(base_state())

    assert result["verification_passed"] is False

    assert result["verification_grounding_probability"] == 0.77

    assert result["verification_citation_probability"] == 0.90

    assert result["verification_reason"] == "Jev verification is uncertain."


def test_jev_missing_answer_fails_closed():

    def fake_verify_with_jev(
        *,
        ticket,
        draft,
        evidence,
        citations,
    ):
        return {
            "answers": {
                "grounded": {
                    "probability": 0.95,
                }
            }
        }

    original = verification.gateway.verify_with_jev

    verification.gateway.verify_with_jev = fake_verify_with_jev

    try:
        result = verification.verify_response(base_state())
    finally:
        verification.gateway.verify_with_jev = original

    assert result["verification_passed"] is False

    assert result["verification_citation_probability"] == 0.0


def test_jev_gateway_failure_fails_closed():

    def fake_verify_with_jev(
        *,
        ticket,
        draft,
        evidence,
        citations,
    ):
        raise RuntimeError("Gateway unavailable")

    original = verification.gateway.verify_with_jev

    verification.gateway.verify_with_jev = fake_verify_with_jev

    try:
        result = verification.verify_response(base_state())
    finally:
        verification.gateway.verify_with_jev = original

    assert result["verification_passed"] is False

    assert result["verification_reason"] == "Jev verification could not be completed."

    assert result["verification_error"] == "Gateway unavailable"


def test_empty_draft_fails_closed():

    state = base_state()

    state["draft"] = ""

    result = verification.verify_response(state)

    assert result["verification_passed"] is False

    assert result["verification_grounding_probability"] == 0.0

    assert result["verification_citation_probability"] == 0.0

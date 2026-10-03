from graph.state import TicketState
from gateway.vercel import VercelGateway

gateway = VercelGateway()


GROUNDING_PASS_THRESHOLD = 0.65
GROUNDING_FAIL_THRESHOLD = 0.50

CITATION_PASS_THRESHOLD = 0.65
CITATION_FAIL_THRESHOLD = 0.50

MAX_RETRIES = 1


def _get_probability(
    result: dict,
    question: str,
) -> float:
    return float(
        result.get(
            "answers",
            {},
        )
        .get(
            question,
            {},
        )
        .get(
            "probability",
            0.0,
        )
    )


def _build_evidence(
    state: TicketState,
) -> str:

    evidence_parts = []

    for document in state.get(
        "retrieved_documents",
        [],
    ):
        metadata = document.get(
            "metadata",
            {},
        )

        evidence_parts.append(f"""
SOURCE TYPE: INTERNAL_KB
SOURCE ID: {metadata.get("id", "")}
TITLE: {metadata.get("title", "")}
CONTENT: {document.get("content", "")}
""")

    for index, result in enumerate(
        state.get(
            "web_results",
            [],
        )
    ):
        evidence_parts.append(f"""
SOURCE TYPE: APPROVED_WEB
SOURCE ID: web-{index + 1}
TITLE: {result.get("title", "")}
URL: {result.get("url", "")}
CONTENT: {result.get("content", "")}
""")

    return "\n".join(evidence_parts)


def verify_response(
    state: TicketState,
) -> TicketState:

    draft = state.get(
        "draft",
        "",
    )

    message = state.get(
        "masked_message",
        "",
    )

    retry_count = state.get(
        "retry_count",
        0,
    )

    if not draft.strip():
        return {
            **state,
            "verification_passed": False,
            "verification_reason": ("Draft is empty."),
            "verification_grounded": False,
            "verification_grounding_probability": 0.0,
            "verification_citation_supported": False,
            "verification_citation_probability": 0.0,
            "verification_unsupported_claims": [],
            "verification_feedback": (
                "The response is empty. Generate a complete "
                "response using only the supplied evidence."
            ),
        }

    if not message.strip():
        return {
            **state,
            "verification_passed": False,
            "verification_reason": ("Ticket message is empty."),
            "verification_grounded": False,
            "verification_grounding_probability": 0.0,
            "verification_citation_supported": False,
            "verification_citation_probability": 0.0,
            "verification_unsupported_claims": [],
            "verification_feedback": (
                "The ticket content is unavailable. " "Do not generate a response."
            ),
        }

    evidence = _build_evidence(state)

    if not evidence.strip():
        return {
            **state,
            "verification_passed": False,
            "verification_reason": ("No evidence was available for verification."),
            "verification_grounded": False,
            "verification_grounding_probability": 0.0,
            "verification_citation_supported": False,
            "verification_citation_probability": 0.0,
            "verification_unsupported_claims": [],
            "verification_feedback": (
                "No evidence is available. Do not make " "unsupported claims."
            ),
        }

    # print("\n--- Evidence sent to Jev ---")
    # print(evidence)

    result = gateway.verify_with_jev(
        ticket=message,
        draft=draft,
        evidence=evidence,
        citations=state.get(
            "citations",
            [],
        ),
    )

    grounding_probability = _get_probability(
        result,
        "grounded",
    )

    citation_probability = _get_probability(
        result,
        "citation_supported",
    )

    grounded = grounding_probability >= GROUNDING_PASS_THRESHOLD

    citation_supported = citation_probability >= CITATION_PASS_THRESHOLD

    passed = grounded and citation_supported

    if passed:
        reason = (
            "Jev found the response sufficiently "
            "grounded and its citations sufficiently "
            "supported."
        )

        feedback = ""

    elif grounding_probability < GROUNDING_FAIL_THRESHOLD:
        reason = "Jev found insufficient grounding " "for the drafted response."

        feedback = (
            "The previous response was not sufficiently "
            "grounded in the supplied evidence. Rewrite "
            "the response using only claims directly "
            "supported by the evidence. Remove unsupported "
            "claims and avoid adding assumptions."
        )

    elif citation_probability < CITATION_FAIL_THRESHOLD:
        reason = "Jev found insufficient citation support " "for the drafted response."

        feedback = (
            "The previous response did not have sufficiently "
            "supported citations. Rewrite the response using "
            "only evidence sources that directly support the "
            "claims, and cite only those sources."
        )

    else:
        reason = "Jev verification is uncertain."

        feedback = (
            "The previous response could not be verified "
            "with sufficient confidence. Rewrite it more "
            "conservatively and include only claims that "
            "are directly supported by the supplied evidence."
        )

    return {
        **state,
        "verification_passed": passed,
        "verification_reason": reason,
        "verification_grounded": grounded,
        "verification_grounding_probability": (grounding_probability),
        "verification_citation_supported": (citation_supported),
        "verification_citation_probability": (citation_probability),
        "verification_unsupported_claims": [],
        "verification_feedback": feedback,
        "retry_count": (retry_count if passed else retry_count),
    }

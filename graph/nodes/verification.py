from typing import Any

from graph.state import TicketState
from gateway.vercel import VercelGateway

gateway = VercelGateway()

# Verification configuration
GROUNDING_PASS_THRESHOLD = 0.60
GROUNDING_FAIL_THRESHOLD = 0.60

CITATION_PASS_THRESHOLD = 0.60
CITATION_FAIL_THRESHOLD = 0.60

MAX_RETRIES = 1


# Helpers
def _get_probability(
    result: dict[str, Any],
    question: str,
) -> float:
    """
    Safely extract a Jev boolean probability.

    Expected Jev structure:

        {
            "answers": {
                "grounded": {
                    "probability": 0.91
                }
            }
        }

    If the answer is missing or malformed,
    return 0.0 so verification fails closed.
    """

    answers = result.get(
        "answers",
        {},
    )

    if not isinstance(answers, dict):
        return 0.0

    answer = answers.get(
        question,
        {},
    )

    if not isinstance(answer, dict):
        return 0.0

    probability = answer.get(
        "probability",
        0.0,
    )

    try:
        probability = float(probability)
    except (
        TypeError,
        ValueError,
    ):
        return 0.0

    # Never allow malformed probabilities
    # outside the valid probability range.
    if probability < 0.0:
        return 0.0

    if probability > 1.0:
        return 1.0

    return probability


def _build_evidence(
    state: TicketState,
) -> str:
    """
    Convert all approved evidence into one explicit
    verification context.

    Every source receives an unambiguous source ID.

    Jev is therefore evaluating the draft against the
    exact evidence that the response generator received.
    """

    evidence_parts: list[str] = []

    # Internal KB
    for document in state.get(
        "retrieved_documents",
        [],
    ):
        metadata = document.get(
            "metadata",
            {},
        )

        document_id = str(
            metadata.get(
                "id",
                "",
            )
        ).strip()

        title = str(
            metadata.get(
                "title",
                "",
            )
        ).strip()

        category = str(
            metadata.get(
                "category",
                "",
            )
        ).strip()

        content = str(
            document.get(
                "content",
                "",
            )
        ).strip()

        evidence_parts.append(
            "\n".join(
                [
                    "SOURCE TYPE: INTERNAL_KB",
                    f"SOURCE ID: {document_id}",
                    f"TITLE: {title}",
                    f"CATEGORY: {category}",
                    f"CONTENT: {content}",
                ]
            )
        )

    # Approved web evidence
    for index, result in enumerate(
        state.get(
            "web_results",
            [],
        )
    ):
        citation_id = f"web-{index + 1}"

        title = str(
            result.get(
                "title",
                "",
            )
        ).strip()

        url = str(
            result.get(
                "url",
                "",
            )
        ).strip()

        content = str(
            result.get(
                "content",
                "",
            )
        ).strip()

        evidence_parts.append(
            "\n".join(
                [
                    "SOURCE TYPE: APPROVED_WEB",
                    f"SOURCE ID: {citation_id}",
                    f"TITLE: {title}",
                    f"URL: {url}",
                    f"CONTENT: {content}",
                ]
            )
        )

    return "\n\n".join(evidence_parts)


def _failure_state(
    state: TicketState,
    *,
    reason: str,
    feedback: str,
    error: str | None = None,
) -> TicketState:
    """
    Build a consistent fail-closed verification state.
    """

    result: TicketState = {
        **state,
        "verification_passed": False,
        "verification_reason": reason,
        "verification_grounded": False,
        "verification_grounding_probability": 0.0,
        "verification_citation_supported": False,
        "verification_citation_probability": 0.0,
        "verification_unsupported_claims": [],
        "verification_feedback": feedback,
    }

    if error is not None:
        result["verification_error"] = error

    return result


# Main verification node


def verify_response(
    state: TicketState,
) -> TicketState:
    """
    Independently verify the generated support response.

    Verification consists of:

            draft
             |
             v
       ---- Jev ----
       |           |
      |           |
    grounding  citations
       \       /
        \     /
         result
           |
           v
      deterministic
        threshold
          |
          v
       pass/fail

    This function never asks an LLM to make the final
    AUTO_REPLY/HUMAN_APPROVE decision.
    """

    draft = str(
        state.get(
            "draft",
            "",
        )
    )

    message = str(
        state.get(
            "masked_message",
            "",
        )
    )

    # Basic validation
    if not draft.strip():
        return _failure_state(
            state,
            reason="Draft is empty.",
            feedback=(
                "The response is empty. "
                "Generate a complete response "
                "using only the supplied evidence."
            ),
        )

    if not message.strip():
        return _failure_state(
            state,
            reason="Ticket message is empty.",
            feedback=(
                "The ticket content is unavailable. " "Do not generate a response."
            ),
        )

    # Build verification evidence
    evidence = _build_evidence(state)

    if not evidence.strip():
        return _failure_state(
            state,
            reason=("No evidence was available " "for verification."),
            feedback=("No evidence is available. " "Do not make unsupported claims."),
        )

    # Call Jev
    try:
        result = gateway.verify_with_jev(
            ticket=message,
            draft=draft,
            evidence=evidence,
            citations=state.get(
                "citations",
                [],
            ),
        )

    except Exception as exc:
        error_message = str(exc)

        return _failure_state(
            state,
            reason=("Jev verification could not " "be completed."),
            feedback=(
                "The verification service was "
                "unavailable or returned an invalid "
                "result. Do not automatically send "
                "the response. Route the ticket "
                "for human review."
            ),
            error=error_message,
        )

    # Parse Jev result
    grounding_probability = _get_probability(
        result,
        "grounded",
    )

    citation_probability = _get_probability(
        result,
        "citation_supported",
    )

    # Deterministic threshold evaluation

    grounded = grounding_probability >= GROUNDING_PASS_THRESHOLD

    citation_supported = citation_probability >= CITATION_PASS_THRESHOLD

    passed = grounded and citation_supported

    # Determine reason + retry feedback

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
            "The previous response did not have "
            "sufficiently supported citations. Rewrite "
            "the response using only evidence sources "
            "that directly support the claims, and "
            "cite only those sources."
        )

    else:
        reason = "Jev verification is uncertain."

        feedback = (
            "The previous response could not be "
            "verified with sufficient confidence. "
            "Rewrite it more conservatively and "
            "include only claims that are directly "
            "supported by the supplied evidence."
        )

    # Extract optional Jev metadata
    verification_error = None

    if isinstance(result, dict):
        errors = result.get("errors")

        if errors:
            verification_error = str(errors)

    # Return complete verification state

    verification_state: TicketState = {
        **state,
        "verification_passed": passed,
        "verification_reason": reason,
        "verification_grounded": grounded,
        "verification_grounding_probability": (grounding_probability),
        "verification_citation_supported": (citation_supported),
        "verification_citation_probability": (citation_probability),
        # Jev's current boolean questions do not return a list of unsupported claims.Therefore we must NOT fabricate one.
        "verification_unsupported_claims": [],
        "verification_feedback": feedback,
    }

    if verification_error:
        verification_state["verification_error"] = verification_error

    return verification_state

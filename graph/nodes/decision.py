from graph.state import TicketState


SENSITIVE_CATEGORIES = {
    "payment",
    "refund",
}


def _append_reason(
    reasons: list[str],
    reason: str,
) -> None:
    if reason not in reasons:
        reasons.append(reason)


def make_decision(
    state: TicketState,
) -> TicketState:
    """Make the final response-routing decision from explicit state.

    This node is intentionally deterministic. It does not ask an LLM
    to make the final routing decision.
    """

    category = state.get(
        "primary_category"
    )

    risk_flags = state.get(
        "risk_flags",
        [],
    )

    web_used = state.get(
        "web_used",
        False,
    )

    web_required = state.get(
        "web_required",
        False,
    )

    verification_passed = state.get(
        "verification_passed",
        False,
    )

    # Preserve reason codes produced by upstream workflow nodes.
    reasons = list(
        state.get(
            "reason_codes",
            [],
        )
    )

    if not verification_passed:
        _append_reason(
            reasons,
            "VERIFICATION_FAILED",
        )

    if category in SENSITIVE_CATEGORIES:
        _append_reason(
            reasons,
            "SENSITIVE_CATEGORY",
        )

    if risk_flags:
        _append_reason(
            reasons,
            "RISK_FLAG",
        )

    if web_used:
        _append_reason(
            reasons,
            "WEB_SOURCED_RESPONSE",
        )

    # Fail closed when external information was required but
    # could not actually be obtained.
    if web_required and not web_used:
        _append_reason(
            reasons,
            "WEB_REQUIRED_BUT_UNAVAILABLE",
        )

    if reasons:
        return {
            **state,
            "decision": "HUMAN_APPROVE",
            "reason_codes": reasons,

            # HITL state
            "review_status": "PENDING",
            "human_decision": "",
            "reviewer_note": "",
            "final_response": "",
            "delivery_status": "WAITING_HUMAN_REVIEW",
        }

    return {
        **state,
        "decision": "AUTO_REPLY",
        "reason_codes": [
            "STANDARD_SUPPORT_REQUEST"
        ],

        # No human review is required.
        "review_status": "NOT_REQUIRED",
        "human_decision": "",
        "reviewer_note": "",
        "final_response": state.get(
            "draft",
            "",
        ),
        "delivery_status": "READY_TO_SEND",
    }
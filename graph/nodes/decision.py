from graph.state import TicketState


def make_decision(
    state: TicketState,
) -> TicketState:

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

    verification_passed = state.get(
        "verification_passed",
        False,
    )

    reasons = []

    if not verification_passed:
        reasons.append(
            "VERIFICATION_FAILED"
        )

    if category in {
        "payment",
        "refund",
    }:
        reasons.append(
            "SENSITIVE_CATEGORY"
        )

    if risk_flags:
        reasons.append(
            "RISK_FLAG"
        )

    if web_used:
        reasons.append(
            "WEB_SOURCED_RESPONSE"
        )

    if reasons:
        return {
            **state,
            "decision": "HUMAN_APPROVE",
            "reason_codes": reasons,
        }

    return {
        **state,
        "decision": "AUTO_REPLY",
        "reason_codes": [
            "STANDARD_SUPPORT_REQUEST"
        ],
    }
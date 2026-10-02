from graph.state import TicketState


def make_decision(state: TicketState) -> TicketState:
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

    existing_reasons = state.get(
        "reason_codes",
        [],
    )

    reasons = list(existing_reasons)

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

    # If the KB was insufficient and we could not
    # use an approved external source, human review
    # is required.
    if state.get("web_required", False) and not web_used:
        reasons.append(
            "WEB_UNAVAILABLE_OR_NOT_ALLOWED"
        )

    # Preserve ordering while removing duplicates.
    reasons = list(dict.fromkeys(reasons))

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
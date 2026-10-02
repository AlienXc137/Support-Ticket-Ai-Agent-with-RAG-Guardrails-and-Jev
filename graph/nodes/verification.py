from graph.state import TicketState


def verify_response(state: TicketState) -> TicketState:
    draft = state.get("draft", "")
    message = state.get("masked_message", "")

    passed = bool(draft.strip()) and bool(message.strip())

    return {
        **state,
        "verification_passed": passed,
        "verification_reason": (
            "Draft generated successfully."
            if passed
            else "Draft or ticket message is empty."
        ),
    }
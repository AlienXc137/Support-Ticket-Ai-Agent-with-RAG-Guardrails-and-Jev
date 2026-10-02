from graph.state import TicketState


def sanitize_ticket(state: TicketState) -> TicketState:
    message = state["raw_message"]

    # Very basic placeholder for now.
    # Real PII masking will be added later.
    masked_message = message.strip()

    return {
        **state,
        "masked_message": masked_message,
    }
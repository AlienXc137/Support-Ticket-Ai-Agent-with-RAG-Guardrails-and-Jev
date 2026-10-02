from graph.state import TicketState
from guardrails.pii import mask_pii


def sanitize_ticket(state: TicketState) -> TicketState:
    raw_message = state["raw_message"]

    masked_message, pii_detected = mask_pii(raw_message)

    return {
        "masked_message": masked_message,
        "pii_detected": pii_detected,
    }
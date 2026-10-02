from graph.state import TicketState
from guardrails.input import check_input


def input_guardrail(state: TicketState) -> TicketState:
    message = state["masked_message"]

    result = check_input(message)

    return {
        "input_allowed": result["allowed"],
        "guardrail_status": result["status"].value,
        "guardrail_reason": result["reason"],
    }
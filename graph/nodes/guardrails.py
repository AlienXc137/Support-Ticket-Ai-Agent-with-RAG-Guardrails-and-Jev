from graph.state import TicketState
from guardrails.input import check_input


def input_guardrail(state: TicketState) -> TicketState:
    result = check_input(state["masked_message"])

    return {
        **state,
        "input_allowed": result["allowed"],
        "guardrail_status": result["status"],
        "guardrail_reason": result["reason"],
        "masked_message": result["message"],
    }
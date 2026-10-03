from langgraph.graph import END,START,StateGraph

from graph.state import TicketState
from graph.nodes.sanitize import sanitize_ticket
from graph.nodes.guardrails import input_guardrail
from graph.nodes.analyzer import analyze_ticket
from graph.nodes.retrieval import retrieve_knowledge
from graph.nodes.coverage import check_kb_coverage
from graph.nodes.web_search import web_search
from graph.nodes.drafting import draft_response
from graph.nodes.verification import MAX_RETRIES,verify_response

from graph.nodes.decision import make_decision


def route_after_input_guardrail(state: TicketState) -> str:
    if not state.get(
        "input_allowed",
        True,
    ):
        return "blocked"

    return "continue"


def route_after_coverage(state: TicketState) -> str:
    if state.get(
        "web_required",
        False,
    ):
        return "web_search"

    return "draft_response"


def route_after_verification(state: TicketState) -> str:
    """
    Verification routing is deterministic.

    PASS
        -> decision

    FAIL + retry available
        -> retry

    FAIL + retry exhausted
        -> decision

    The decision node then sees:
        verification_passed = False

    and therefore adds:
        VERIFICATION_FAILED

    This guarantees human review.
    """

    if state.get(
        "verification_passed",
        False,
    ):
        return "decision"

    retry_count = state.get(
        "retry_count",
        0,
    )

    if retry_count < MAX_RETRIES:
        return "retry"

    return "decision"


def prepare_retry(state: TicketState) -> TicketState:
    return {
        **state,
        "retry_count": (
            state.get(
                "retry_count",
                0,
            )
            + 1
        ),
    }


def build_graph():
    graph = StateGraph(TicketState)

    # Nodes

    graph.add_node("sanitize_ticket", sanitize_ticket)
    graph.add_node("input_guardrail", input_guardrail)
    graph.add_node("analyze_ticket", analyze_ticket)
    graph.add_node("retrieve_knowledge", retrieve_knowledge)
    graph.add_node("check_kb_coverage", check_kb_coverage)
    graph.add_node("web_search", web_search)
    graph.add_node("draft_response", draft_response)
    graph.add_node("verify_response", verify_response)
    graph.add_node("prepare_retry", prepare_retry)
    graph.add_node("make_decision", make_decision)

    # Intake

    graph.add_edge(START, "sanitize_ticket")
    graph.add_edge("sanitize_ticket", "input_guardrail")

    graph.add_conditional_edges(
        "input_guardrail",
        route_after_input_guardrail,
        {
            "continue": "analyze_ticket",
            "blocked": END,
        },
    )

    # Analysis / Retrieval

    graph.add_edge("analyze_ticket", "retrieve_knowledge")
    graph.add_edge("retrieve_knowledge", "check_kb_coverage")

    # Web fallback

    graph.add_conditional_edges(
        "check_kb_coverage",
        route_after_coverage,
        {
            "web_search": "web_search",
            "draft_response": "draft_response",
        },
    )

    graph.add_edge("web_search", "draft_response")

    # Draft -> Verification

    graph.add_edge("draft_response", "verify_response")

    # Verification routing

    graph.add_conditional_edges(
        "verify_response",
        route_after_verification,
        {
            "decision": "make_decision",
            "retry": "prepare_retry",
        },
    )

    # Controlled retry

    graph.add_edge("prepare_retry", "draft_response")

    # Final deterministic decision

    graph.add_edge("make_decision", END)

    return graph.compile()
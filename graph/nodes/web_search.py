from graph.state import TicketState
from web.policy import WebPolicy
from web.tavily import TavilyClient


policy = WebPolicy()


def web_search(state: TicketState) -> TicketState:
    source_type = state.get(
        "web_source_type",
        "other",
    )

    policy_config = policy.get_policy(
        source_type
    )

    if not policy_config.get(
        "enabled",
        False,
    ):
        return {
            **state,
            "web_results": [],
            "web_used": False,
            "reason_codes": [
                *state.get("reason_codes", []),
                "WEB_NOT_ALLOWED",
            ],
        }

    domains = policy_config.get(
        "domains",
        [],
    )

    query = state["masked_message"]

    tavily = TavilyClient()

    results = tavily.search_web(
        query=query,
        domains=domains or None,
    )

    if not results:
        return {
            **state,
            "web_results": [],
            "web_used": False,
            "reason_codes": [
                *state.get("reason_codes", []),
                "WEB_NO_RESULTS",
            ],
        }

    return {
        **state,
        "web_results": results,
        "web_used": True,
    }
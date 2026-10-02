from graph.state import TicketState
from gateway.prompts import TICKET_ANALYSIS_PROMPT
from gateway.vercel import VercelGateway


gateway = VercelGateway()

analysis_chain = (
    TICKET_ANALYSIS_PROMPT
    | gateway.analysis_llm
)


def analyze_ticket(state: TicketState) -> TicketState:
    message = state["masked_message"]

    analysis = analysis_chain.invoke(
        {
            "ticket": message,
        }
    )

    return {
        **state,
        "issues": [
            issue.model_dump()
            for issue in analysis.issues
        ],
        "primary_category": analysis.primary_category,
        "urgency": analysis.urgency,
        "complexity": analysis.complexity,
        "anger_score": analysis.anger_score,
        "risk_flags": analysis.risk_flags,
    }
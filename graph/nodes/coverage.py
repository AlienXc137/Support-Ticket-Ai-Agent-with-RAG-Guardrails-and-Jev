from graph.state import TicketState
from gateway.prompts import KB_COVERAGE_PROMPT
from gateway.vercel import VercelGateway


gateway = VercelGateway()

coverage_chain = (
    KB_COVERAGE_PROMPT
    | gateway.coverage_llm
)


def check_kb_coverage(state: TicketState) -> TicketState:
    documents = state.get("retrieved_documents",[])

    context_parts = []

    for document in documents:
        metadata = document.get("metadata", {})

        context_parts.append(
            f"""
            Document ID: {metadata.get("id", "")}
            Title: {metadata.get("title", "")}
            Category: {metadata.get("category", "")}
            Content: {document.get("content", "")}
            """
        )

    context = "\n".join(context_parts)

    result = coverage_chain.invoke(
        {
            "ticket": state["masked_message"],
            "context": context,
        }
    )

    return {
        **state,
        "kb_coverage": result.sufficient,
        "web_required": not result.sufficient,
        "web_reason": result.reason,
        "web_source_type": result.source_type,
    }
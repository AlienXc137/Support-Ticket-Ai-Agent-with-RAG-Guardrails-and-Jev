from graph.state import TicketState
from gateway.prompts import RESPONSE_PROMPT
from gateway.vercel import VercelGateway


gateway = VercelGateway()

response_chain = (
    RESPONSE_PROMPT
    | gateway.response_llm
)


def draft_response(
    state: TicketState,
) -> TicketState:

    documents = state.get(
        "retrieved_documents",
        [],
    )

    web_results = state.get(
        "web_results",
        [],
    )

    context_parts = []
    valid_citation_ids = set()

    # Internal KB evidence
    for document in documents:
        metadata = document.get(
            "metadata",
            {},
        )

        document_id = metadata.get(
            "id",
            "",
        )

        context_parts.append(
            f"""
SOURCE TYPE: INTERNAL_KB
SOURCE ID: {document_id}
TITLE: {metadata.get("title", "")}
CATEGORY: {metadata.get("category", "")}
CONTENT: {document.get("content", "")}
"""
        )

        if document_id:
            valid_citation_ids.add(
                document_id
            )

    # Approved web evidence
    for index, result in enumerate(
        web_results
    ):
        citation_id = f"web-{index + 1}"

        context_parts.append(
            f"""
SOURCE TYPE: APPROVED_WEB
SOURCE ID: {citation_id}
TITLE: {result.get("title", "")}
URL: {result.get("url", "")}
CONTENT: {result.get("content", "")}
"""
        )

        valid_citation_ids.add(
            citation_id
        )

    if not context_parts:
        return {
            **state,
            "draft": (
                "We do not currently have enough "
                "reliable information to answer "
                "this request. The request requires "
                "further review."
            ),
            "citations": [],
        }

    context = "\n".join(
        context_parts
    )

    verification_feedback = state.get(
        "verification_feedback",
        "",
    )

    response = response_chain.invoke(
        {
            "ticket": state["masked_message"],
            "context": context,
            "verification_feedback": (
                verification_feedback
                if verification_feedback
                else "No previous verification feedback."
            ),
        }
    )

    citation_ids = [
        citation_id
        for citation_id in response.citation_ids
        if citation_id in valid_citation_ids
    ]

    return {
        **state,
        "draft": response.answer,
        "citations": citation_ids,
    }
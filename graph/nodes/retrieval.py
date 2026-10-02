from graph.state import TicketState
from retrieval.hybrid import build_hybrid_retriever


retriever = build_hybrid_retriever()


def retrieve_knowledge(state: TicketState) -> TicketState:
    query = state["masked_message"]

    documents = retriever.invoke(query)

    retrieved_documents = []

    for document in documents:
        retrieved_documents.append(
            {
                "content": document.page_content,
                "metadata": document.metadata,
            }
        )

    return {
        **state,
        "retrieved_documents": retrieved_documents,
    }
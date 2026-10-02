from langchain_classic.retrievers import EnsembleRetriever

from retrieval.bm25 import build_bm25_retriever
from retrieval.vector import build_vector_store


def build_hybrid_retriever():
    vector_store = build_vector_store()
    vector_retriever = vector_store.as_retriever(
        search_kwargs={
            "k": 5
        }
    )

    bm25_retriever = build_bm25_retriever()

    hybrid_retriever = EnsembleRetriever(
        retrievers=[
            bm25_retriever,
            vector_retriever,
        ],
        weights=[
            0.35,
            0.65,
        ],
    )

    return hybrid_retriever
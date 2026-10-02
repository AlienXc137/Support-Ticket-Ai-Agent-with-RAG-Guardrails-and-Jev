from langchain_community.retrievers import BM25Retriever

from retrieval.loader import load_documents


def build_bm25_retriever() -> BM25Retriever:
    documents = load_documents()
    retriever = BM25Retriever.from_documents(documents)
    retriever.k = 5
    return retriever
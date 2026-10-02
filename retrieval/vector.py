from langchain_community.vectorstores import FAISS

from retrieval.embeddings import get_embeddings
from retrieval.loader import load_documents


def build_vector_store() -> FAISS:
    documents = load_documents()
    embeddings = get_embeddings()

    return FAISS.from_documents(
        documents,
        embeddings,
    )
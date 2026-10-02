import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


from langchain_huggingface import HuggingFaceEmbeddings


def get_embeddings():
    load_dotenv()
    return HuggingFaceEmbeddings(
        model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        model_kwargs={
            "device": "cpu",
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )
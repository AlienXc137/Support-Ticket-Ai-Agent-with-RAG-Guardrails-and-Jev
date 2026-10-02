import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings


load_dotenv()


def get_embeddings() -> OpenAIEmbeddings:
    api_key = os.getenv("AI_GATEWAY_API_KEY")

    if not api_key:
        raise ValueError(
            "AI_GATEWAY_API_KEY is not set."
        )

    return OpenAIEmbeddings(
        model="openai/text-embedding-3-small",
        api_key=api_key,
        base_url="https://ai-gateway.vercel.sh/v1",

        # Important for Vercel AI Gateway:
        # send raw text strings instead of LangChain's
        # pre-tokenized integer arrays.
        check_embedding_ctx_length=False,
    )
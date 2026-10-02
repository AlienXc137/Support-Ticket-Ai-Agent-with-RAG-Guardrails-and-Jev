import json
from pathlib import Path

from langchain_core.documents import Document

BASE_DIR = Path(__file__).resolve().parent.parent
KB_PATH = BASE_DIR / "kb" / "documents.json"


def load_documents() -> list[Document]:
    with KB_PATH.open("r",encoding="utf-8") as file:
        records = json.load(file)

    documents = []

    for record in records:
        documents.append(
            Document(
                page_content=record["content"],
                metadata={
                    "id": record["id"],
                    "title": record["title"],
                    "category": record["category"],
                },
            )
        )

    return documents
from pathlib import Path
import json

from langchain_core.documents import Document

BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = BASE_DIR / "kb"
MANIFEST_NAME = "kb_manifest.json"


def load_documents() -> list[Document]:
    if not KB_DIR.exists():
        raise FileNotFoundError(f"Knowledge base directory not found: {KB_DIR}")

    json_files = sorted(
        path for path in KB_DIR.rglob("*.json") if path.name != MANIFEST_NAME
    )

    if not json_files:
        raise FileNotFoundError(f"No KB JSON files found in: {KB_DIR}")

    documents: list[Document] = []

    for json_path in json_files:
        with json_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            payload = json.load(file)

        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict):
            records = payload.get("documents", [])
        else:
            raise ValueError(f"Unsupported JSON structure in: {json_path}")

        for record in records:
            if not isinstance(record, dict):
                continue

            content = str(record.get("content", "")).strip()

            if not content:
                continue

            title = str(record.get("title", "")).strip()

            category = str(record.get("category", "")).strip()

            department = str(record.get("department", "")).strip()

            scenario = str(record.get("scenario", "")).strip()

            keywords = str(record.get("keywords", "")).strip()

            searchable_content = (
                f"Title: {title}\n"
                f"Category: {category}\n"
                f"Department: {department}\n"
                f"Scenario: {scenario}\n"
                f"Keywords: {keywords}\n\n"
                f"{content}"
            )

            documents.append(
                Document(
                    page_content=searchable_content,
                    metadata={
                        "id": record.get("id", ""),
                        "title": title,
                        "category": category,
                        "department": department,
                        "scenario": scenario,
                        "keywords": keywords,
                        "source_file": json_path.name,
                    },
                )
            )

    return documents

import os
from langchain_tavily import TavilySearch


class TavilyClient:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise ValueError("TAVILY_API_KEY is not set.")

        self.search = TavilySearch(
            max_results=5,
            topic="general",
            search_depth="basic",
            include_answer=False,
            include_raw_content=False,
            include_images=False,
        )

    def search_web(
        self,
        query: str,
        domains: list[str] | None = None,
    ) -> list[dict]:
        kwargs = {
            "query": query,
        }

        if domains:
            kwargs["include_domains"] = domains

        result = self.search.invoke(kwargs)

        # TavilySearch returns serialized result content.
        if isinstance(result, str):
            import json

            result = json.loads(result)

        return result.get("results", [])
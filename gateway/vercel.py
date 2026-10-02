import os

import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.schemas import (
    KBCoverage,
    SupportResponse,
    TicketAnalysis,
)

load_dotenv()


class VercelGateway:
    def __init__(self):
        api_key = os.getenv("AI_GATEWAY_API_KEY")

        if not api_key:
            raise ValueError(
                "AI_GATEWAY_API_KEY is not set."
            )

        self.api_key = api_key

        self.llm = ChatOpenAI(
            model=os.getenv(
                "LLM_MODEL",
                "openai/gpt-6-luna",
            ),
            api_key=api_key,
            base_url="https://ai-gateway.vercel.sh/v1",
            temperature=0,
        )

        self.analysis_llm = (
            self.llm.with_structured_output(
                TicketAnalysis
            )
        )

        self.response_llm = (
            self.llm.with_structured_output(
                SupportResponse
            )
        )

        self.coverage_llm = (
            self.llm.with_structured_output(
                KBCoverage
            )
        )

    def evaluate_with_jev(
        self,
        state: dict,
        questions: dict,
    ) -> dict:
        response = httpx.post(
            "https://ai-gateway.vercel.sh/v1/evaluate",
            headers={
                "Authorization": (
                    f"Bearer {self.api_key}"
                ),
                "Content-Type": "application/json",
            },
            json={
                "model": "typesafe-ai/jev",
                "state": state,
                "questions": questions,
            },
            timeout=30.0,
        )

        response.raise_for_status()

        return response.json()

    def verify_with_jev(
        self,
        ticket: str,
        draft: str,
        evidence: str,
        citations: list[str],
    ) -> dict:
        return self.evaluate_with_jev(
            state={
                "ticket": ticket,
                "draft": draft,
                "evidence": evidence,
                "citations": citations,
            },
            questions={
                "grounded": {
                    "type": "boolean",
                    "instructions": (
                        "Is every substantive claim in the "
                        "drafted response directly supported "
                        "by the supplied evidence?"
                    ),
                },
                "citation_supported": {
                    "type": "boolean",
                    "instructions": (
                        "Are the citations used by the drafted "
                        "response supported by the supplied "
                        "evidence sources?"
                    ),
                },
            },
        )
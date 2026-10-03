import os
from typing import Any

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
    """
    Central gateway for all LLM and Jev calls.

    LLM calls use the OpenAI-compatible Vercel AI Gateway endpoint.

    Jev is different from normal LLM generation:
    it is an evaluation model and must be called through
    the Vercel evaluation endpoint.
    """

    DEFAULT_GATEWAY_BASE_URL = ("https://ai-gateway.vercel.sh/v1")

    DEFAULT_JEV_MODEL = "typesafe-ai/jev"

    DEFAULT_JEV_TIMEOUT = 30.0

    def __init__(self):
        api_key = os.getenv(
            "AI_GATEWAY_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "AI_GATEWAY_API_KEY is not set."
            )

        self.api_key = api_key

        self.gateway_base_url = os.getenv(
            "AI_GATEWAY_BASE_URL",
            self.DEFAULT_GATEWAY_BASE_URL,
        ).rstrip("/")

        self.jev_model = os.getenv(
            "JEV_MODEL",
            self.DEFAULT_JEV_MODEL,
        )

        self.jev_timeout = float(
            os.getenv(
                "JEV_TIMEOUT",
                str(self.DEFAULT_JEV_TIMEOUT),
            )
        )

        # Normal LLM gateway
        self.llm = ChatOpenAI(
            model=os.getenv(
                "LLM_MODEL",
                "openai/gpt-6-luna",
            ),
            api_key=api_key,
            base_url=self.gateway_base_url,
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

    # Jev
    def evaluate_with_jev(
        self,
        *,
        state: dict[str, Any],
        questions: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Call Jev through Vercel AI Gateway.

        Vercel's Jev HTTP API expects:

            POST /v1/evaluate

        with:

            {
                "model": "typesafe-ai/jev",
                "state": ...,
                "questions": ...
            }

        Jev returns:

            {
                "answers": {
                    "<question>": {
                        "probability": ...
                    }
                }
            }
        """

        endpoint = (
            f"{self.gateway_base_url}/evaluate"
        )

        headers = {
            "Authorization": (
                f"Bearer {self.api_key}"
            ),
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.jev_model,
            "state": state,
            "questions": questions,
        }

        try:
            response = httpx.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=self.jev_timeout,
            )

            response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            status_code = (
                exc.response.status_code
                if exc.response is not None
                else "unknown"
            )

            response_text = ""

            if exc.response is not None:
                response_text = (
                    exc.response.text[:1000]
                )

            raise RuntimeError(
                "Jev evaluation request failed "
                f"with HTTP {status_code}: "
                f"{response_text}"
            ) from exc

        except httpx.RequestError as exc:
            raise RuntimeError(
                "Jev evaluation request could not "
                f"reach the Vercel AI Gateway: {exc}"
            ) from exc

        try:
            result = response.json()

        except ValueError as exc:
            raise RuntimeError(
                "Jev returned a non-JSON response."
            ) from exc

        if not isinstance(result, dict):
            raise RuntimeError(
                "Jev returned an invalid response shape."
            )

        return result

    def verify_with_jev(
        self,
        *,
        ticket: str,
        draft: str,
        evidence: str,
        citations: list[str],
    ) -> dict[str, Any]:
        """
        Verify a generated support response with Jev.

        Two independent boolean evaluations are performed
        in a single Jev request:

        1. Grounding
        2. Citation support
        """

        state = {
            "ticket": ticket,
            "draft": draft,
            "evidence": evidence,
            "citations": citations,
        }

        questions = {
            "grounded": {
                "type": "boolean",
                "instructions": (
                    "Is every substantive claim in "
                    "the drafted response directly "
                    "supported by the supplied evidence?"
                ),
            },
            "citation_supported": {
                "type": "boolean",
                "instructions": (
                    "Are the citations used by the "
                    "drafted response supported by "
                    "the supplied evidence sources?"
                ),
            },
        }

        return self.evaluate_with_jev(
            state=state,
            questions=questions,
        )
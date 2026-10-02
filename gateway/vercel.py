import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.schemas import SupportResponse, TicketAnalysis, KBCoverage

load_dotenv()


class VercelGateway:
    def __init__(self):
        api_key = os.getenv("AI_GATEWAY_API_KEY")

        if not api_key:
            raise ValueError(
                "AI_GATEWAY_API_KEY is not set."
            )

        self.llm = ChatOpenAI(
            model=os.getenv(
                "LLM_MODEL",
                "openai/gpt-6-luna",
            ),
            api_key=api_key,
            base_url="https://ai-gateway.vercel.sh/v1",
            temperature=0,
        )

        self.analysis_llm = self.llm.with_structured_output(TicketAnalysis)

        self.response_llm = self.llm.with_structured_output(SupportResponse)
        
        self.coverage_llm = self.llm.with_structured_output(KBCoverage)
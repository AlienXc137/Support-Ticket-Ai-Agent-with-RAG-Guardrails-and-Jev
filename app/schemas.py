from typing import Literal

from pydantic import BaseModel, Field


class Issue(BaseModel):
    type: str
    description: str


class TicketAnalysis(BaseModel):
    issues: list[Issue]
    primary_category: str
    urgency: str = Field(
        description="low, medium, high, or critical"
    )
    complexity: str = Field(
        description="low, medium, or high"
    )
    anger_score: float = Field(
        ge=0.0,
        le=1.0,
    )
    risk_flags: list[str]


class SupportResponse(BaseModel):
    answer: str
    citation_ids: list[str]


class KBCoverage(BaseModel):
    sufficient: bool = Field(
        description=(
            "Whether the internal KB contains enough "
            "information to answer the ticket."
        )
    )

    reason: str = Field(
        description="Why the KB is or is not sufficient."
    )

    source_type: Literal[
        "institute_info",
        "public_exam_info",
        "general_knowledge",
        "private_account_data",
        "other",
    ]
    
    
class VerificationResult(BaseModel):
    grounded: bool = Field(
        description=(
            "Whether the drafted response is fully supported "
            "by the supplied evidence."
        )
    )

    unsupported_claims: list[str] = Field(
        description=(
            "Claims in the response that are not supported "
            "by the supplied evidence."
        )
    )

    reasoning: str = Field(
        description=(
            "Concise explanation of why the response is "
            "or is not grounded."
        )
    )
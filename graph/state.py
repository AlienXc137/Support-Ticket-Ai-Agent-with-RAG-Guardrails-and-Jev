from typing import Any, TypedDict


class TicketState(TypedDict, total=False):
    # Input
    ticket_id: str
    raw_message: str
    channel: str

    # Sanitization
    masked_message: str
    pii_detected: list[str]
    
    # Guardrails
    input_allowed: bool
    guardrail_status: str
    guardrail_reason: str

    # Analysis
    issues: list[dict[str, Any]]
    primary_category: str
    urgency: str
    complexity: str
    anger_score: float
    risk_flags: list[str]

    # Retrieval
    retrieved_documents: list[dict[str, Any]]
    retrieval_score: float
    kb_coverage: bool

    # Web
    web_required: bool
    web_reason: str
    web_source_type: str
    web_results: list[dict[str, Any]]
    web_used: bool

    # Generation
    draft: str
    citations: list[str]
    verification_feedback: str

    # Verification
    verification_passed: bool
    verification_reason: str
    verification_grounded: bool
    verification_grounding_probability: float
    verification_citation_supported: bool
    verification_citation_probability: float
    verification_unsupported_claims: list[str]
    retry_count: int

    # Final decision
    decision: str
    reason_codes: list[str]

    # Errors
    error: str | None
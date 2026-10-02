from graph.state import TicketState


VALID_ACTIONS = {
    "approve",
    "reject",
    "edit",
}


def resolve_human_review(
    state: TicketState,
    action: str,
    reviewer_note: str = "",
    edited_response: str = "",
) -> TicketState:
    """Apply a human decision to a ticket waiting for review.

    Supported actions:

    approve
        Approve the existing generated draft.

    reject
        Reject the generated response. Nothing is sent.

    edit
        Approve an edited version of the generated response.
    """

    action = action.strip().lower()

    if action not in VALID_ACTIONS:
        raise ValueError(
            f"Invalid human review action: {action!r}. "
            f"Expected one of: {sorted(VALID_ACTIONS)}."
        )

    if state.get("decision") != "HUMAN_APPROVE":
        raise ValueError(
            "Human review can only be resolved for tickets "
            "whose system decision is HUMAN_APPROVE."
        )

    review_status = state.get(
        "review_status",
        "PENDING",
    )

    if review_status != "PENDING":
        raise ValueError(
            "Ticket is not currently waiting for human review."
        )

    draft = state.get(
        "draft",
        "",
    ).strip()

    if not draft:
        raise ValueError(
            "Cannot resolve human review because the draft is empty."
        )

    reviewer_note = reviewer_note.strip()

    if action == "approve":
        return {
            **state,
            "review_status": "APPROVED",
            "human_decision": "APPROVE",
            "reviewer_note": reviewer_note,
            "final_response": draft,
            "delivery_status": "READY_TO_SEND",
        }

    if action == "edit":
        edited_response = edited_response.strip()

        if not edited_response:
            raise ValueError(
                "edited_response is required when action='edit'."
            )

        return {
            **state,
            "review_status": "APPROVED_WITH_EDIT",
            "human_decision": "EDIT",
            "reviewer_note": reviewer_note,
            "final_response": edited_response,
            "delivery_status": "READY_TO_SEND",
        }

    return {
        **state,
        "review_status": "REJECTED",
        "human_decision": "REJECT",
        "reviewer_note": reviewer_note,
        "final_response": "",
        "delivery_status": "NOT_SENT",
    }
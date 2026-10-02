from human_review.human_review import resolve_human_review
from graph.nodes.decision import make_decision


def build_human_review_state() -> dict:
    return make_decision(
        {
            "ticket_id": "HITL-001",
            "raw_message": (
                "I cannot access my course recordings."
            ),
            "masked_message": (
                "I cannot access my course recordings."
            ),
            "primary_category": "course_access",
            "risk_flags": [],
            "web_required": False,
            "web_used": False,
            "verification_passed": False,
            "draft": (
                "Please check your course dashboard to access "
                "your lecture recordings."
            ),
        }
    )


def test_approve():
    state = build_human_review_state()

    assert state["decision"] == "HUMAN_APPROVE"
    assert state["review_status"] == "PENDING"
    assert state["delivery_status"] == "WAITING_HUMAN_REVIEW"

    result = resolve_human_review(
        state,
        action="approve",
        reviewer_note="Reviewed and approved.",
    )

    assert result["review_status"] == "APPROVED"
    assert result["human_decision"] == "APPROVE"
    assert result["delivery_status"] == "READY_TO_SEND"
    assert result["final_response"] == state["draft"]


def test_reject():
    state = build_human_review_state()

    result = resolve_human_review(
        state,
        action="reject",
        reviewer_note="Needs additional review.",
    )

    assert result["review_status"] == "REJECTED"
    assert result["human_decision"] == "REJECT"
    assert result["delivery_status"] == "NOT_SENT"
    assert result["final_response"] == ""


def test_edit():
    state = build_human_review_state()

    edited_response = (
        "Please verify that you are enrolled in the correct "
        "course and batch, then check your course dashboard."
    )

    result = resolve_human_review(
        state,
        action="edit",
        reviewer_note="Clarified the response.",
        edited_response=edited_response,
    )

    assert result["review_status"] == "APPROVED_WITH_EDIT"
    assert result["human_decision"] == "EDIT"
    assert result["delivery_status"] == "READY_TO_SEND"
    assert result["final_response"] == edited_response


def test_auto_reply_state():
    result = make_decision(
        {
            "ticket_id": "AUTO-001",
            "primary_category": "course_access",
            "risk_flags": [],
            "web_required": False,
            "web_used": False,
            "verification_passed": True,
            "draft": (
                "Please check your course dashboard."
            ),
        }
    )

    assert result["decision"] == "AUTO_REPLY"
    assert result["review_status"] == "NOT_REQUIRED"
    assert result["delivery_status"] == "READY_TO_SEND"
    assert (
        result["final_response"]
        == result["draft"]
    )


def test_invalid_action():
    state = build_human_review_state()

    try:
        resolve_human_review(
            state,
            action="something_else",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid action should raise ValueError."
        )


def main():
    test_approve()
    print("PASS: approve")

    test_reject()
    print("PASS: reject")

    test_edit()
    print("PASS: edit")

    test_auto_reply_state()
    print("PASS: auto reply state")

    test_invalid_action()
    print("PASS: invalid action")


if __name__ == "__main__":
    main()
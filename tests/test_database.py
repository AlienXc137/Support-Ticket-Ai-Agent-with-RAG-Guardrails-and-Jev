from pathlib import Path

import pytest

from app.database import (
    SQLiteTicketStore,
    TicketAlreadyExistsError,
    TicketNotFoundError,
)


def sample_state(
    ticket_id: str = "SQL-001",
) -> dict:
    return {
        "ticket_id": ticket_id,
        "raw_message": (
            "I cannot access my course recordings."
        ),
        "channel": "web",
        "masked_message": (
            "I cannot access my course recordings."
        ),
        "pii_detected": [],
        "primary_category": "course_access",
        "urgency": "low",
        "complexity": "low",
        "risk_flags": [],
        "kb_coverage": True,
        "web_required": False,
        "web_used": False,
        "draft": (
            "Please check your course dashboard."
        ),
        "citations": [
            "kb-001"
        ],
        "verification_passed": True,
        "retry_count": 0,
        "decision": "AUTO_REPLY",
        "reason_codes": [
            "STANDARD_SUPPORT_REQUEST"
        ],
        "review_status": "NOT_REQUIRED",
        "human_decision": "",
        "reviewer_note": "",
        "final_response": (
            "Please check your course dashboard."
        ),
        "delivery_status": "READY_TO_SEND",
    }


def test_create_and_get_persisted_state(
    tmp_path: Path,
):
    database = (
        tmp_path
        / "tickets.sqlite3"
    )

    store = SQLiteTicketStore(
        database
    )

    state = sample_state()

    store.create(state)

    assert store.get(
        "SQL-001"
    ) == state


def test_state_survives_store_reinitialization(
    tmp_path: Path,
):
    database = (
        tmp_path
        / "tickets.sqlite3"
    )

    state = sample_state()

    first_store = SQLiteTicketStore(
        database
    )

    first_store.create(state)

    reopened_store = SQLiteTicketStore(
        database
    )

    assert reopened_store.get(
        "SQL-001"
    ) == state


def test_duplicate_ticket_is_rejected(
    tmp_path: Path,
):
    store = SQLiteTicketStore(
        tmp_path / "tickets.sqlite3"
    )

    state = sample_state()

    store.create(state)

    with pytest.raises(
        TicketAlreadyExistsError
    ):
        store.create(state)


def test_update_persists_human_review_state(
    tmp_path: Path,
):
    database = (
        tmp_path
        / "tickets.sqlite3"
    )

    store = SQLiteTicketStore(
        database
    )

    state = sample_state()

    state.update(
        {
            "decision": "HUMAN_APPROVE",
            "review_status": "PENDING",
            "human_decision": "",
            "reviewer_note": "",
            "final_response": "",
            "delivery_status": (
                "WAITING_HUMAN_REVIEW"
            ),
        }
    )

    store.create(state)

    updated_state = {
        **state,
        "review_status": (
            "APPROVED_WITH_EDIT"
        ),
        "human_decision": "EDIT",
        "reviewer_note": (
            "Clarified the response."
        ),
        "final_response": (
            "Updated response."
        ),
        "delivery_status": (
            "READY_TO_SEND"
        ),
    }

    store.update(
        updated_state
    )

    reopened_store = SQLiteTicketStore(
        database
    )

    assert reopened_store.get(
        "SQL-001"
    ) == updated_state


def test_list_returns_most_recent_updates_first(
    tmp_path: Path,
):
    store = SQLiteTicketStore(
        tmp_path / "tickets.sqlite3"
    )

    first = sample_state(
        "SQL-001"
    )

    second = sample_state(
        "SQL-002"
    )

    store.create(first)
    store.create(second)

    updated_second = {
        **second,
        "decision": "HUMAN_APPROVE",
        "review_status": "PENDING",
    }

    store.update(
        updated_second
    )

    tickets = store.list()

    assert len(tickets) == 2

    assert (
        tickets[0]["ticket_id"]
        == "SQL-002"
    )


def test_list_can_filter_by_decision(
    tmp_path: Path,
):
    store = SQLiteTicketStore(
        tmp_path / "tickets.sqlite3"
    )

    store.create(
        sample_state("SQL-001")
    )

    human_state = {
        **sample_state("SQL-002"),
        "decision": "HUMAN_APPROVE",
        "review_status": "PENDING",
        "delivery_status": (
            "WAITING_HUMAN_REVIEW"
        ),
    }

    store.create(
        human_state
    )

    tickets = store.list(
        decision="HUMAN_APPROVE"
    )

    assert [
        ticket["ticket_id"]
        for ticket in tickets
    ] == [
        "SQL-002"
    ]


def test_missing_ticket_raises_not_found(
    tmp_path: Path,
):
    store = SQLiteTicketStore(
        tmp_path / "tickets.sqlite3"
    )

    with pytest.raises(
        TicketNotFoundError
    ):
        store.get(
            "DOES-NOT-EXIST"
        )


def test_database_file_is_created(
    tmp_path: Path,
):
    database = (
        tmp_path
        / "nested"
        / "tickets.sqlite3"
    )

    SQLiteTicketStore(
        database
    )

    assert database.exists()
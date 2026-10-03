from fastapi.testclient import TestClient

from app import main
from app.database import SQLiteTicketStore


class FakeWorkflow:
    def invoke(
        self,
        state: dict,
    ) -> dict:
        return {
            **state,
            "masked_message": state[
                "raw_message"
            ],
            "pii_detected": [],
            "primary_category": "course_access",
            "verification_passed": True,
            "decision": "AUTO_REPLY",
            "review_status": "NOT_REQUIRED",
            "delivery_status": "READY_TO_SEND",
            "draft": (
                "Please check your course dashboard."
            ),
            "final_response": (
                "Please check your course dashboard."
            ),
            "reason_codes": [
                "STANDARD_SUPPORT_REQUEST"
            ],
        }


def test_list_tickets_returns_persisted_history(
    tmp_path,
):
    original_store = main.ticket_store
    original_workflow = main.workflow

    try:
        main.ticket_store = SQLiteTicketStore(
            tmp_path / "tickets.sqlite3"
        )

        main.workflow = FakeWorkflow()

        client = TestClient(
            main.app
        )

        create_response = client.post(
            "/api/tickets",
            json={
                "ticket_id": "HIST-001",
                "message": (
                    "I cannot access "
                    "my course recordings."
                ),
                "channel": "web",
            },
        )

        assert (
            create_response.status_code
            == 200
        )

        history = client.get(
            "/api/tickets?limit=50"
        )

        assert (
            history.status_code
            == 200
        )

        payload = history.json()

        assert payload["count"] == 1

        ticket = payload[
            "tickets"
        ][0]

        assert (
            ticket["ticket_id"]
            == "HIST-001"
        )

        assert (
            ticket["decision"]
            == "AUTO_REPLY"
        )

        assert (
            ticket["review_status"]
            == "NOT_REQUIRED"
        )

        assert (
            ticket["verification_passed"]
            is True
        )

        assert ticket["created_at"]
        assert ticket["updated_at"]

        assert (
            ticket["message_preview"]
            == (
                "I cannot access "
                "my course recordings."
            )
        )

    finally:
        main.ticket_store = (
            original_store
        )

        main.workflow = (
            original_workflow
        )


def test_list_tickets_can_filter_by_decision(
    tmp_path,
):
    original_store = main.ticket_store
    original_workflow = main.workflow

    try:
        main.ticket_store = (
            SQLiteTicketStore(
                tmp_path / "tickets.sqlite3"
            )
        )

        main.ticket_store.create(
            {
                "ticket_id": "HIST-001",
                "masked_message": (
                    "Normal request"
                ),
                "primary_category": (
                    "course_access"
                ),
                "decision": "AUTO_REPLY",
                "review_status": (
                    "NOT_REQUIRED"
                ),
                "delivery_status": (
                    "READY_TO_SEND"
                ),
                "verification_passed": True,
            }
        )

        main.ticket_store.create(
            {
                "ticket_id": "HIST-002",
                "masked_message": (
                    "Needs review"
                ),
                "primary_category": (
                    "refund"
                ),
                "decision": "HUMAN_APPROVE",
                "review_status": "PENDING",
                "delivery_status": (
                    "WAITING_HUMAN_REVIEW"
                ),
                "verification_passed": False,
            }
        )

        client = TestClient(
            main.app
        )

        response = client.get(
            "/api/tickets?decision=HUMAN_APPROVE"
        )

        assert (
            response.status_code
            == 200
        )

        payload = response.json()

        assert (
            payload["count"]
            == 1
        )

        assert (
            payload["tickets"][0][
                "ticket_id"
            ]
            == "HIST-002"
        )

    finally:
        main.ticket_store = (
            original_store
        )

        main.workflow = (
            original_workflow
        )
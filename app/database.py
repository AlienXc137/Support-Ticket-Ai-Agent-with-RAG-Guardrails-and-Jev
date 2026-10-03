from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class TicketNotFoundError(KeyError):
    """Raised when a requested ticket does not exist."""


class TicketAlreadyExistsError(ValueError):
    """Raised when creating a ticket with an existing ticket ID."""


def _utc_now() -> str:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


class SQLiteTicketStore:
    """SQLite-backed persistence for support ticket workflow state.

    The complete TicketState is stored as JSON so new workflow fields can
    be introduced without requiring a database migration for every field.

    Frequently queried fields are also stored in dedicated SQLite columns
    so ticket history/filtering can be added efficiently later.
    """

    def __init__(
        self,
        database_path: str | Path | None = None,
    ) -> None:
        if database_path is None:
            database_path = os.getenv(
                "SUPPORT_TICKET_DB_PATH"
            )

        if database_path is None:
            project_root = (
                Path(__file__).resolve().parent.parent
            )

            database_path = (
                project_root
                / "data"
                / "support_tickets.sqlite3"
            )

        self.database_path = (
            Path(database_path)
            .expanduser()
            .resolve()
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path,
            timeout=30.0,
        )

        connection.row_factory = sqlite3.Row

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        connection.execute(
            "PRAGMA journal_mode = WAL"
        )

        connection.execute(
            "PRAGMA busy_timeout = 30000"
        )

        return connection

    def initialize(self) -> None:
        """Create the ticket persistence schema if needed."""
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    decision TEXT NOT NULL DEFAULT '',
                    review_status TEXT NOT NULL DEFAULT '',
                    delivery_status TEXT NOT NULL DEFAULT '',
                    primary_category TEXT NOT NULL DEFAULT ''
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_tickets_updated_at
                ON tickets(updated_at DESC)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_tickets_decision
                ON tickets(decision)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_tickets_review_status
                ON tickets(review_status)
                """
            )

    @staticmethod
    def _serialize_state(
        state: dict[str, Any],
    ) -> str:
        return json.dumps(
            state,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @staticmethod
    def _deserialize_state(
        state_json: str,
    ) -> dict[str, Any]:
        state = json.loads(state_json)

        if not isinstance(state, dict):
            raise ValueError(
                "Persisted ticket state must deserialize "
                "to a JSON object."
            )

        return state

    def create(
        self,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """Persist a new ticket state."""
        ticket_id = str(
            state.get("ticket_id", "")
        ).strip()

        if not ticket_id:
            raise ValueError(
                "Cannot persist a ticket without a ticket_id."
            )

        now = _utc_now()

        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO tickets (
                        ticket_id,
                        state_json,
                        created_at,
                        updated_at,
                        decision,
                        review_status,
                        delivery_status,
                        primary_category
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ticket_id,
                        self._serialize_state(state),
                        now,
                        now,
                        str(
                            state.get(
                                "decision",
                                "",
                            )
                        ),
                        str(
                            state.get(
                                "review_status",
                                "",
                            )
                        ),
                        str(
                            state.get(
                                "delivery_status",
                                "",
                            )
                        ),
                        str(
                            state.get(
                                "primary_category",
                                "",
                            )
                        ),
                    ),
                )

        except sqlite3.IntegrityError as exc:
            raise TicketAlreadyExistsError(
                f"Ticket '{ticket_id}' already exists."
            ) from exc

        return dict(state)

    def get(
        self,
        ticket_id: str,
    ) -> dict[str, Any]:
        """Return a ticket state."""
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT state_json
                FROM tickets
                WHERE ticket_id = ?
                """,
                (ticket_id,),
            ).fetchone()

        if row is None:
            raise TicketNotFoundError(
                f"Ticket '{ticket_id}' was not found."
            )

        return self._deserialize_state(
            row["state_json"]
        )

    def update(
        self,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """Persist an updated ticket state."""
        ticket_id = str(
            state.get("ticket_id", "")
        ).strip()

        if not ticket_id:
            raise ValueError(
                "Cannot persist a ticket without a ticket_id."
            )

        now = _utc_now()

        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE tickets
                SET
                    state_json = ?,
                    updated_at = ?,
                    decision = ?,
                    review_status = ?,
                    delivery_status = ?,
                    primary_category = ?
                WHERE ticket_id = ?
                """,
                (
                    self._serialize_state(state),
                    now,
                    str(
                        state.get(
                            "decision",
                            "",
                        )
                    ),
                    str(
                        state.get(
                            "review_status",
                            "",
                        )
                    ),
                    str(
                        state.get(
                            "delivery_status",
                            "",
                        )
                    ),
                    str(
                        state.get(
                            "primary_category",
                            "",
                        )
                    ),
                    ticket_id,
                ),
            )

            if cursor.rowcount == 0:
                raise TicketNotFoundError(
                    f"Ticket '{ticket_id}' was not found."
                )

        return dict(state)

    def list(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        decision: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return persisted tickets ordered by latest update."""
        if limit < 1:
            raise ValueError(
                "limit must be greater than zero."
            )

        if offset < 0:
            raise ValueError(
                "offset cannot be negative."
            )

        query = """
            SELECT state_json
            FROM tickets
        """

        parameters: list[Any] = []

        if decision is not None:
            query += """
                WHERE decision = ?
            """

            parameters.append(decision)

        query += """
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
        """

        parameters.extend(
            [
                limit,
                offset,
            ]
        )

        with self._connect() as connection:
            rows = connection.execute(
                query,
                parameters,
            ).fetchall()

        return [
            self._deserialize_state(
                row["state_json"]
            )
            for row in rows
        ]
        
    def list_summaries(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        decision: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return lightweight records for the ticket history view.

        Only the sanitized message preview is exposed. The raw customer
        message remains inside the persisted TicketState and is returned
        only when a specific ticket is opened.
        """
        if limit < 1:
            raise ValueError(
                "limit must be greater than zero."
            )

        if offset < 0:
            raise ValueError(
                "offset cannot be negative."
            )

        query = """
            SELECT
                ticket_id,
                state_json,
                created_at,
                updated_at,
                decision,
                review_status,
                delivery_status,
                primary_category
            FROM tickets
        """

        parameters: list[Any] = []

        if decision is not None:
            query += " WHERE decision = ?"
            parameters.append(decision)

        query += """
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
        """

        parameters.extend(
            [
                limit,
                offset,
            ]
        )

        with self._connect() as connection:
            rows = connection.execute(
                query,
                parameters,
            ).fetchall()

        summaries: list[dict[str, Any]] = []

        for row in rows:
            state = self._deserialize_state(
                row["state_json"]
            )

            masked_message = str(
                state.get(
                    "masked_message",
                    "",
                )
            ).strip()

            summaries.append(
                {
                    "ticket_id": row["ticket_id"],
                    "channel": state.get(
                        "channel",
                        "",
                    ),
                    "message_preview": (
                        masked_message[:180]
                        + "…"
                        if len(masked_message) > 180
                        else masked_message
                    ),
                    "primary_category": row[
                        "primary_category"
                    ],
                    "decision": row[
                        "decision"
                    ],
                    "review_status": row[
                        "review_status"
                    ],
                    "delivery_status": row[
                        "delivery_status"
                    ],
                    "verification_passed": state.get(
                        "verification_passed"
                    ),
                    "created_at": row[
                        "created_at"
                    ],
                    "updated_at": row[
                        "updated_at"
                    ],
                }
            )

        return summaries

    def delete(
        self,
        ticket_id: str,
    ) -> None:
        """Delete a ticket.

        This method is intentionally not exposed by the API yet.
        """
        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM tickets
                WHERE ticket_id = ?
                """,
                (ticket_id,),
            )

            if cursor.rowcount == 0:
                raise TicketNotFoundError(
                    f"Ticket '{ticket_id}' was not found."
                )
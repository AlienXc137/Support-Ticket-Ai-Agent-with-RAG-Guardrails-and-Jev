from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Literal

from graph.graph import build_graph
from human_review.human_review import resolve_human_review


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"


app = FastAPI(
    title="Support Ticket Triage & Resolution Agent",
    version="0.1.0",
    description=(
        "API layer for the LangGraph-based support ticket "
        "triage, verification, and human-review workflow."
    ),
)


app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)


workflow = build_graph()

ticket_store: dict[str, dict] = {}


class TicketCreateRequest(BaseModel):
    ticket_id: str | None = None
    message: str = Field(min_length=1)
    channel: str = "web"


class HumanReviewRequest(BaseModel):
    action: Literal["approve", "reject", "edit"]
    reviewer_note: str = ""
    edited_response: str = ""


def _get_ticket_or_404(ticket_id: str) -> dict:
    state = ticket_store.get(ticket_id)

    if state is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket '{ticket_id}' was not found.",
        )

    return state


@app.get(
    "/",
    response_class=FileResponse,
    include_in_schema=False,
)
def serve_frontend():
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "support-ticket-agent",
    }


@app.post("/api/tickets")
def create_ticket(
    request: TicketCreateRequest,
):
    ticket_id = (
        request.ticket_id.strip()
        if request.ticket_id
        else f"TKT-{uuid4().hex[:8].upper()}"
    )

    if ticket_id in ticket_store:
        raise HTTPException(
            status_code=409,
            detail=f"Ticket '{ticket_id}' already exists.",
        )

    initial_state = {
        "ticket_id": ticket_id,
        "raw_message": request.message,
        "channel": request.channel,
    }

    try:
        result = workflow.invoke(initial_state)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {exc}",
        ) from exc

    ticket_store[ticket_id] = dict(result)

    return {
        "ticket_id": ticket_id,
        "state": result,
    }


@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    return {
        "ticket_id": ticket_id,
        "state": _get_ticket_or_404(ticket_id),
    }


@app.post("/api/tickets/{ticket_id}/review")
def review_ticket(
    ticket_id: str,
    request: HumanReviewRequest,
):
    state = _get_ticket_or_404(ticket_id)

    try:
        result = resolve_human_review(
            state,
            action=request.action,
            reviewer_note=request.reviewer_note,
            edited_response=request.edited_response,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    ticket_store[ticket_id] = dict(result)

    return {
        "ticket_id": ticket_id,
        "state": result,
    }

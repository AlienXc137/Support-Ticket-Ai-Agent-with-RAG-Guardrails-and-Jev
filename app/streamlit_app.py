import html
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Streamlit executes this file from the app/ directory. Add the project root
# so sibling packages such as graph/, gateway/, retrieval/, and web/ remain
# importable when running `streamlit run app/streamlit_app.py`.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import streamlit.components.v1 as components

from graph.graph import build_graph
from human_review.human_review import resolve_human_review


st.set_page_config(
    page_title="Support AI Operations",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------

st.markdown(
    """
<style>
    :root {
        --bg: #0b0f14;
        --panel: #111820;
        --panel-2: #0e141b;
        --border: #24303c;
        --text: #e6edf3;
        --muted: #8b98a8;
        --primary: #5b8cff;
        --success: #22c55e;
        --warning: #f59e0b;
        --danger: #ef4444;
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    [data-testid="stSidebar"] {
        background: #0a0e13;
        border-right: 1px solid var(--border);
    }

    [data-testid="stHeader"] {
        background: rgba(11, 15, 20, 0.92);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.2rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(135deg, #111820 0%, #0d131a 100%);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 22px 24px;
        margin-bottom: 18px;
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.22);
    }

    .eyebrow {
        color: #7f8da0;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-size: 11px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .hero-title {
        color: var(--text);
        font-size: 30px;
        line-height: 1.1;
        font-weight: 750;
        margin: 0;
    }

    .hero-subtitle {
        color: var(--muted);
        margin-top: 8px;
        font-size: 14px;
    }

    .section-title {
        color: var(--text);
        font-size: 16px;
        font-weight: 700;
        margin: 0 0 10px 0;
    }

    .card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 16px;
        margin-bottom: 14px;
    }

    .metric-card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 14px 15px;
        min-height: 92px;
    }

    .metric-label {
        color: var(--muted);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
    }

    .metric-value {
        color: var(--text);
        font-size: 21px;
        font-weight: 750;
        margin-top: 5px;
    }

    .metric-sub {
        color: #718092;
        font-size: 11px;
        margin-top: 3px;
    }

    .pill {
        display: inline-block;
        padding: 5px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.03em;
        margin-right: 6px;
        border: 1px solid var(--border);
        background: #0d141b;
    }

    .pill-success { color: var(--success); }
    .pill-warning { color: var(--warning); }
    .pill-danger { color: var(--danger); }
    .pill-primary { color: var(--primary); }
    .pill-neutral { color: #aab5c2; }

    .ticket-box {
        background: var(--panel-2);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 14px;
        color: #d6dee7;
        font-size: 14px;
        line-height: 1.6;
        white-space: pre-wrap;
    }

    .draft-box {
        background: #0d151e;
        border: 1px solid #2a3949;
        border-radius: 12px;
        padding: 15px;
        color: #e8eef5;
        font-size: 14px;
        line-height: 1.65;
        white-space: pre-wrap;
    }

    .evidence-item {
        background: #0c131a;
        border: 1px solid var(--border);
        border-radius: 11px;
        padding: 12px;
        margin-bottom: 8px;
    }

    .evidence-meta {
        color: #7d8a99;
        font-size: 11px;
        margin-bottom: 4px;
    }

    .evidence-title {
        color: #dce5ee;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .evidence-text {
        color: #aab5c2;
        font-size: 12px;
        line-height: 1.5;
    }

    .decision-banner {
        border-radius: 14px;
        padding: 15px 16px;
        margin-bottom: 14px;
        border: 1px solid var(--border);
        background: #0e141b;
    }

    .decision-title {
        font-size: 14px;
        font-weight: 800;
        letter-spacing: 0.04em;
        margin-bottom: 5px;
    }

    .decision-note {
        color: var(--muted);
        font-size: 12px;
    }

    .progress-shell {
        background: #0a0f14;
        border: 1px solid var(--border);
        height: 8px;
        border-radius: 999px;
        overflow: hidden;
        margin-top: 7px;
    }

    .progress-fill {
        height: 100%;
        border-radius: 999px;
    }

    .sidebar-title {
        color: #dce5ee;
        font-weight: 750;
        font-size: 16px;
        margin-bottom: 2px;
    }

    .sidebar-subtitle {
        color: #758293;
        font-size: 11px;
        margin-bottom: 18px;
    }

    .footer-note {
        color: #657284;
        font-size: 11px;
        text-align: center;
        padding-top: 10px;
    }

    div[data-testid="stButton"] > button {
        border-radius: 10px;
        font-weight: 700;
        min-height: 42px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""))


def pct(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


def render_metric(
    label: str,
    value: str,
    sub: str = "",
) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{esc(label)}</div>
            <div class="metric-value">{esc(value)}</div>
            <div class="metric-sub">{esc(sub)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_progress(
    label: str,
    probability: Any,
) -> None:
    value = pct(probability)
    percentage = value * 100

    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="color:#9aa7b5;font-size:12px;">{esc(label)}</span>
            <span style="color:#e6edf3;font-size:12px;font-weight:700;">{percentage:.0f}%</span>
        </div>
        <div class="progress-shell">
            <div class="progress-fill" style="width:{percentage:.1f}%;background:#5b8cff;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">AI Support Operations</div>
            <div class="hero-title">Support Ticket Triage &amp; Resolution Agent</div>
            <div class="hero-subtitle">
                Secure intake · Hybrid RAG · Controlled web fallback · Jev verification · Human review
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    components.html(
        """
        <div style="
            display:flex;
            justify-content:flex-end;
            align-items:center;
            gap:8px;
            background:#0e141b;
            border:1px solid #24303c;
            border-radius:10px;
            padding:8px 12px;
            font-family:Inter,system-ui,sans-serif;
            color:#8b98a8;
            font-size:12px;
        ">
            <span style="
                width:8px;
                height:8px;
                border-radius:50%;
                background:#22c55e;
                box-shadow:0 0 10px rgba(34,197,94,.65);
            "></span>
            <span>Workflow online</span>
            <span id="clock" style="color:#d9e2eb;"></span>
            <script>
                const clock = document.getElementById("clock");
                const tick = () => {
                    clock.textContent = new Date().toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit"
                    });
                };
                tick();
                setInterval(tick, 1000);
            </script>
        </div>
        """,
        height=46,
    )


def render_evidence(state: dict) -> None:
    documents = state.get("retrieved_documents", [])
    web_results = state.get("web_results", [])

    if not documents and not web_results:
        st.markdown(
            '<div class="card"><div style="color:#7f8c9b;font-size:12px;">No evidence records available.</div></div>',
            unsafe_allow_html=True,
        )
        return

    for document in documents:
        metadata = document.get("metadata", {})
        st.markdown(
            f"""
            <div class="evidence-item">
                <div class="evidence-meta">INTERNAL_KB · {esc(metadata.get("id", ""))}</div>
                <div class="evidence-title">{esc(metadata.get("title", ""))}</div>
                <div class="evidence-text">{esc(document.get("content", ""))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for index, result in enumerate(web_results, start=1):
        st.markdown(
            f"""
            <div class="evidence-item">
                <div class="evidence-meta">APPROVED_WEB · web-{index}</div>
                <div class="evidence-title">{esc(result.get("title", ""))}</div>
                <div class="evidence-text">{esc(result.get("content", ""))}</div>
                <div style="color:#5b8cff;font-size:11px;margin-top:6px;word-break:break-all;">{esc(result.get("url", ""))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_state(state: dict) -> None:
    decision = state.get("decision", "")
    review_status = state.get("review_status", "")
    delivery_status = state.get("delivery_status", "")

    if decision == "AUTO_REPLY":
        tone = "pill-success"
        title = "AUTO REPLY READY"
        note = "All configured automated gates passed."
    elif decision == "HUMAN_APPROVE":
        tone = "pill-warning"
        title = "HUMAN REVIEW REQUIRED"
        note = "The system has held the response for reviewer action."
    else:
        tone = "pill-neutral"
        title = decision or "NO DECISION"
        note = "Workflow state is available below."

    st.markdown(
        f"""
        <div class="decision-banner">
            <div class="decision-title"><span class="pill {tone}">{esc(title)}</span></div>
            <div class="decision-note">
                Review: {esc(review_status or "—")} · Delivery: {esc(delivery_status or "—")} · {esc(note)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(5)
    with cols[0]:
        render_metric(
            "Ticket",
            state.get("ticket_id", "—"),
        )
    with cols[1]:
        render_metric(
            "Category",
            state.get("primary_category", "—"),
        )
    with cols[2]:
        render_metric(
            "Urgency",
            state.get("urgency", "—"),
        )
    with cols[3]:
        render_metric(
            "KB Coverage",
            "Yes" if state.get("kb_coverage") else "No",
        )
    with cols[4]:
        render_metric(
            "Web Used",
            "Yes" if state.get("web_used") else "No",
        )

    left, right = st.columns([1, 1])

    with left:
        st.markdown('<div class="section-title">Ticket</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="ticket-box">{esc(state.get("masked_message", ""))}</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-title" style="margin-top:18px;">Analysis</div>', unsafe_allow_html=True)
        risk_flags = state.get("risk_flags", [])
        issues = state.get("issues", [])

        analysis_rows = [
            f"<b>Complexity:</b> {esc(state.get('complexity', '—'))}",
            f"<b>Anger score:</b> {float(state.get('anger_score', 0.0)):.2f}",
            f"<b>Risk flags:</b> {esc(', '.join(risk_flags) if risk_flags else 'None')}",
            f"<b>Issues:</b> {esc('; '.join(item.get('description', '') for item in issues) if issues else 'None')}",
        ]
        st.markdown(
            f'<div class="card" style="font-size:12px;line-height:1.8;color:#aab5c2;">{"<br>".join(analysis_rows)}</div>',
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="section-title">Verification</div>', unsafe_allow_html=True)
        grounding = state.get("verification_grounding_probability", 0.0)
        citation = state.get("verification_citation_probability", 0.0)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        render_progress("Grounding", grounding)
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        render_progress("Citation support", citation)
        st.markdown(
            f"""
            <div style="margin-top:14px;color:#aab5c2;font-size:12px;line-height:1.7;">
                <b>Status:</b> {esc("PASS" if state.get("verification_passed") else "REVIEW") }<br>
                <b>Reason:</b> {esc(state.get("verification_reason", "—"))}<br>
                <b>Unsupported claims:</b> {esc(", ".join(state.get("verification_unsupported_claims", [])) or "None reported")}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title" style="margin-top:18px;">Reason Codes</div>', unsafe_allow_html=True)
        reasons = state.get("reason_codes", [])
        pills = "".join(
            f'<span class="pill pill-warning">{esc(reason)}</span>'
            for reason in reasons
        ) or '<span class="pill pill-neutral">None</span>'
        st.markdown(
            f'<div class="card">{pills}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">Evidence</div>', unsafe_allow_html=True)
    render_evidence(state)

    st.markdown('<div class="section-title" style="margin-top:18px;">Generated Response</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="draft-box">{esc(state.get("draft", ""))}</div>',
        unsafe_allow_html=True,
    )


def run_workflow(ticket_id: str, message: str, channel: str) -> None:
    graph = build_graph()

    ticket = {
        "ticket_id": ticket_id.strip() or "WEB-001",
        "raw_message": message,
        "channel": channel,
    }

    with st.spinner("Running support workflow..."):
        result = graph.invoke(ticket)

    st.session_state.workflow_state = result
    st.session_state.review_complete = False


def apply_review(
    action: str,
    reviewer_note: str = "",
    edited_response: str = "",
) -> None:
    state = st.session_state.get("workflow_state")

    if not state:
        return

    result = resolve_human_review(
        state,
        action=action,
        reviewer_note=reviewer_note,
        edited_response=edited_response,
    )

    st.session_state.workflow_state = result
    st.session_state.review_complete = True


# -----------------------------------------------------------------------------
# App
# -----------------------------------------------------------------------------

render_header()

if "workflow_state" not in st.session_state:
    st.session_state.workflow_state = None

if "review_complete" not in st.session_state:
    st.session_state.review_complete = False

with st.sidebar:
    st.markdown('<div class="sidebar-title">Workflow Console</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Run the existing LangGraph pipeline and resolve held responses.</div>', unsafe_allow_html=True)

    ticket_id = st.text_input(
        "Ticket ID",
        value="WEB-001",
    )

    channel = st.selectbox(
        "Channel",
        ["web", "email", "chat", "portal"],
        index=0,
    )

    message = st.text_area(
        "Customer ticket",
        value="I cannot access my course recordings.",
        height=170,
    )

    run_clicked = st.button(
        "Run Support Workflow",
        type="primary",
        use_container_width=True,
    )

    if run_clicked:
        if not message.strip():
            st.error("Customer ticket cannot be empty.")
        else:
            try:
                run_workflow(ticket_id, message, channel)
                st.rerun()
            except Exception as exc:
                st.exception(exc)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

    if st.session_state.workflow_state:
        if st.button(
            "Clear Current Ticket",
            use_container_width=True,
        ):
            st.session_state.workflow_state = None
            st.session_state.review_complete = False
            st.rerun()

    st.markdown(
        '<div class="footer-note">The UI does not reimplement workflow logic. It calls the existing graph and HITL resolver.</div>',
        unsafe_allow_html=True,
    )

state = st.session_state.workflow_state

if not state:
    st.markdown(
        """
        <div class="card" style="padding:34px;text-align:center;">
            <div style="color:#dce5ee;font-size:18px;font-weight:750;">No ticket processed yet</div>
            <div style="color:#7f8c9b;font-size:13px;margin-top:6px;">Enter a support ticket from the left panel to start the workflow.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

render_state(state)

# -----------------------------------------------------------------------------
# Human review panel
# -----------------------------------------------------------------------------

if (
    state.get("decision") == "HUMAN_APPROVE"
    and state.get("review_status") == "PENDING"
):
    st.markdown(
        """
        <div class="card" style="margin-top:18px;border-color:#3a3321;">
            <div class="section-title">Human Review</div>
            <div style="color:#8f9baa;font-size:12px;line-height:1.6;margin-bottom:12px;">
                This response was held by the deterministic decision gate. Review the evidence and draft before allowing delivery.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    edited_response = st.text_area(
        "Response for reviewer",
        value=state.get("draft", ""),
        height=170,
        key="review_response",
    )

    reviewer_note = st.text_input(
        "Reviewer note",
        value="",
        key="review_note",
    )

    approve_col, edit_col, reject_col = st.columns(3)

    with approve_col:
        if st.button(
            "Approve",
            type="primary",
            use_container_width=True,
        ):
            try:
                apply_review(
                    action="approve",
                    reviewer_note=reviewer_note,
                )
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    with edit_col:
        if st.button(
            "Approve with Edit",
            use_container_width=True,
        ):
            try:
                apply_review(
                    action="edit",
                    reviewer_note=reviewer_note,
                    edited_response=edited_response,
                )
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    with reject_col:
        if st.button(
            "Reject",
            use_container_width=True,
        ):
            try:
                apply_review(
                    action="reject",
                    reviewer_note=reviewer_note,
                )
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

# -----------------------------------------------------------------------------
# Final state
# -----------------------------------------------------------------------------

state = st.session_state.workflow_state

if state.get("review_status") in {
    "APPROVED",
    "APPROVED_WITH_EDIT",
    "REJECTED",
}:
    st.markdown('<div class="section-title" style="margin-top:20px;">Review Outcome</div>', unsafe_allow_html=True)

    if state.get("review_status") == "REJECTED":
        st.error("Response rejected. Delivery is blocked.")
    else:
        final_response = state.get("final_response", "")
        st.success("Response approved. Delivery is ready.")
        st.markdown(
            f'<div class="draft-box">{esc(final_response)}</div>',
            unsafe_allow_html=True,
        )

        if state.get("reviewer_note"):
            st.caption(f"Reviewer note: {state['reviewer_note']}")

st.markdown(
    '<div class="footer-note">Prototype HITL console · Persistence, authentication, audit storage, and observability remain later stages.</div>',
    unsafe_allow_html=True,
)

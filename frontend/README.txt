Support Agent Frontend — rebuilt from scratch

Files:
- index.html
- app.js
- styles.css

Copy these three files into your project's frontend/ directory.

The frontend expects the existing FastAPI endpoints:
- POST /api/tickets
- GET /api/tickets
- GET /api/tickets/{ticket_id}
- POST /api/tickets/{ticket_id}/review

It includes four built-in demo tickets:
1. KB-supported course access -> demonstrates normal RAG + auto reply.
2. Current exam schedule -> demonstrates coverage gate + web fallback + human review.
3. Prompt injection -> demonstrates Presidio/guardrail blocking.
4. Refund/account request -> demonstrates sensitive handling + HITL.

Demo tickets are UI presets; clicking one loads its message into the composer. It does not insert fake results into the backend. Run the agent to process it through the real workflow.

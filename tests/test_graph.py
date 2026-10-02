from graph.graph import build_graph


def main():
    app = build_graph()

    ticket = {
        "ticket_id": "WEB-001",
        "raw_message": (
            "I cannot access my course recordings."
        ),
        "channel": "web",
    }

    result = app.invoke(ticket)

    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)

    print(
        f"Ticket ID:       "
        f"{result.get('ticket_id')}"
    )

    print(
        f"Raw message:     "
        f"{result.get('raw_message')}"
    )

    print(
        f"Masked message:   "
        f"{result.get('masked_message')}"
    )

    print(
        f"PII detected:     "
        f"{result.get('pii_detected')}"
    )

    print(
        f"Category:         "
        f"{result.get('primary_category')}"
    )

    print(
        f"KB coverage:      "
        f"{result.get('kb_coverage')}"
    )

    print(
        f"Web required:     "
        f"{result.get('web_required')}"
    )

    print(
        f"Web source type:  "
        f"{result.get('web_source_type')}"
    )

    print(
        f"Web used:         "
        f"{result.get('web_used')}"
    )

    print(
        f"Web results:      "
        f"{len(result.get('web_results', []))}"
    )

    print(
        f"Draft:            "
        f"{result.get('draft')}"
    )

    print(
        f"Citations:        "
        f"{result.get('citations')}"
    )

    print("\n--- Jev Verification ---")

    print(
        f"Verification:     "
        f"{result.get('verification_passed')}"
    )

    print(
        f"Verification reason:\n"
        f"{result.get('verification_reason')}"
    )

    print(
        f"Grounded:         "
        f"{result.get('verification_grounded')}"
    )

    print(
        f"Grounding prob:   "
        f"{result.get('verification_grounding_probability')}"
    )

    print(
        f"Citations OK:     "
        f"{result.get('verification_citation_supported')}"
    )

    print(
        f"Citation prob:    "
        f"{result.get('verification_citation_probability')}"
    )

    print(
        f"Unsupported:      "
        f"{result.get('verification_unsupported_claims')}"
    )

    print(
        f"Retry count:      "
        f"{result.get('retry_count', 0)}"
    )

    print(
        f"Feedback:         "
        f"{result.get('verification_feedback')}"
    )

    print("\n--- Final Decision ---")

    print(
        f"Decision:         "
        f"{result.get('decision')}"
    )

    print(
        f"Reasons:          "
        f"{result.get('reason_codes')}"
    )

    print("=" * 80)


if __name__ == "__main__":
    main()
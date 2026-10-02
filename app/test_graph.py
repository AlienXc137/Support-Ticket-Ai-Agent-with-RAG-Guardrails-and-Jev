from graph.graph import build_graph


def run_ticket(
    ticket_id: str,
    message: str,
) -> None:
    app = build_graph()

    ticket = {
        "ticket_id": ticket_id,
        "raw_message": message,
        "channel": "web",
    }

    result = app.invoke(ticket)

    print("\n" + "=" * 80)
    print(f"TICKET: {ticket_id}")
    print("=" * 80)

    print(f"Raw message: {result.get('raw_message')}")
    print(f"Masked:      {result.get('masked_message')}")
    print(f"PII:         {result.get('pii_detected')}")
    print(f"Category:    {result.get('primary_category')}")
    print(f"KB coverage: {result.get('kb_coverage')}")
    print(f"Web required:{result.get('web_required')}")
    print(f"Source type: {result.get('web_source_type')}")
    print(f"Web used:    {result.get('web_used')}")
    print(f"Web reason:  {result.get('web_reason')}")
    print(f"Web results: {len(result.get('web_results', []))}")
    print(f"Draft:       {result.get('draft')}")
    print(f"Verification: {result.get('verification_passed')}")
    print(f"Decision:    {result.get('decision')}")
    print(f"Reasons:     {result.get('reason_codes')}")


def main():
    run_ticket(
        "WEB-001",
        "When is the next public examination scheduled?",
    )


if __name__ == "__main__":
    main()
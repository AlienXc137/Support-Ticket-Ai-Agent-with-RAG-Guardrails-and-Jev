from graph.graph import build_graph


def main():
    app = build_graph()

    ticket = {
        "ticket_id": "TICKET-001",
        "raw_message": (
            "I was charged twice for my course and I still cannot access the recordings."
        ),
        "channel": "web",
    }

    result = app.invoke(ticket)

    print("\n=== FINAL RESULT ===")
    print(f"Category: {result.get('primary_category')}")
    print(f"Issues: {result.get('issues')}")
    print(f"Draft: {result.get('draft')}")
    print(f"Verification: {result.get('verification_passed')}")
    print(f"Decision: {result.get('decision')}")
    print(f"Reasons: {result.get('reason_codes')}")


if __name__ == "__main__":
    main()
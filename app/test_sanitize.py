from graph.nodes.sanitize import sanitize_ticket


def main():
    state = {
        "raw_message": (
            "I cannot access my course. "
            "My email is student@example.com and "
            "my phone number is 9876543210."
        )
    }

    result = sanitize_ticket(state)

    print("=" * 70)
    print("RAW:")
    print(state["raw_message"])

    print("\nMASKED:")
    print(result["masked_message"])

    print("\nPII DETECTED:")
    print(result["pii_detected"])


if __name__ == "__main__":
    main()
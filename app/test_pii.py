from guardrails.pii import mask_pii


def main():
    messages = [
        "My email is student@example.com and I cannot access my course.",
        "Call me at 9876543210 regarding my account.",
        "My student ID is GCET20261234 and I need help.",
        "My Aadhaar number is 1234 5678 9012.",
        "I cannot access my course recordings.",
    ]

    for message in messages:
        masked, detected = mask_pii(message)

        print("\n" + "=" * 70)
        print(f"INPUT:   {message}")
        print(f"MASKED:  {masked}")
        print(f"PII:     {detected}")


if __name__ == "__main__":
    main()
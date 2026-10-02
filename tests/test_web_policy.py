from web.policy import WebPolicy


def main():
    policy = WebPolicy()

    source_types = [
        "institute_info",
        "public_exam_info",
        "general_knowledge",
        "private_account_data",
        "other",
    ]

    for source_type in source_types:
        config = policy.get_policy(
            source_type
        )

        print("\n" + "=" * 70)
        print(f"SOURCE TYPE: {source_type}")
        print(f"ENABLED:     {config.get('enabled')}")
        print(f"DOMAINS:     {config.get('domains')}")


if __name__ == "__main__":
    main()
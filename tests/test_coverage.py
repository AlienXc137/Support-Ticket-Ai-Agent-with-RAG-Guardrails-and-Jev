from graph.nodes.coverage import check_kb_coverage


def run_case(
    message: str,
    documents: list[dict],
) -> None:
    state = {
        "masked_message": message,
        "retrieved_documents": documents,
    }

    result = check_kb_coverage(state)

    print("\n" + "=" * 80)
    print(f"TICKET: {message}")
    print("=" * 80)

    print(f"KB COVERAGE : {result.get('kb_coverage')}")
    print(f"WEB REQUIRED: {result.get('web_required')}")
    print(f"WEB REASON  : {result.get('web_reason')}")
    print(f"SOURCE TYPE : {result.get('web_source_type')}")


def main():
    # Case 1: KB clearly contains the answer.
    run_case(
        "I cannot access my course recordings.",
        [
            {
                "content": (
                    "Students enrolled in a course can access lecture "
                    "recordings from the course dashboard. If recordings "
                    "are missing, verify that the student is enrolled in "
                    "the correct course and batch. Recording access may "
                    "take some time after a live lecture is completed."
                ),
                "metadata": {
                    "id": "kb-001",
                    "title": "Course Recording Access",
                    "category": "course_access",
                },
            }
        ],
    )

    # Case 2: KB has only generic exam information, not the actual date.
    run_case(
        "When is the next public examination scheduled?",
        [
            {
                "content": (
                    "Exam dates and schedules are published through the "
                    "official academic communication channels. Students "
                    "should check the latest official announcement for "
                    "the applicable examination schedule."
                ),
                "metadata": {
                    "id": "kb-007",
                    "title": "Exam Schedule",
                    "category": "academic",
                },
            }
        ],
    )

    # Case 3: Private account information.
    run_case(
        "Why hasn't my personal payment been refunded?",
        [
            {
                "content": (
                    "Refund requests are handled according to the "
                    "applicable course refund policy. Support should "
                    "verify the purchase, payment transaction, and "
                    "refund eligibility before confirming whether "
                    "a refund can be issued."
                ),
                "metadata": {
                    "id": "kb-003",
                    "title": "Course Refund Policy",
                    "category": "refund",
                },
            }
        ],
    )


if __name__ == "__main__":
    main()
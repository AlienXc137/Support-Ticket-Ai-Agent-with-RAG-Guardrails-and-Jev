from graph.nodes.decision import make_decision


def run_case(
    name: str,
    state: dict,
    expected_decision: str,
    expected_reasons: list[str],
) -> None:
    result = make_decision(state)

    assert result["decision"] == expected_decision, (
        name,
        result["decision"],
        expected_decision,
    )

    for reason in expected_reasons:
        assert reason in result["reason_codes"], (
            name,
            result["reason_codes"],
            reason,
        )

    print(f"PASS: {name}")
    print(f"  decision    = {result['decision']}")
    print(f"  reason_codes= {result['reason_codes']}")


def main():
    # 1. Safe + KB-supported + verified -> AUTO_REPLY.
    run_case(
        "safe verified KB response",
        {
            "primary_category": "course_access",
            "risk_flags": [],
            "web_required": False,
            "web_used": False,
            "verification_passed": True,
        },
        "AUTO_REPLY",
        ["STANDARD_SUPPORT_REQUEST"],
    )

    # 2. Verification failure -> HUMAN_APPROVE.
    run_case(
        "verification failure",
        {
            "primary_category": "course_access",
            "risk_flags": [],
            "web_required": False,
            "web_used": False,
            "verification_passed": False,
        },
        "HUMAN_APPROVE",
        ["VERIFICATION_FAILED"],
    )

    # 3. Private/disallowed web request remains human-routed.
    run_case(
        "web not allowed",
        {
            "primary_category": "account",
            "risk_flags": [],
            "web_required": True,
            "web_used": False,
            "verification_passed": True,
            "reason_codes": ["WEB_NOT_ALLOWED"],
        },
        "HUMAN_APPROVE",
        [
            "WEB_NOT_ALLOWED",
            "WEB_REQUIRED_BUT_UNAVAILABLE",
        ],
    )

    # 4. Sensitive category -> HUMAN_APPROVE.
    run_case(
        "sensitive category",
        {
            "primary_category": "refund",
            "risk_flags": [],
            "web_required": False,
            "web_used": False,
            "verification_passed": True,
        },
        "HUMAN_APPROVE",
        ["SENSITIVE_CATEGORY"],
    )

    # 5. Risk flag -> HUMAN_APPROVE.
    run_case(
        "risk flag",
        {
            "primary_category": "technical",
            "risk_flags": ["security-sensitive"],
            "web_required": False,
            "web_used": False,
            "verification_passed": True,
        },
        "HUMAN_APPROVE",
        ["RISK_FLAG"],
    )

    # 6. Web was used -> HUMAN_APPROVE and preserve provenance.
    run_case(
        "web sourced response",
        {
            "primary_category": "academic",
            "risk_flags": [],
            "web_required": True,
            "web_used": True,
            "verification_passed": True,
        },
        "HUMAN_APPROVE",
        ["WEB_SOURCED_RESPONSE"],
    )

    # 7. Web search returned no results -> fail closed.
    run_case(
        "web no results",
        {
            "primary_category": "academic",
            "risk_flags": [],
            "web_required": True,
            "web_used": False,
            "verification_passed": True,
            "reason_codes": ["WEB_NO_RESULTS"],
        },
        "HUMAN_APPROVE",
        [
            "WEB_NO_RESULTS",
            "WEB_REQUIRED_BUT_UNAVAILABLE",
        ],
    )


if __name__ == "__main__":
    main()
from gateway.vercel import VercelGateway


def main():
    gateway = VercelGateway()

    result = gateway.verify_with_jev(
        ticket="I cannot access my course recordings.",
        draft=(
            "Course recordings are normally available "
            "within 24 hours after the live class."
        ),
        evidence=(
            "kb-001: Course Recording Access — "
            "Course recordings are normally available "
            "within 24 hours after the live class."
        ),
    )

    print("=" * 70)
    print("JEV VERIFICATION")
    print("=" * 70)
    print(result)


if __name__ == "__main__":
    main()
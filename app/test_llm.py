from gateway.vercel import VercelGateway


def main():
    gateway = VercelGateway()

    message = """
    I was charged twice for my course and I still cannot access
    the recordings. I have already contacted support twice.
    """

    result = gateway.analyze_ticket(message)

    print("\n=== LLM ANALYSIS ===")

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
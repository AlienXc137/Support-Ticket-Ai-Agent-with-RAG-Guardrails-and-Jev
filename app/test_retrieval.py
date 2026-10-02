from retrieval.hybrid import build_hybrid_retriever


def main():
    retriever = build_hybrid_retriever()

    test_queries = [
        "I cannot access my course recordings.",
        # "I was charged twice for my course.",
        # "How do I reset my account password?",
        # "I cannot see my assigned batch.",
        # "My payment was successful but my course is missing.",
    ]

    for query in test_queries:
        print("\n" + "=" * 80)
        print(f"QUERY: {query}")
        print("=" * 80)

        documents = retriever.invoke(query)

        for rank, document in enumerate(documents, start=1):
            print(f"\n[{rank}]")
            print(f"ID:       {document.metadata.get('id')}")
            print(f"TITLE:    {document.metadata.get('title')}")
            print(f"CATEGORY: {document.metadata.get('category')}")
            print(f"CONTENT:  {document.page_content}")


if __name__ == "__main__":
    main()
from retrieval.embeddings import get_embeddings


def main():
    embeddings = get_embeddings()

    text = "I cannot access my course recordings."

    vector = embeddings.embed_query(text)

    print("=" * 70)
    print("EMBEDDING TEST")
    print("=" * 70)

    print(f"Model: {embeddings.model}")
    print(f"Dimensions: {len(vector)}")
    print(f"First 10 values: {vector[:10]}")


if __name__ == "__main__":
    main()
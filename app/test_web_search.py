from web.tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

def main():
    client = TavilyClient()

    results = client.search_web(
        query="latest public examination schedule",
    )

    print("\n" + "=" * 70)
    print(f"RESULTS: {len(results)}")
    print("=" * 70)

    for index, result in enumerate(
        results,
        start=1,
    ):
        print(f"\n[{index}]")
        print(f"TITLE: {result.get('title')}")
        print(f"URL:   {result.get('url')}")
        print(f"TEXT:  {result.get('content')}")


if __name__ == "__main__":
    main()
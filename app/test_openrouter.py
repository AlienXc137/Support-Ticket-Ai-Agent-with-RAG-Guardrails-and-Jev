import os
import time

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def main():
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("NEMO_GUARDRAIL_MODEL")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is not set."
        )

    if not model:
        raise ValueError(
            "NEMO_GUARDRAIL_MODEL is not set."
        )

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    start = time.perf_counter()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: OPENROUTER_OK",
            }
        ],
        temperature=0,
        max_tokens=20,
    )

    elapsed = time.perf_counter() - start

    print("Response:")
    print(response.choices[0].message.content)

    print(f"\nModel requested: {model}")
    print(f"Time: {elapsed:.2f}s")

    if response.model:
        print(f"Model returned: {response.model}")

    print(f"Provider usage: {response.usage}")


if __name__ == "__main__":
    main()
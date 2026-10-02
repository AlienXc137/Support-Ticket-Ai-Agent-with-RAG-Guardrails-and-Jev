import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("AI_GATEWAY_API_KEY"),
    base_url="https://ai-gateway.vercel.sh/v1"
)

response = client.chat.completions.create(
    model="openai/gpt-6-luna",
    messages=[
        {
            "role": "user",
            "content": "Explain quantum computing in one paragraph."
        }
    ]
)

print(response.choices[0].message.content)
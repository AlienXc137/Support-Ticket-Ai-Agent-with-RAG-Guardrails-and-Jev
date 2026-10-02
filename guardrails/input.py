import os
from pathlib import Path

from dotenv import load_dotenv
from nemoguardrails import LLMRails, RailsConfig


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config"

config = RailsConfig.from_path(
    str(CONFIG_PATH)
)

rails = LLMRails(
    config,
    verbose=True,
)


def check_input(message: str) -> dict:
    result = rails.check(
        [
            {
                "role": "user",
                "content": message,
            }
        ]
    )

    return {
        "allowed": result.status.value != "blocked",
        "status": result.status,
        "message": result.content or message,
        "reason": result.rail or "",
    }
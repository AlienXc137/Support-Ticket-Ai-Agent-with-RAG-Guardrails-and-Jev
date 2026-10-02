from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
POLICY_PATH = BASE_DIR / "config" / "web_policy.yaml"

class WebPolicy:
    def __init__(self):
        with POLICY_PATH.open("r",encoding="utf-8") as file:
            self.config = yaml.safe_load(file) or {}

    def get_policy(self,source_type: str) -> dict:
        return self.config.get(
            source_type,
            {
                "enabled": False,
                "domains": [],
            },
        )
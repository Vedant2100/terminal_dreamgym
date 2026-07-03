import json
import os
from pathlib import Path


class MissingRequiredConfig(RuntimeError):
    pass


def load_settings(path: str | Path = "config.json", env: dict[str, str] | None = None) -> dict[str, object]:
    env = os.environ if env is None else env
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {
        "timeout": data["timeout"],
        "api_key": env.get("API_KEY") or data["api_key"],
        "region": data["region"],
    }

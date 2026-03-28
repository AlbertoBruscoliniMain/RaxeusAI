import json
from datetime import datetime
from pathlib import Path

SESSIONS_DIR = Path(__file__).parent / "sessions"


def save_session(history: list) -> str:
    SESSIONS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = SESSIONS_DIR / f"session_{timestamp}.json"
    messages = [m for m in history if m.get("role") != "system"]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    return str(path)


def list_sessions() -> list[str]:
    if not SESSIONS_DIR.exists():
        return []
    files = sorted(SESSIONS_DIR.glob("session_*.json"), reverse=True)
    return [f.stem.replace("session_", "") for f in files]


def load_session(timestamp: str) -> list:
    path = SESSIONS_DIR / f"session_{timestamp}.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

"""Runtime configuration, read from environment variables (or a .env file)."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv() -> None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()

DOMAINS_DIR = ROOT / "domains"
WEB_DIR = ROOT / "web"
DATA_DIR = Path(os.environ.get("VELAN_DATA_DIR", ROOT / "data"))
DB_PATH = DATA_DIR / "velan.db"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = os.environ.get("VELAN_MODEL", "claude-opus-5-5")
# "claude" uses the Claude API; "offline" uses the rule-based agent; "auto" picks.
AGENT_MODE = os.environ.get("VELAN_AGENT", "auto")

SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY", "")

ENABLED_DOMAINS = [
    d.strip() for d in os.environ.get("VELAN_DOMAINS", "farmer,citizen").split(",") if d.strip()
]

LANGUAGES = {
    "ta": {"name": "தமிழ்", "bcp47": "ta-IN"},
    "hi": {"name": "हिन्दी", "bcp47": "hi-IN"},
    "en": {"name": "English", "bcp47": "en-IN"},
}
DEFAULT_LANG = "ta"


def use_claude() -> bool:
    if AGENT_MODE == "offline":
        return False
    if AGENT_MODE == "claude":
        return True
    return bool(ANTHROPIC_API_KEY)

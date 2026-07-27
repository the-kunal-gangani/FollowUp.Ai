import json
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    _BASE_DIR = Path(sys.executable).parent
else:
    _BASE_DIR = Path(__file__).parent

SETTINGS_PATH = _BASE_DIR / "settings.json"

DEFAULTS = {
    "extraction_backend": "local",
    "ollama_host": "http://localhost:11434",
    "ollama_model": "llama3.2",
    "groq_api_key": "",
    "groq_model": "llama-3.3-70b-versatile",
    "whisper_model_size": "base",
}


def load_settings():
    if not SETTINGS_PATH.exists():
        return dict(DEFAULTS)
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULTS)
        merged.update({k: v for k, v in data.items() if k in DEFAULTS})
        return merged
    except Exception:
        return dict(DEFAULTS)


def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        return True, None
    except Exception as exc:
        return False, str(exc)
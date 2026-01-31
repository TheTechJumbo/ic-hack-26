import json
import os
from datetime import datetime

VOICES_FILE = os.path.join(os.path.dirname(__file__), "..", "voices.json")


def _load_voices() -> dict:
    """Load voices from JSON file."""
    if os.path.exists(VOICES_FILE):
        with open(VOICES_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_voices(voices: dict):
    """Save voices to JSON file."""
    with open(VOICES_FILE, "w") as f:
        json.dump(voices, f, indent=2)


def save_user_voice(telegram_id: str, voice_id: str):
    """Save a user's cloned voice ID."""
    voices = _load_voices()
    voices[str(telegram_id)] = {
        "voice_id": voice_id,
        "created_at": datetime.utcnow().isoformat(),
    }
    _save_voices(voices)


def get_user_voice(telegram_id: str) -> str | None:
    """Get a user's cloned voice ID, or None if not found."""
    voices = _load_voices()
    user_data = voices.get(str(telegram_id))
    if user_data:
        return user_data.get("voice_id")
    return None


def delete_user_voice(telegram_id: str) -> bool:
    """Delete a user's cloned voice. Returns True if deleted."""
    voices = _load_voices()
    if str(telegram_id) in voices:
        del voices[str(telegram_id)]
        _save_voices(voices)
        return True
    return False

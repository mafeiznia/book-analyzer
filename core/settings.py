"""User settings — persisted in data/settings.json."""
import json
import sys
from pathlib import Path


def _get_settings_path() -> Path:
    """Return path to settings.json (dev or frozen mode)."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "settings.json"


DEFAULTS = {
    "theme": "light",  # "light" | "dark"
    "language": "fa",
}


def load_settings() -> dict:
    """Load settings from disk, fallback to defaults."""
    path = _get_settings_path()
    if not path.exists():
        return dict(DEFAULTS)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        # Merge with defaults (for future keys)
        merged = dict(DEFAULTS)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULTS)


def save_settings(settings: dict) -> None:
    """Save settings to disk."""
    path = _get_settings_path()
    try:
        path.write_text(
            json.dumps(settings, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


def get_theme() -> str:
    return load_settings().get("theme", DEFAULTS["theme"])


def set_theme(theme: str) -> None:
    s = load_settings()
    s["theme"] = theme
    save_settings(s)
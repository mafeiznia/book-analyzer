"""Save analysis result as JSON (English version)."""
import json
from datetime import datetime
from pathlib import Path

from core.bilingual import flatten_for_lang


import sys


def _get_output_dir() -> Path:
    """Return the output directory.

    - In dev mode: <project_root>/output
    - In frozen (exe) mode: <exe_dir>/output
    """
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent
    d = base / "output"
    d.mkdir(parents=True, exist_ok=True)
    return d


OUTPUT_DIR = _get_output_dir()


def _slug(text: str, max_len: int = 40) -> str:
    """Make a safe filename slug from a title."""
    keep = []
    for ch in text.strip():
        if ch.isalnum() or ch in ("-", "_"):
            keep.append(ch)
        elif ch.isspace():
            keep.append("_")
    s = "".join(keep)[:max_len].strip("_")
    return s or "untitled"


def project_dir(project_id: int, title: str) -> Path:
    """Return the base output directory for a project."""
    d = OUTPUT_DIR / f"{project_id}_{_slug(title)}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_json(
    project_id: int,
    title: str,
    author: str,
    version: int,
    analysis: dict,
    translation_prompt: str,
    sources_used: list[str],
    provider: str,
    model: str,
    tokens_in: int = 0,
    tokens_out: int = 0,
    analyzed_at: str | None = None,
) -> Path:
    """Save a complete JSON file with English-only fields. Returns the file path."""
    base = project_dir(project_id, title) / f"v{version}"
    base.mkdir(parents=True, exist_ok=True)

    # Flatten bilingual fields to English
    analysis_en = flatten_for_lang(analysis, "en")

    payload = {
        "meta": {
            "project_id": project_id,
            "title": title,
            "author": author,
            "version": version,
            "analyzed_at": analyzed_at or datetime.now().isoformat(timespec="seconds"),
            "provider": provider,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "language": "en",
        },
        "analysis": analysis_en,
        "translation_prompt": translation_prompt,
        "sources_used": sources_used,
    }

    path = base / "analysis.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path
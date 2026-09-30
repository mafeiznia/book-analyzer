"""Helpers for working with bilingual (fa/en) analysis fields."""
from typing import Any


def pick(value: Any, lang: str = "fa") -> str:
    """Extract a single string from a bilingual field.

    Handles:
    - {"fa": "...", "en": "..."}          → returns value[lang]
    - "plain string"                       → returns as-is (legacy compatibility)
    - None                                 → returns ""
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        v = value.get(lang)
        if v:
            return str(v)
        # Fallback to the other language if requested one is missing
        fallback = "en" if lang == "fa" else "fa"
        v2 = value.get(fallback)
        return str(v2) if v2 else ""
    return str(value)


def pick_list(values: Any, lang: str = "fa") -> list[str]:
    """Extract a list of strings from a list of bilingual fields."""
    if not values:
        return []
    if not isinstance(values, list):
        return [pick(values, lang)]
    return [pick(v, lang) for v in values if v is not None]


def flatten_for_lang(data: dict, lang: str = "fa") -> dict:
    """Recursively flatten a bilingual analysis dict to single-language strings.

    Used by exporters that only need one language (e.g., MD/PDF for Persian,
    JSON for English).
    """
    if isinstance(data, dict):
        # Bilingual leaf
        if set(data.keys()) >= {"fa", "en"} and len(data) == 2:
            return pick(data, lang)
        # Recurse
        return {k: flatten_for_lang(v, lang) for k, v in data.items()}
    if isinstance(data, list):
        return [flatten_for_lang(item, lang) for item in data]
    return data
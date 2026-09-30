"""Build prompts for analysis and translation from templates."""
import json
import sys
from pathlib import Path

from core.bilingual import flatten_for_lang
from core.crawler import CrawlResult
from core.schemas import Analysis


def _get_prompts_dir() -> Path:
    """Return the prompts directory."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "core" / "prompts"
    return Path(__file__).parent / "prompts"


PROMPTS_DIR = _get_prompts_dir()

MAX_TOTAL_SOURCE_CHARS = 24_000  # ~6000 tokens
MAX_SNIPPET_CHARS = 8_000


def _load_template(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def _build_source_block(results: list[CrawlResult], max_chars: int) -> str:
    """Concatenate source texts with per-source and total caps."""
    valid = [r for r in results if r.ok and r.text.strip()]
    if not valid:
        return "(هیچ منبع متنی در دسترس نبود)"

    per_source = max(4000, max_chars // len(valid))
    parts = []
    total = 0

    for r in valid:
        chunk = r.text[:per_source]
        block = f"\n### Source: {r.url}\n{chunk}\n"
        if total + len(block) > max_chars:
            remaining = max_chars - total
            if remaining < 500:
                break
            block = block[:remaining]
        parts.append(block)
        total += len(block)

    return "\n".join(parts)


def build_analysis_prompt(
    title: str,
    author: str,
    results: list[CrawlResult],
    snippet: str = "",
) -> str:
    """Build the analysis prompt by filling the template."""
    template = _load_template("analysis.txt")

    sources_block = _build_source_block(results, MAX_TOTAL_SOURCE_CHARS)

    snippet = (snippet or "").strip()
    if snippet:
        snippet_block = snippet[:MAX_SNIPPET_CHARS]
        if len(snippet) > MAX_SNIPPET_CHARS:
            snippet_block += "\n\n[... متن نمونه خلاصه شد ...]"
    else:
        snippet_block = "(کاربر متنی وارد نکرده است)"

    schema_json = json.dumps(
        Analysis.model_json_schema(),
        ensure_ascii=False,
        indent=2,
    )

    prompt = (
        template
        .replace("<<TITLE>>", title)
        .replace("<<AUTHOR>>", author)
        .replace("<<SOURCES>>", sources_block)
        .replace("<<SNIPPET>>", snippet_block)
        .replace("<<SCHEMA>>", schema_json)
    )
    return prompt


def build_translation_prompt(
    title: str,
    author: str,
    analysis: dict,
    source_text: str,
) -> str:
    """Build the translation prompt from the analysis result.

    All fields extracted from `analysis` use the ENGLISH version
    so that the entire translation prompt is in English.
    """
    template = _load_template("translation.txt")

    # Flatten bilingual analysis to English
    analysis_en = flatten_for_lang(analysis, "en")

    # --- Flatten analysis into readable strings ---
    genre = analysis_en.get("genre", {}) or {}
    genre_parts = [genre.get("primary", "")]
    if genre.get("secondary"):
        genre_parts.append(genre["secondary"])
    if genre.get("notes"):
        genre_parts.append(genre["notes"])
    genre_str = " — ".join(p for p in genre_parts if p) or "—"

    tone = analysis_en.get("tone", {}) or {}
    tone_str = tone.get("description", "—") or "—"

    style = analysis_en.get("style", {}) or {}
    style_parts = []
    if style.get("sentence_length"):
        style_parts.append(f"Sentences: {style['sentence_length']}")
    if style.get("narrative_voice"):
        style_parts.append(f"Voice: {style['narrative_voice']}")
    if style.get("vocabulary"):
        style_parts.append(f"Vocabulary: {style['vocabulary']}")
    if style.get("notable_features"):
        features = ", ".join(style["notable_features"])
        style_parts.append(f"Features: {features}")
    style_str = " | ".join(style_parts) or "—"

    # --- Translation notes ---
    notes = analysis_en.get("translation_notes", []) or []
    if notes:
        note_lines = []
        for i, n in enumerate(notes, 1):
            topic = n.get("topic", "")
            issue = n.get("issue", "")
            suggestion = n.get("suggestion", "")
            note_lines.append(
                f"{i}. [{topic}]\n   Issue: {issue}\n   Strategy: {suggestion}"
            )
        notes_str = "\n\n".join(note_lines)
    else:
        notes_str = "(No translation notes recorded)"

    # --- Source text (cap) ---
    source = (source_text or "").strip()
    if not source:
        source = "(No text provided for translation)"
    else:
        max_source = 8000
        if len(source) > max_source:
            source = source[:max_source] + "\n\n[... source text truncated ...]"

    # --- Fill template ---
    prompt = (
        template
        .replace("<<TITLE>>", title)
        .replace("<<AUTHOR>>", author)
        .replace("<<GENRE>>", genre_str)
        .replace("<<TONE>>", tone_str)
        .replace("<<STYLE>>", style_str)
        .replace("<<NOTES>>", notes_str)
        .replace("<<SOURCE>>", source)
    )
    return prompt
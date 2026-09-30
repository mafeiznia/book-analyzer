"""Generate Markdown report with YAML front matter (Persian version)."""
from datetime import datetime
from pathlib import Path

from core.bilingual import flatten_for_lang, pick, pick_list
from exporters.to_json import project_dir


def _yaml_escape(s: str) -> str:
    """Escape a string for YAML (basic)."""
    if s is None:
        return '""'
    s = str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    return f'"{s}"'


def _md_escape(s: str) -> str:
    """Escape special Markdown characters in inline text."""
    if s is None:
        return ""
    return str(s).replace("|", "\\|")


def build_markdown(
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
) -> str:
    """Build the complete Markdown report as a string (Persian)."""
    ts = analyzed_at or datetime.now().isoformat(timespec="seconds")

    LANG = "fa"

    # Flatten bilingual analysis to Persian for convenience
    analysis_fa = flatten_for_lang(analysis, LANG)

    genre = analysis_fa.get("genre", {}) or {}
    tone = analysis_fa.get("tone", {}) or {}
    style = analysis_fa.get("style", {}) or {}
    notes = analysis_fa.get("translation_notes", []) or []
    confidence = analysis_fa.get("confidence", "Unknown")

    # --- YAML front matter ---
    yaml_lines = [
        "---",
        f"title: {_yaml_escape(title)}",
        f"author: {_yaml_escape(author)}",
        f"project_id: {project_id}",
        f"version: {version}",
        f"analyzed_at: {_yaml_escape(ts)}",
        f"provider: {_yaml_escape(provider)}",
        f"model: {_yaml_escape(model)}",
        f"tokens_in: {tokens_in}",
        f"tokens_out: {tokens_out}",
        f"genre: {_yaml_escape(genre.get('primary', ''))}",
        f"confidence: {confidence}",
        "---",
    ]

    # --- Body ---
    body = []

    # TOC (accordion with <details>)
    toc_lines = [
        "<details>",
        "<summary>📑 فهرست مطالب</summary>",
        "",
        "- [ژانر](#ژانر)",
        "- [لحن](#لحن)",
        "- [سبک نویسنده](#سبک-نویسنده)",
        "- [نکات ترجمه](#نکات-ترجمه)",
        "- [پرامپت ترجمه](#پرامپت-ترجمه)",
        "- [منابع استفاده‌شده](#منابع-استفاده‌شده)",
        "",
        "</details>",
    ]
    body.append("\n".join(toc_lines))
    body.append("")

    # Title
    body.append(f"# تحلیل کتاب: {title}")
    body.append("")
    body.append(f"**نویسنده:** {author}  ")
    body.append(f"**تاریخ تحلیل:** {ts}  ")
    body.append(f"**نسخه:** {version}  ")
    body.append(f"**Provider:** {provider} / {model}  ")
    body.append(f"**سطح اطمینان:** {confidence}")
    body.append("")

    # Genre
    body.append("## ژانر")
    body.append("")
    if genre.get("primary"):
        line = f"**ژانر اصلی:** {_md_escape(genre['primary'])}"
        if genre.get("secondary"):
            line += f"  \n**زیرژانر:** {_md_escape(genre['secondary'])}"
        body.append(line)
        body.append("")
    if genre.get("notes"):
        body.append(_md_escape(genre["notes"]))
        body.append("")

    # Tone
    body.append("## لحن")
    body.append("")
    if tone.get("description"):
        body.append(_md_escape(tone["description"]))
        body.append("")
    examples = tone.get("examples", []) or []
    if examples:
        body.append("**نمونه‌ها:**")
        body.append("")
        for ex in examples:
            body.append(f"> {ex}")
            body.append("")

    # Style
    body.append("## سبک نویسنده")
    body.append("")
    if style.get("sentence_length"):
        body.append(f"- **طول جمله‌ها:** {_md_escape(style['sentence_length'])}")
    if style.get("narrative_voice"):
        body.append(f"- **راوی:** {_md_escape(style['narrative_voice'])}")
    if style.get("vocabulary"):
        body.append(f"- **واژگان:** {_md_escape(style['vocabulary'])}")
    features = style.get("notable_features", []) or []
    if features:
        body.append("- **ویژگی‌های قابل توجه:**")
        for f in features:
            body.append(f"  - {_md_escape(f)}")
    body.append("")

    # Translation Notes
    body.append("## نکات ترجمه")
    body.append("")
    if notes:
        body.append("| # | موضوع | چالش | راهبرد پیشنهادی |")
        body.append("|---|---|---|---|")
        for i, n in enumerate(notes, 1):
            topic = _md_escape(n.get("topic", ""))
            issue = _md_escape(n.get("issue", ""))
            suggestion = _md_escape(n.get("suggestion", ""))
            body.append(f"| {i} | {topic} | {issue} | {suggestion} |")
    else:
        body.append("_(هیچ نکته ترجمه‌ای ثبت نشده است)_")
    body.append("")

    # Translation Prompt
    body.append("## پرامپت ترجمه")
    body.append("")
    body.append("```text")
    body.append(translation_prompt or "(خالی)")
    body.append("```")
    body.append("")

    # Sources
    body.append("## منابع استفاده‌شده")
    body.append("")
    if sources_used:
        for i, url in enumerate(sources_used, 1):
            body.append(f"{i}. {url}")
    else:
        body.append("_(منبعی ثبت نشده است)_")
    body.append("")

    # Footer
    body.append("---")
    body.append("")
    body.append(f"_تولیدشده توسط Book Analyzer — {ts}_")

    return "\n".join(yaml_lines) + "\n\n" + "\n".join(body)


def save_markdown(
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
    """Write the Markdown report to disk. Returns the file path."""
    base = project_dir(project_id, title) / f"v{version}"
    base.mkdir(parents=True, exist_ok=True)

    md = build_markdown(
        project_id=project_id,
        title=title,
        author=author,
        version=version,
        analysis=analysis,
        translation_prompt=translation_prompt,
        sources_used=sources_used,
        provider=provider,
        model=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        analyzed_at=analyzed_at,
    )

    path = base / "report.md"
    path.write_text(md, encoding="utf-8")
    return path
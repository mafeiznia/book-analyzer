"""Main analyzer: collect sources, call LLM, validate output."""
import json
import re
import time
from dataclasses import dataclass, field

from pydantic import ValidationError

from core.collector import collect_sources
from core.prompt_builder import build_analysis_prompt, build_translation_prompt
from core.schemas import Analysis


@dataclass
class AnalysisResult:
    ok: bool
    analysis: dict | None = None
    error: str = ""
    sources_used: list[str] = field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0
    provider: str = ""
    model: str = ""
    elapsed_ms: int = 0
    raw_response: str = ""
    translation_prompt: str = ""


def _strip_code_fences(text: str) -> str:
    """Remove ```json ... ``` wrapper if present."""
    text = text.strip()
    m = re.match(r"^```(?:json)?\s*\n(.*)\n```\s*$", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text


def _extract_json(text: str) -> str:
    """Extract first JSON object from text."""
    text = _strip_code_fences(text)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


async def analyze_book(
    title: str,
    author: str,
    urls: list[str],
    snippet: str,
    provider,
    model: str,
    on_log=None,
) -> AnalysisResult:
    """Full pipeline: collect → prompt → LLM → validate."""

    def log(msg: str, level: str = "simple", tech: dict | None = None):
        if on_log:
            try:
                on_log(level, msg, tech)
            except Exception:
                pass

    start = time.time()
    result = AnalysisResult(ok=False, provider=provider.name, model=model)

    # --- 1. Collect sources ---
    log("📚 مرحله ۱/۳: جمع‌آوری منابع...")
    crawl_results, urls_used = await collect_sources(
        title=title,
        author=author,
        user_urls=urls,
        min_chars=2000,
        max_search_results=3,
        on_log=on_log,
    )
    result.sources_used = urls_used

    if not crawl_results:
        result.error = "هیچ منبعی برای تحلیل در دسترس نیست."
        result.elapsed_ms = int((time.time() - start) * 1000)
        return result

    # --- 2. Build prompt ---
    log("📝 مرحله ۲/۳: ساخت پرامپت تحلیل...")
    prompt = build_analysis_prompt(title, author, crawl_results, snippet)
    log(
        f"   طول پرامپت: {len(prompt):,} کاراکتر",
        level="technical",
        tech={"prompt_chars": len(prompt)},
    )

    # --- 3. Call LLM ---
    log(f"🤖 مرحله ۳/۳: فراخوانی {provider.name}/{model}...")
    try:
        response = await provider.ask(prompt, model=model, max_tokens=3000, temperature=0.2)
    except Exception as e:
        result.error = f"خطا در فراخوانی Provider: {type(e).__name__}: {str(e)[:200]}"
        result.elapsed_ms = int((time.time() - start) * 1000)
        log(f"❌ {result.error}")
        return result

    result.tokens_in = response.tokens_in
    result.tokens_out = response.tokens_out
    result.raw_response = response.text

    log(
        f"   پاسخ دریافت شد: {len(response.text):,} کاراکتر "
        f"(ورودی: {response.tokens_in:,} توکن، خروجی: {response.tokens_out:,} توکن)",
        level="technical",
        tech={
            "tokens_in": response.tokens_in,
            "tokens_out": response.tokens_out,
            "response_chars": len(response.text),
        },
    )

    # --- 4. Parse + validate ---
    json_text = _extract_json(response.text)

    try:
        analysis = Analysis.model_validate_json(json_text)
    except (ValidationError, ValueError, json.JSONDecodeError) as e:
        result.error = f"خروجی LLM معتبر نبود: {type(e).__name__}: {str(e)[:300]}"
        result.elapsed_ms = int((time.time() - start) * 1000)
        log(f"❌ {result.error}")
        log("   پیش‌نمایش پاسخ خام:", level="technical")
        log(f"   {response.text[:500]}", level="technical")
        return result

    result.ok = True
    result.analysis = analysis.model_dump()

    # --- 5. Build translation prompt ---
    log("📝 تولید پرامپت ترجمه...")
    try:
        # Use user snippet as the source text; if empty, use a placeholder
        source_for_translation = (snippet or "").strip()
        if not source_for_translation:
            source_for_translation = "(متن برای ترجمه وارد نشده است — این پرامپت را می‌توانید بعداً با متن خودتان استفاده کنید.)"

        result.translation_prompt = build_translation_prompt(
            title=title,
            author=author,
            analysis=result.analysis,
            source_text=source_for_translation,
        )
        log(
            f"   پرامپت ترجمه ساخته شد: {len(result.translation_prompt):,} کاراکتر",
            level="technical",
            tech={"translation_prompt_chars": len(result.translation_prompt)},
        )
    except Exception as e:
        log(f"⚠️ خطا در ساخت پرامپت ترجمه: {type(e).__name__}: {str(e)[:150]}")

    result.elapsed_ms = int((time.time() - start) * 1000)
    log(f"✅ تحلیل با موفقیت انجام شد ({result.elapsed_ms}ms)")
    return result
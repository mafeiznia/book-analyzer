"""Test LLM analysis end-to-end.

Usage:
    python test_analyzer.py
"""
import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv()

from providers.manager import provider_manager
from core.analyzer import analyze_book


def on_log(level, msg, tech=None):
    prefix = "  " if level == "technical" else ""
    print(f"{prefix}[{level}] {msg}")
    if tech:
        print(f"    {tech}")


async def main():
    # Init providers
    provider_manager.load()

    provider = provider_manager.get_active()
    if provider is None:
        print("❌ هیچ Provider فعالی وجود ندارد. ابتدا در تنظیمات، یک Provider را فعال کنید.")
        return

    model = os.getenv("DEFAULT_MODEL", "").strip()
    if not model:
        print("❌ DEFAULT_MODEL در .env تنظیم نشده است.")
        return

    print(f"🔌 Provider: {provider.name}")
    print(f"🤖 Model: {model}\n")

    title = "The Great Gatsby"
    author = "F. Scott Fitzgerald"
    urls = ["https://en.wikipedia.org/wiki/The_Great_Gatsby"]
    snippet = (
        "In my younger and more vulnerable years my father gave me some advice "
        "that I've been turning over in my mind ever since.\n\n"
        "\"Whenever you feel like criticizing any one,\" he told me, "
        "\"just remember that all the people in this world haven't had the "
        "advantages that you've had.\""
    )

    print("=" * 70)
    print(f"📖 {title} — {author}")
    print("=" * 70 + "\n")

    result = await analyze_book(
        title=title,
        author=author,
        urls=urls,
        snippet=snippet,
        provider=provider,
        model=model,
        on_log=on_log,
    )

    print("\n" + "=" * 70)
    if result.ok:
        print("✅ تحلیل موفق")
        print("=" * 70)
        print(json.dumps(result.analysis, ensure_ascii=False, indent=2))
        print("\n📊 آمار:")
        print(f"   ورودی: {result.tokens_in:,} توکن")
        print(f"   خروجی: {result.tokens_out:,} توکن")
        print(f"   زمان: {result.elapsed_ms}ms")

        # --- Translation prompt ---
        if result.translation_prompt:
            print("\n" + "=" * 70)
            print("📝 پرامپت ترجمه (آماده استفاده)")
            print("=" * 70)
            print(result.translation_prompt)
    else:
        print("❌ تحلیل ناموفق")
        print("=" * 70)
        print(f"خطا: {result.error}")
        if result.raw_response:
            print("\n--- پیش‌نمایش پاسخ خام (۵۰۰ کاراکتر اول) ---")
            print(result.raw_response[:500])


if __name__ == "__main__":
    asyncio.run(main())
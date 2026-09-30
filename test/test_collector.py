"""Test full source collection flow: crawl + search fallback."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.collector import collect_sources


def _on_log(level, msg, tech):
    print(f"[{level}] {msg}")


async def main():
    title = "The Great Gatsby"
    author = "F. Scott Fitzgerald"

    # Test scenarios
    scenarios = [
        ("بدون لینک — جست‌وجو فعال می‌شود", []),
        ("با یک لینک کافی — جست‌وجو غیرفعال می‌ماند", [
            "https://en.wikipedia.org/wiki/The_Great_Gatsby",
        ]),
        ("با یک لینک نامعتبر — جست‌وجو فعال می‌شود", [
            "https://invalid-domain-xyz-12345.com",
        ]),
    ]

    for label, urls in scenarios:
        print("\n" + "=" * 70)
        print(f"🧪 سناریو: {label}")
        print(f"   لینک‌ها: {urls if urls else '[] (هیچ)'}")
        print("=" * 70)

        results, urls_used = await collect_sources(
            title=title,
            author=author,
            user_urls=urls,
            min_chars=2000,
            max_search_results=3,
            on_log=_on_log,
        )

        print(f"\n📦 {len(results)} نتیجه دریافتی، {len(urls_used)} URL استفاده‌شده")


if __name__ == "__main__":
    asyncio.run(main())
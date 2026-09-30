"""Test crawler: fetch URLs and print extracted text preview.

Usage:
    python test_crawler.py                       # uses a default Wikipedia URL
    python test_crawler.py URL1 URL2 ...         # uses given URLs
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.crawler import crawl_many


def _print_result(result):
    icon = "✅" if result.ok else "❌"
    print(f"{icon} {result.url}")
    if result.ok:
        print(f"   عنوان: {result.title[:100]}")
        print(f"   کاراکتر: {result.char_count:,}  |  زمان: {result.elapsed_ms}ms")
        preview = result.text[:400].replace("\n", " ")
        print(f"   پیش‌نمایش: {preview}")
    else:
        print(f"   خطا: {result.error}")
    print()


async def main():
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        urls = ["https://en.wikipedia.org/wiki/The_Great_Gatsby"]

    print(f"🔍 دریافت {len(urls)} لینک با timeout=20s\n")
    print("─" * 70)

    results = await crawl_many(urls, timeout=20.0, on_result=_print_result)

    print("─" * 70)
    ok = sum(1 for r in results if r.ok)
    print(f"\n📊 نتیجه: {ok}/{len(results)} موفق")


if __name__ == "__main__":
    asyncio.run(main())
"""Test DuckDuckGo search."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.search import search_web


async def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "The Great Gatsby F. Scott Fitzgerald"

    print(f"🔍 جست‌وجو: «{query}»\n")
    print("─" * 70)

    try:
        results = await search_web(query, max_results=5)
    except Exception as e:
        print(f"❌ خطا: {type(e).__name__}: {e}")
        return

    if not results:
        print("هیچ نتیجه‌ای یافت نشد.")
        return

    for i, r in enumerate(results, 1):
        print(f"{i}. {r.title}")
        print(f"   🔗 {r.url}")
        print(f"   💬 {r.snippet[:150]}")
        print()

    print("─" * 70)
    print(f"📊 {len(results)} نتیجه")


if __name__ == "__main__":
    asyncio.run(main())
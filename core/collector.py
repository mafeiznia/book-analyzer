"""Orchestrator: crawl user URLs, search if not enough."""
from core.crawler import CrawlResult, crawl_many
from core.search import search_web


async def collect_sources(
    title: str,
    author: str,
    user_urls: list[str],
    min_chars: int = 2000,
    max_search_results: int = 5,
    on_log=None,
) -> tuple[list[CrawlResult], list[str]]:
    """Collect source text from user URLs; search if insufficient.

    Returns:
        (results, urls_used)
    """

    def log(msg: str, level: str = "simple", tech: dict | None = None):
        if on_log:
            try:
                on_log(level, msg, tech)
            except Exception:
                pass

    def on_crawl(result: CrawlResult):
        if result.ok:
            log(
                f"   ✅ {_short(result.url)} — {result.char_count:,} کاراکتر ({result.elapsed_ms}ms)"
            )
        else:
            log(f"   ❌ {_short(result.url)} — {result.error}")

    # --- Step 1: Crawl user URLs ---
    user_urls = [u.strip() for u in user_urls if u and u.strip()]
    results: list[CrawlResult] = []
    urls_used: list[str] = []

    if user_urls:
        log(f"🔗 دریافت {len(user_urls)} لینک از کاربر...")
        user_results = await crawl_many(user_urls, timeout=20.0, on_result=on_crawl)
        results.extend(user_results)
        urls_used.extend(user_urls)

        total_chars = sum(r.char_count for r in user_results if r.ok)
    else:
        log("⚠️ کاربر هیچ لینکی وارد نکرده است.")
        total_chars = 0

    # --- Step 2: Search if insufficient ---
    if total_chars < min_chars:
        log(
            f"⚠️ متن استخراج‌شده کافی نیست ({total_chars:,} < {min_chars:,}). جست‌وجوی خودکار...",
        )
        query = f"{title} {author}".strip()
        log(f"🔍 جست‌وجو در DuckDuckGo: «{query}»")

        try:
            search_results = await search_web(query, max_results=max_search_results)
        except Exception as e:
            log(f"❌ خطا در جست‌وجو: {type(e).__name__}: {str(e)[:120]}")
            search_results = []

        if not search_results:
            log("❌ هیچ نتیجه‌ای از جست‌وجو بازنگشت.")
            return results, urls_used

        log(f"✅ {len(search_results)} نتیجه از جست‌وجو:")
        for r in search_results:
            log(f"   • {_short(r.url)}")

        # Filter out already-crawled URLs
        seen = set(urls_used)
        new_urls = [r.url for r in search_results if r.url not in seen]

        # Limit to avoid overloading
        new_urls = new_urls[:max_search_results]

        if new_urls:
            log(f"🔗 دریافت {len(new_urls)} نتیجه جدید...")
            search_crawl = await crawl_many(new_urls, timeout=20.0, on_result=on_crawl)
            results.extend(search_crawl)
            urls_used.extend(new_urls)
        else:
            log("ℹ️ همه نتایج تکراری بودند.")

    # --- Final ---
    total_ok = sum(1 for r in results if r.ok)
    total_final_chars = sum(r.char_count for r in results if r.ok)
    log(
        f"📊 جمع‌بندی: {total_ok}/{len(results)} منبع موفق، "
        f"{total_final_chars:,} کاراکتر متن"
    )

    return results, urls_used


def _short(url: str, max_len: int = 70) -> str:
    return url if len(url) <= max_len else url[: max_len - 1] + "…"
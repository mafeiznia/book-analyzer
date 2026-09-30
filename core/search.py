"""DuckDuckGo web search via ddgs."""
import asyncio
from dataclasses import dataclass

from ddgs import DDGS


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


def _sync_search(query: str, max_results: int) -> list[SearchResult]:
    """Blocking search (runs in a thread)."""
    results: list[SearchResult] = []
    with DDGS(timeout=15) as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            url = r.get("href") or r.get("url") or ""
            if not url:
                continue
            results.append(
                SearchResult(
                    title=r.get("title", ""),
                    url=url,
                    snippet=r.get("body", ""),
                )
            )
    return results


async def search_web(query: str, max_results: int = 5) -> list[SearchResult]:
    """Async wrapper around DuckDuckGo search."""
    return await asyncio.to_thread(_sync_search, query, max_results)
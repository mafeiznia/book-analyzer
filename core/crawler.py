"""Web crawler: fetch URLs, extract meaningful text."""
import time
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Tags to remove before text extraction
STRIP_TAGS = [
    "script", "style", "noscript",
    "nav", "footer", "header", "aside",
    "form", "iframe", "svg",
]


@dataclass
class CrawlResult:
    url: str
    ok: bool
    title: str = ""
    text: str = ""
    char_count: int = 0
    elapsed_ms: int = 0
    error: str = ""


def _extract_text(html: str) -> tuple[str, str]:
    """Return (title, cleaned_text) from raw HTML."""
    soup = BeautifulSoup(html, "lxml")

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Remove useless tags
    for tag in STRIP_TAGS:
        for el in soup.find_all(tag):
            el.decompose()

    # Prefer main content containers
    main = soup.find("main") or soup.find("article") or soup.body or soup
    raw_text = main.get_text(separator="\n", strip=True)

    # Collapse empty lines
    lines = [ln.strip() for ln in raw_text.splitlines()]
    lines = [ln for ln in lines if ln]
    text = "\n".join(lines)

    return title, text


async def fetch_url(url: str, timeout: float = 20.0) -> CrawlResult:
    """Fetch a single URL and extract text."""
    start = time.time()

    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()

            content_type = resp.headers.get("content-type", "").lower()
            if "html" not in content_type and "text" not in content_type:
                return CrawlResult(
                    url=url,
                    ok=False,
                    elapsed_ms=int((time.time() - start) * 1000),
                    error=f"نوع محتوا پشتیبانی نمی‌شود: {content_type[:60]}",
                )

            title, text = _extract_text(resp.text)
            return CrawlResult(
                url=url,
                ok=True,
                title=title,
                text=text,
                char_count=len(text),
                elapsed_ms=int((time.time() - start) * 1000),
            )

    except httpx.TimeoutException:
        return CrawlResult(
            url=url,
            ok=False,
            elapsed_ms=int((time.time() - start) * 1000),
            error=f"Timeout ({timeout:.0f}s)",
        )
    except httpx.HTTPStatusError as e:
        return CrawlResult(
            url=url,
            ok=False,
            elapsed_ms=int((time.time() - start) * 1000),
            error=f"HTTP {e.response.status_code}",
        )
    except httpx.RequestError as e:
        return CrawlResult(
            url=url,
            ok=False,
            elapsed_ms=int((time.time() - start) * 1000),
            error=f"خطای شبکه: {type(e).__name__}",
        )
    except Exception as e:
        return CrawlResult(
            url=url,
            ok=False,
            elapsed_ms=int((time.time() - start) * 1000),
            error=f"{type(e).__name__}: {str(e)[:100]}",
        )


async def crawl_many(urls: list[str], timeout: float = 20.0, on_result=None) -> list[CrawlResult]:
    """Crawl multiple URLs sequentially. Calls on_result(result) after each."""
    results: list[CrawlResult] = []
    for url in urls:
        result = await fetch_url(url, timeout=timeout)
        results.append(result)
        if on_result:
            try:
                on_result(result)
            except Exception:
                pass
    return results
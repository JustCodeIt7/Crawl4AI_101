import asyncio
import sys
import time
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

URL = "https://docs.crawl4ai.com/"


async def timed_crawl(crawler: AsyncWebCrawler, label: str, mode: CacheMode) -> None:
    started = time.perf_counter()
    result = await crawler.arun(url=URL, config=CrawlerRunConfig(cache_mode=mode, verbose=False))
    elapsed = time.perf_counter() - started
    print(label, "success=", result.success, "seconds=", f"{elapsed:.2f}")


async def main() -> None:
    async with AsyncWebCrawler() as crawler:
        await timed_crawl(crawler, "enabled-first", CacheMode.ENABLED)
        await timed_crawl(crawler, "read-only", CacheMode.READ_ONLY)
        await timed_crawl(crawler, "bypass", CacheMode.BYPASS)


if __name__ == "__main__":
    asyncio.run(main())

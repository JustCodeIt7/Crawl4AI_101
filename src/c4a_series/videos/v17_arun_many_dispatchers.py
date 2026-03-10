import asyncio
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerMonitor,
    CrawlerRunConfig,
    MemoryAdaptiveDispatcher,
    RateLimiter,
)

URLS = [
    "https://docs.crawl4ai.com/",
    "https://docs.crawl4ai.com/core/quickstart/",
    "https://docs.crawl4ai.com/core/browser-crawler-config/",
    "https://docs.crawl4ai.com/core/markdown-generation/",
]


def build_dispatcher(total: int) -> MemoryAdaptiveDispatcher:
    return MemoryAdaptiveDispatcher(
        memory_threshold_percent=80.0,
        check_interval=1.0,
        max_session_permit=4,
        rate_limiter=RateLimiter(base_delay=(0.5, 1.0), max_delay=5.0, max_retries=2),
        monitor=CrawlerMonitor(urls_total=total, enable_ui=False),
    )


async def main() -> None:
    browser_config = BrowserConfig(headless=True, verbose=False)
    batch_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False, verbose=False)
    stream_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=True, verbose=False)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        batch_results = await crawler.arun_many(URLS, config=batch_config, dispatcher=build_dispatcher(len(URLS)))
        print("batch_ok:", sum(1 for result in batch_results if result.success), "of", len(batch_results))

        stream_iter = await crawler.arun_many(URLS[:2], config=stream_config, dispatcher=build_dispatcher(2))
        async for result in stream_iter:
            print("stream:", result.success, result.url)


if __name__ == "__main__":
    asyncio.run(main())

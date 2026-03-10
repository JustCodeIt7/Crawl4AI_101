import asyncio
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig

URL = "https://docs.crawl4ai.com/"


async def run_once(crawler: AsyncWebCrawler, label: str, config: CrawlerRunConfig) -> None:
    result = await crawler.arun(url=URL, config=config)
    print(label, "success=", result.success, "html_chars=", len(result.html or ""))


async def main() -> None:
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        viewport_width=1280,
        viewport_height=720,
        verbose=False,
    )

    fast_run = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False)
    debug_run = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_until="networkidle",
        exclude_external_links=True,
        verbose=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        await run_once(crawler, "fast", fast_run)
        await run_once(crawler, "debug", debug_run)


if __name__ == "__main__":
    asyncio.run(main())

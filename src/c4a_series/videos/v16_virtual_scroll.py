import asyncio
import re
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig, VirtualScrollConfig

URL = "https://docs.crawl4ai.com/"


def count_links(html: str) -> int:
    return len(re.findall(r"<a\\b", html or "", flags=re.IGNORECASE))


async def main() -> None:
    base_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False)
    scroll_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        virtual_scroll_config=VirtualScrollConfig(
            container_selector="body",
            scroll_count=3,
            scroll_by="page_height",
            wait_after_scroll=0.4,
        ),
        verbose=False,
    )

    async with AsyncWebCrawler(config=BrowserConfig(headless=True, verbose=False)) as crawler:
        base = await crawler.arun(url=URL, config=base_config)
        scrolled = await crawler.arun(url=URL, config=scroll_config)

    print("base_links:", count_links(base.html or ""))
    print("virtual_scroll_links:", count_links(scrolled.html or ""))


if __name__ == "__main__":
    asyncio.run(main())

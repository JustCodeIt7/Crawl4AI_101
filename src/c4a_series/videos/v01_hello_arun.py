import asyncio
import sys
from pathlib import Path
from rich import print

############################# Path Configuration #############################

# Allow running this file directly by adding the project root to sys.path
if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

from c4a_series.common.io import preview, raw_markdown

URL = "https://docs.crawl4ai.com/"

################################# Web Crawl ##################################


async def main() -> None:
    """Crawl a single URL and print a preview of the extracted markdown."""
    # Skip cached results to always fetch fresh content
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False)

    # Open an async crawler session and fetch the target page
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    # Handle crawl failure gracefully
    if not result.success:
        print("crawl failed:", result.error_message)
        return

    print("url:", result.url)
    # print("markdown:", preview(raw_markdown(result.markdown), 300))  # Show first 300 chars
    print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())

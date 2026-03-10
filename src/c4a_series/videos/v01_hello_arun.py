import asyncio
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

from c4a_series.common.io import preview, raw_markdown

URL = "https://docs.crawl4ai.com/"


async def main() -> None:
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    if not result.success:
        print("crawl failed:", result.error_message)
        return

    print("url:", result.url)
    print("markdown:", preview(raw_markdown(result.markdown), 300))


if __name__ == "__main__":
    asyncio.run(main())

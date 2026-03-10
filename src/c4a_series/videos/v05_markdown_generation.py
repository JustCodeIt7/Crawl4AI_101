import asyncio
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from c4a_series.common.io import preview, raw_markdown

URL = "https://docs.crawl4ai.com/"


async def crawl_with_source(source: str) -> None:
    generator = DefaultMarkdownGenerator(
        content_source=source,
        options={"ignore_links": True, "body_width": 78},
    )
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, markdown_generator=generator, verbose=False)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    if not result.success:
        print(source, "failed:", result.error_message)
        return

    markdown = raw_markdown(result.markdown)
    print(source, "chars=", len(markdown), "preview=", preview(markdown, 140))


async def main() -> None:
    for source in ("raw_html", "cleaned_html", "fit_html"):
        await crawl_with_source(source)


if __name__ == "__main__":
    asyncio.run(main())

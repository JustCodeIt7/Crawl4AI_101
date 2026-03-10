import asyncio
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig, RegexExtractionStrategy

URL = "https://docs.python.org/3/"


async def main() -> None:
    built_in = RegexExtractionStrategy(
        pattern=RegexExtractionStrategy.Url | RegexExtractionStrategy.Email,
        input_format="html",
    )
    custom = RegexExtractionStrategy(
        custom={"python_version": r"Python\s+3\.\d+(?:\.\d+)?"},
        input_format="html",
    )

    async with AsyncWebCrawler() as crawler:
        built_in_result = await crawler.arun(
            url=URL,
            config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, extraction_strategy=built_in, verbose=False),
        )
        custom_result = await crawler.arun(
            url=URL,
            config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, extraction_strategy=custom, verbose=False),
        )

    if built_in_result.success:
        matches = json.loads(built_in_result.extracted_content or "[]")
        print("built-in matches:", len(matches), "sample:", matches[:3])
    if custom_result.success:
        matches = json.loads(custom_result.extracted_content or "[]")
        print("custom matches:", len(matches), "sample:", matches[:3])


if __name__ == "__main__":
    asyncio.run(main())

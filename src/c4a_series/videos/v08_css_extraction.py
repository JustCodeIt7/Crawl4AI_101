import asyncio
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig, JsonCssExtractionStrategy

URL = "https://docs.crawl4ai.com/"
SCHEMA = {
    "name": "Docs navigation links",
    "baseSelector": "nav a",
    "fields": [
        {"name": "text", "type": "text", "transform": "strip"},
        {"name": "href", "selector": "a", "type": "attribute", "attribute": "href", "default": ""},
    ],
}


async def main() -> None:
    strategy = JsonCssExtractionStrategy(SCHEMA, verbose=False)
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, extraction_strategy=strategy, verbose=False)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    if not result.success:
        print("extraction failed:", result.error_message)
        return

    rows = json.loads(result.extracted_content or "[]")
    print("items:", len(rows))
    print("first:", rows[0] if rows else None)


if __name__ == "__main__":
    asyncio.run(main())

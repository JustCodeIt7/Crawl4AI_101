import asyncio
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig, JsonCssExtractionStrategy

URL = "https://docs.crawl4ai.com/core/quickstart/"
SCHEMA = {
    "name": "Docs article outline",
    "baseSelector": "main",
    "baseFields": [
        {"name": "page_title", "selector": "h1", "type": "text", "transform": "strip", "default": "Untitled"},
    ],
    "fields": [
        {
            "name": "sections",
            "type": "nested_list",
            "selector": "h2, h3",
            "fields": [
                {"name": "heading", "type": "text", "transform": "strip", "default": ""},
                {"name": "anchor", "selector": "a", "type": "attribute", "attribute": "href", "default": ""},
            ],
        },
        {
            "name": "code_blocks",
            "type": "list",
            "selector": "pre",
            "fields": [
                {"name": "snippet", "type": "text", "transform": "strip", "default": ""},
            ],
        },
    ],
}


async def main() -> None:
    strategy = JsonCssExtractionStrategy(SCHEMA, verbose=False)
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, extraction_strategy=strategy, verbose=False)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    if not result.success:
        print("schema extraction failed:", result.error_message)
        return

    rows = json.loads(result.extracted_content or "[]")
    record = rows[0] if rows else {}
    print("title:", record.get("page_title"))
    print("section_count:", len(record.get("sections", [])))
    print("code_block_count:", len(record.get("code_blocks", [])))


if __name__ == "__main__":
    asyncio.run(main())

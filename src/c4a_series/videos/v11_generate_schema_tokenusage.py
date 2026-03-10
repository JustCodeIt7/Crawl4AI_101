import asyncio
import json
import os
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import (
    AsyncWebCrawler,
    CacheMode,
    CrawlerRunConfig,
    JsonCssExtractionStrategy,
    LLMConfig,
)

from c4a_series.common.io import SCHEMA_CACHE_DIR, load_env, write_json

URL = "https://docs.crawl4ai.com/core/quickstart/"
SCHEMA_FILE = SCHEMA_CACHE_DIR / "v11_quickstart_schema.json"


async def fetch_sample_html() -> str:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=URL,
            config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False),
        )
    if not result.success:
        raise RuntimeError(result.error_message)
    return (result.cleaned_html or result.html or "")[:12000]


async def main() -> None:
    load_env()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is required for schema generation.")
        return

    SCHEMA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if SCHEMA_FILE.exists():
        schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
        print("using cached schema:", SCHEMA_FILE)
    else:
        schema = JsonCssExtractionStrategy.generate_schema(
            html=await fetch_sample_html(),
            schema_type="CSS",
            query="Extract the article title and major quickstart sections from this page.",
            llm_config=LLMConfig(provider="openai/gpt-4o-mini", api_token=api_key),
        )
        write_json(SCHEMA_FILE, schema)
        print("generated schema:", SCHEMA_FILE)

    strategy = JsonCssExtractionStrategy(schema, verbose=False)
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, extraction_strategy=strategy, verbose=False)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    print("success:", result.success)
    print("extracted preview:", (result.extracted_content or "")[:250])


if __name__ == "__main__":
    asyncio.run(main())

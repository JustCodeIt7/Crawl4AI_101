import asyncio
import json
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig, LLMConfig, LLMExtractionStrategy

from c4a_series.common.io import load_env

URL = "https://docs.crawl4ai.com/core/quickstart/"


class PageSummary(BaseModel):
    title: str = ""
    key_steps: list[str] = Field(default_factory=list)


async def main() -> None:
    load_env()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is required for LLM extraction.")
        return

    strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(provider="openai/gpt-4o-mini", api_token=api_key),
        schema=PageSummary.model_json_schema(),
        extraction_type="schema",
        instruction="Extract the page title and 3 to 5 quickstart steps as JSON.",
        input_format="fit_markdown",
        chunk_token_threshold=1400,
        overlap_rate=0.1,
        apply_chunking=True,
        extra_args={"temperature": 0.2, "max_tokens": 700},
    )
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, extraction_strategy=strategy, verbose=False)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    if not result.success:
        print("llm extraction failed:", result.error_message)
        return

    print(json.loads(result.extracted_content or "{}"))
    strategy.show_usage()


if __name__ == "__main__":
    asyncio.run(main())

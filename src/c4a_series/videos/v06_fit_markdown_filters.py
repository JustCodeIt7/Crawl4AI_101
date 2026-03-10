import asyncio
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.content_filter_strategy import BM25ContentFilter, PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from c4a_series.common.io import fit_markdown, preview, raw_markdown

URL = "https://docs.crawl4ai.com/"


async def compare_filter(label: str, generator: DefaultMarkdownGenerator) -> None:
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, markdown_generator=generator, verbose=False)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    if not result.success:
        print(label, "failed:", result.error_message)
        return

    raw_text = raw_markdown(result.markdown)
    fit_text = fit_markdown(result.markdown)
    print(label, "raw=", len(raw_text), "fit=", len(fit_text), "preview=", preview(fit_text, 160))


async def main() -> None:
    pruning = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=0.45, threshold_type="dynamic", min_word_threshold=5)
    )
    bm25 = DefaultMarkdownGenerator(
        content_filter=BM25ContentFilter(user_query="installation quickstart browser config", bm25_threshold=1.0)
    )
    await compare_filter("pruning", pruning)
    await compare_filter("bm25", bm25)


if __name__ == "__main__":
    asyncio.run(main())

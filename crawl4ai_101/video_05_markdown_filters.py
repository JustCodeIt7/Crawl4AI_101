"""Video 05: Markdown generation and content filters.

Demonstrates:
- DefaultMarkdownGenerator
- PruningContentFilter and BM25ContentFilter
- raw_markdown vs fit_markdown
- citations and references output

Prerequisites:
- `pip install crawl4ai playwright`
- `playwright install`

Run:
- `python crawl4ai_101/video_05_markdown_filters.py`
"""

import asyncio

from crawl4ai import (
    AsyncWebCrawler,
    BM25ContentFilter,
    CacheMode,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
)

URL = "https://docs.crawl4ai.com/core/browser-crawler-config/"
QUERY = "proxy configuration user agent browser config"


def lengths(result) -> tuple[int, int]:
    markdown = result.markdown
    return len(markdown.raw_markdown or ""), len(markdown.fit_markdown or "")


async def main() -> None:
    pruning_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=0.48, threshold_type="dynamic"),
        options={"citations": True, "body_width": 100},
    )
    bm25_generator = DefaultMarkdownGenerator(
        content_filter=BM25ContentFilter(user_query=QUERY, bm25_threshold=1.1),
        options={"citations": True, "body_width": 100},
    )
    prune_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=pruning_generator,
        verbose=False,
    )
    bm25_config = prune_config.clone(markdown_generator=bm25_generator)

    async with AsyncWebCrawler() as crawler:
        pruned = await crawler.arun(URL, config=prune_config)
        bm25 = await crawler.arun(URL, config=bm25_config)

    if not pruned.success:
        print(f"Pruning crawl failed: {pruned.error_message}")
        return
    if not bm25.success:
        print(f"BM25 crawl failed: {bm25.error_message}")
        return

    prune_raw, prune_fit = lengths(pruned)
    bm25_raw, bm25_fit = lengths(bm25)
    print(f"Pruning lengths: raw={prune_raw} fit={prune_fit}")
    print(f"BM25 lengths: raw={bm25_raw} fit={bm25_fit}")
    print(
        "Citation references preview: "
        f"{(bm25.markdown.references_markdown or '').splitlines()[:3]}"
    )


if __name__ == "__main__":
    asyncio.run(main())

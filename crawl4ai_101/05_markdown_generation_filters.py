"""Video 05: Markdown generation and fit filters.

Demonstrates:
- content_source: raw_html, cleaned_html, fit_html
- PruningContentFilter and BM25ContentFilter
- raw markdown, fit markdown, and references preview

Run:
- python crawl4ai_101/05_markdown_generation_filters.py
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
from rich import print

########################## Configuration ##########################

URL = "https://docs.crawl4ai.com/core/browser-crawler-config/"
QUERY = "proxy configuration user agent browser config"  # Search query for BM25 relevance filtering


###################### Crawl & Display Helper ######################


async def show_result(
    crawler: AsyncWebCrawler,
    label: str,
    generator: DefaultMarkdownGenerator,
    fit_view: bool = False,
):
    """Crawl a page and print raw-only or raw-vs-fit markdown stats with a short preview."""
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # Always fetch fresh content
        markdown_generator=generator,
        verbose=False,
    )
    result = await crawler.arun(URL, config=config)
    if not result.success:
        print(f"{label} failed: {result.error_message}")
        return None

    markdown = result.markdown
    raw_text = markdown.raw_markdown or ""

    preview_text = raw_text
    summary = f"{label}: chars={len(raw_text)}"
    # Show fit (filtered) markdown stats when fit_view is enabled
    if fit_view:
        fit_text = markdown.fit_markdown or ""
        preview_text = fit_text
        summary = f"{label}: raw={len(raw_text)} fit={len(fit_text)}"

    preview = preview_text[:120].replace("\n", " ").strip()
    print(f"{summary} preview={preview}")
    return result


########################### Main Pipeline ###########################


async def main() -> None:
    """Run demos for content_source options and content filters."""
    async with AsyncWebCrawler() as crawler:
        # Compare markdown output from different HTML processing stages
        print("== content_source ==")
        for source in ("raw_html", "cleaned_html", "fit_html"):
            await show_result(
                crawler,
                source,
                DefaultMarkdownGenerator(
                    content_source=source,
                    options={"ignore_links": True, "body_width": 80},
                ),
            )

        # Demonstrate two filtering strategies for extracting relevant content
        print("\n== content_filters ==")
        # Remove boilerplate using statistical pruning with a dynamic threshold
        pruning = DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(
                threshold=0.45,
                threshold_type="dynamic",
                min_word_threshold=5,  # Skip blocks with fewer than 5 words
            ),
            options={"citations": True, "body_width": 80},
        )
        # Rank content blocks by BM25 relevance to the search query
        bm25 = DefaultMarkdownGenerator(
            content_filter=BM25ContentFilter(user_query=QUERY, bm25_threshold=1.0),
            options={"citations": True, "body_width": 80},
        )
        await show_result(crawler, "pruning", pruning, fit_view=True)
        bm25_result = await show_result(crawler, "bm25", bm25, fit_view=True)
        # Preview the first few reference links extracted by the BM25 filter
        if bm25_result:
            refs = (bm25_result.markdown.references_markdown or "").splitlines()[:3]
            print(f"references: {refs}")


if __name__ == "__main__":
    asyncio.run(main())

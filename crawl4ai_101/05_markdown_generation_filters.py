"""
Demonstrates Crawl4AI's Markdown generation and content filtering capabilities.

This module shows how to:
1. Control Markdown source (raw, cleaned, or fit).
2. Use `PruningContentFilter` to remove boilerplate (statistical).
3. Use `BM25ContentFilter` to extract relevant content (semantic).

Run:
    python crawl4ai_101/05_markdown_generation_filters.py
"""

import asyncio
from typing import Optional

from crawl4ai import (
    AsyncWebCrawler,
    BM25ContentFilter,
    CacheMode,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
    CrawlResult,
)
from rich import print

########################## Configuration ##########################

# The target URL we want to crawl and analyze.
URL = "https://docs.crawl4ai.com/core/browser-crawler-config/"

# Query for BM25ContentFilter to find relevant content.
QUERY = "proxy configuration user agent browser config"


###################### Crawl & Display Helper ######################


async def show_result(
    crawler: AsyncWebCrawler,
    label: str,
    generator: DefaultMarkdownGenerator,
    fit_view: bool = False,
) -> Optional[CrawlResult]:
    """Executes a crawl and prints a summary of the generated Markdown."""
    # Use BYPASS to ensure we see transformations on every run.
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=generator,
        verbose=False,
    )

    result = await crawler.arun(URL, config=config)
    if not result.success:
        print(f"[!] {label} failed: {result.error_message}")
        return None

    markdown = result.markdown
    raw_text = markdown.raw_markdown or ""

    preview_text = raw_text
    summary = f"{label}: chars={len(raw_text)}"

    # 'fit_markdown' is the filtered version (after BM25/Pruning).
    if fit_view:
        fit_text = markdown.fit_markdown or ""
        preview_text = fit_text
        summary = f"{label}: raw={len(raw_text)} fit={len(fit_text)}"

    # Clean up the preview for the console: remove newlines and truncate.
    preview = preview_text[:120].replace("\n", " ").strip()
    print(f"[+] {summary} preview: {preview}...")

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
                    content_source=source,  # Select which HTML version feeds the markdown generator
                    options={"ignore_links": True, "body_width": 80},  # Keep the console output tidy by ignoring links and wrapping lines
                ),
            )

        # Demonstrate two filtering strategies for extracting relevant content
        print("\n== content_filters ==")

        # STRATEGY 1: Pruning (Statistical Filtering) - removes low-density/short blocks.
        pruning = DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(
                threshold=0.45,
                threshold_type="dynamic",
                min_word_threshold=5,
            ),
            options={"citations": True, "body_width": 80},
        )

        # STRATEGY 2: BM25 (Semantic Filtering) - ranks blocks by relevance to QUERY.
        bm25 = DefaultMarkdownGenerator(
            content_filter=BM25ContentFilter(user_query=QUERY, bm25_threshold=1.0),  # Adjust threshold to be more or less aggressive; 1.0 is a common default
            options={"citations": True, "body_width": 80},  # Enable citation references in the output for BM25 so we can see what sources it kept
        )
        await show_result(crawler, "pruning", pruning, fit_view=True)
        bm25_result = await show_result(crawler, "bm25", bm25, fit_view=True)
        # Preview the first few reference links extracted by the BM25 filter
        if bm25_result:
            refs = (bm25_result.markdown.references_markdown or "").splitlines()[:3]
            print(f"references: {refs}")


if __name__ == "__main__":
    asyncio.run(main())

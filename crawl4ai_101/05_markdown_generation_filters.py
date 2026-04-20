"""
Module: Markdown Generation and Content Filtering Demonstration

PURPOSE IN THE SYSTEM:
In a large-scale web crawling system, raw HTML is often cluttered with 'noise'
(headers, footers, sidebars, ads). If you pass all this noise to an LLM,
you waste tokens and introduce irrelevant context. This module demonstrates
the tools provided by Crawl4AI to:
1. Control the source of Markdown generation (raw vs. cleaned vs. fit).
2. Apply statistical filters (Pruning) to remove boilerplate.
3. Apply semantic filters (BM25) to extract content relevant to a specific query.

WHEN TO USE THESE FILTERS:
- Use `PruningContentFilter` when you want to reduce token usage by removing
  low-information blocks (e.g., short menu items or footer links).
- Use `BM25ContentFilter` when you have a specific topic in
  in mind and want the crawler to 'find' the relevant parts of the page for you.

DEMONSTRATES:
- `content_source`: Switching between `raw_html`, `cleaned_html`, and `fit_html`.
- `PruningContentFilter`: Statistical removal of boilerplate.
- `BM25ContentFilter`: Semantic relevance ranking using the BM25 algorithm.
- Comparison of raw markdown vs. 'fit' markdown.

Run:
- python crawl4ai_101/05_markdown_generation_filters.py
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

# This query is used by the BM25ContentFilter to find the most relevant
# parts of the page. Think of it like a mini-search engine within the page.
QUERY = "proxy configuration user agent browser config"


###################### Crawl & Display Helper ######################


async def show_result(
    crawler: AsyncWebCrawler,
    label: str,
    generator: DefaultMarkdownGenerator,
    fit_view: bool = False,
) -> Optional[CrawlResult]:
    """
    Executes a crawl operation and prints a summary of the generated Markdown.

    This helper function abstracts the boilerplate of running a crawler and
    formatting the output for the console. It allows us to compare different
    generation strategies side-by-side.

    Args:
        crawler: The active AsyncWebCrawler instance.
        label: A descriptive name for the current test case (e.g., 'pruning').
        generator: The MarkdownGenerator configuration to use for this run.
        fit_view: If True, it will attempt to display the 'fit_markdown'
                  (the version after filters have been applied) instead of
                  just the 'raw_markdown'.

    Returns:
        The CrawlResult object if successful, otherwise None.

    """
    # We use BYPASS cache mode here because we want to
    # see the actual transformation process on every
    # run without stale data interference.
    # If we used CACHE_MODE.ENABLED, we might see the same result even if
    # we changed the filters, which would make debugging/learning harder!
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=generator,  # Attach our custom generator with the desired content source and filters
        verbose=False,
    )

    result = await crawler.arun(URL, config=config)
    # Check if the crawl was successful before trying to access the markdown.
    if not result.success:
        print(f"[!] {label} failed: {result.error_message}")
        return None

    markdown = result.markdown
    # 'raw_markdown' is the direct conversion from the source HTML.
    # It contains everything: headers, footers, ads, and the actual content.
    raw_text = markdown.raw_markdown or ""

    # Default to showing raw text unless the user specifically wants to see the 'fit' version.
    preview_text = raw_text
    summary = f"{label}: chars={len(raw_text)}"

    # 'fit_markdown' is the magic part! It's the markdown that remains AFTER
    # the content filters (like BM25 or Pruning) have done their work.
    # This is what you'd typically send to an LLM to save tokens.
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

        # STRATEGY 1: Pruning (Statistical Filtering)
        # This removes "noise" based on patterns. For example, if a block of text
        # is very short or doesn't meet a certain density, it's likely boilerplate.
        pruning = DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(
                threshold=0.45,
                threshold_type="dynamic",
                min_word_threshold=5,  # Skip blocks with fewer than 5 words
            ),
            options={"citations": True, "body_width": 80},
        )

        # STRATEGY 2: BM25 (Semantic/Keyword Filtering)
        # This uses the BM25 algorithm (used in search engines) to rank blocks
        # based on how well they match our QUERY. It's great for "finding the needle in the haystack".
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

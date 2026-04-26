"""Video 05.2: Markdown generation and content filters.

Demonstrates:
- DefaultMarkdownGenerator
- PruningContentFilter and BM25ContentFilter
- raw_markdown vs fit_markdown
- citations and references output

Prerequisites:
- `pip install crawl4ai playwright`
- `playwright install`
"""

############################# Imports & Constants ##############################
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

URL = "https://docs.streamlit.io/get-started"
QUERY = "How to get started with Streamlit?"  # Used for BM25 relevance filtering, not needed for pruning


############################### Helper Functions ###############################
def lengths(result) -> tuple[int, int]:
    """Return character counts for raw and filtered markdown."""
    markdown = result.markdown
    return len(markdown.raw_markdown or ""), len(markdown.fit_markdown or "")


########################### Main Crawl & Comparison ############################
async def main() -> None:
    """Configure two markdown generators, crawl the same URL, and compare output sizes."""

    # Set up a pruning filter that removes low-density content blocks
    pruning_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(
            threshold=0.48,  # How aggressive to prune — lower means more blocks removed
            threshold_type="dynamic",  # Threshold is adjusted based on page's content distribution
        ),
        options={
            "citations": True,  # Enable citation links in output
            "body_width": 80,  # Set width to 100 characters better readability in the console
        },
    )

    # Set up a BM25 filter that keeps only content relevant to the search query
    bm25_generator = DefaultMarkdownGenerator(
        content_filter=BM25ContentFilter(
            user_query=QUERY,  # The BM25 filter needs a query to determine relevance, unlike pruning which is query-agnostic
            bm25_threshold=1,  # A higher threshold means stricter relevance filtering, so only blocks with a strong match to the query will be kept.
            language="english",
        ),
        options={"citations": False, "body_width": 80},
    )

    # Build a crawl config for the pruning strategy
    prune_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # Force a fresh fetch, skip cache
        markdown_generator=pruning_generator,
        verbose=False,
    )

    # Clone the config and swap in the BM25 generator to keep all other settings identical
    bm25_config = prune_config.clone(markdown_generator=bm25_generator)

    # Crawl the same URL with both filter strategies
    async with AsyncWebCrawler() as crawler:
        pruned = await crawler.arun(URL, config=prune_config)
        bm25 = await crawler.arun(URL, config=bm25_config)

    ############################ Display Results ################################
    # Compare raw vs fit_markdown lengths to see how much each filter removed
    prune_raw, prune_fit = lengths(pruned)
    bm25_raw, bm25_fit = lengths(bm25)
    print(pruned.metadata)
    print(f"\nPruning lengths: raw={prune_raw} fit={prune_fit}")
    print(f"\n Preview:\n{(pruned.markdown.fit_markdown or '')[:500]}")
    print(f"\nBM25 lengths: raw={bm25_raw} fit={bm25_fit}")
    print(f"\n Preview:\n{(bm25.markdown.fit_markdown or '')[:500]}")

    # Preview the first few citation reference lines from the BM25 result
    print(f"Citation references preview: {(bm25.markdown.references_markdown or '').splitlines()[:3]}")


if __name__ == "__main__":
    asyncio.run(main())

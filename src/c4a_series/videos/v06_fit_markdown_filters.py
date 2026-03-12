import asyncio
import sys
from pathlib import Path

############################# Path Configuration #############################

# When running this script directly (e.g., `python v06_fit_markdown_filters.py`),
# __package__ will be None or empty. In that case, add the project root (two
# levels up) to sys.path so that sibling package imports resolve correctly.
if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.content_filter_strategy import BM25ContentFilter, PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from c4a_series.common.io import fit_markdown, preview, raw_markdown

# Define the target URL to crawl — the official Crawl4AI documentation site
URL = "https://docs.crawl4ai.com/"

########################## Filter Comparison Helper ##########################


async def compare_filter(label: str, generator: DefaultMarkdownGenerator) -> None:
    """Crawl the target URL using the given markdown generator and print a size comparison.

    Runs a single crawl with the supplied generator (which wraps a content
    filter), then reports three values side-by-side:
      - raw:  character count of the unfiltered markdown
      - fit:  character count of the filtered (fit) markdown
      - preview: the first 160 characters of the fit output

    This makes it easy to see at a glance how aggressively each filter
    trims the page content.

    Args:
        label:     A short identifier printed before each result line (e.g. "pruning" or "bm25").
        generator: A DefaultMarkdownGenerator configured with a specific content filter.
    """
    # Attach the generator to the run config so Crawl4AI uses the chosen
    # filter strategy when converting the crawled HTML to markdown
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, markdown_generator=generator, verbose=False)

    # Launch an async crawler session — the context manager handles headless
    # browser startup and teardown automatically
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    # Guard against network errors or other crawl failures before touching
    # the result payload
    if not result.success:
        print(label, "failed:", result.error_message)
        return

    # raw_markdown() returns the full, unfiltered markdown produced from the
    # crawled page — everything Crawl4AI extracted before any content filter ran
    raw_text = raw_markdown(result.markdown)

    # fit_markdown() returns the filtered markdown — only the blocks that
    # survived the content filter attached to the generator.  Comparing its
    # length to raw_text shows how much the filter removed.
    fit_text = fit_markdown(result.markdown)

    # Print a one-line summary: label, raw size, fit size, and a short preview
    # of the fit output so we can visually verify what was kept
    print(label, "raw=", len(raw_text), "fit=", len(fit_text), "preview=", preview(fit_text, 160))


################################# Main Routine ###############################


async def main() -> None:
    """Build two content-filter generators and compare their output on the same page.

    Two filtering strategies are demonstrated:

    PruningContentFilter — statistical, query-free pruning
        Scores every content block by how information-dense it is relative to
        the rest of the page, then drops blocks below a threshold.
        - threshold=0.45: blocks scoring below 45 % of the dynamic baseline
          are removed; higher values prune more aggressively.
        - threshold_type="dynamic": the baseline is computed per-page rather
          than being a fixed absolute value, so it adapts to each document.
        - min_word_threshold=5: blocks with fewer than 5 words are always
          discarded regardless of their score (removes stubs and labels).

    BM25ContentFilter — query-driven relevance filtering
        Uses the classic BM25 ranking algorithm to score each block against a
        user-supplied query string, keeping only the most relevant sections.
        - user_query: the search terms that drive relevance scoring; blocks
          containing these terms (weighted by frequency and document rarity)
          receive higher scores.
        - bm25_threshold=1.0: blocks with a BM25 score below 1.0 are dropped;
          raise this value to keep only very tightly matching content, lower it
          to be more permissive.
    """
    # Configure a pruning-based generator — no query required; the filter
    # decides relevance purely from the page's own statistical distribution
    pruning = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=0.45, threshold_type="dynamic", min_word_threshold=5)
    )

    # Configure a BM25-based generator — the query string steers which blocks
    # are considered relevant to the topic we care about
    bm25 = DefaultMarkdownGenerator(
        content_filter=BM25ContentFilter(user_query="installation quickstart browser config", bm25_threshold=1.0)
    )

    # Run both filters against the same URL so the size and content differences
    # are directly comparable in the printed output
    await compare_filter("pruning", pruning)
    await compare_filter("bm25", bm25)


################################# Entry Point ################################

# Standard Python entry-point guard — use asyncio.run() to execute the
# async main() coroutine from a synchronous context
if __name__ == "__main__":
    asyncio.run(main())

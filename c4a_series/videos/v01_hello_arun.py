import asyncio
import sys
from pathlib import Path

############################# Path Configuration #############################

# When running this script directly (e.g., `python crawl_basic.py`), __package__
# will be None or empty. In that case, add the project root (two levels up) to
# sys.path so that sibling package imports resolve correctly.
if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

from c4a_series.common.io import preview, raw_markdown

# Define the target URL to crawl — the official Crawl4AI documentation site
URL = "https://docs.crawl4ai.com/"

############################ Main Crawl Routine ##############################


async def main() -> None:
    """Crawl a single URL using Crawl4AI and print a truncated markdown preview.

    This demonstrates the minimal setup needed to fetch a page with
    AsyncWebCrawler: create a run config, open a crawler context, and
    inspect the result object.
    """
    # Build the crawler run configuration:
    # - BYPASS cache so we always hit the live page instead of returning stale data
    # - Disable verbose logging to keep the console output clean
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False)

    # Launch an async crawler session using a context manager, which handles
    # browser startup and teardown (Crawl4AI uses a headless browser under the hood)
    async with AsyncWebCrawler() as crawler:
        # Perform the actual crawl — arun() fetches the page, renders any
        # JavaScript, and converts the visible content into markdown
        result = await crawler.arun(url=URL, config=config)

    # Guard against crawl failures (e.g., network errors, timeouts) before
    # attempting to access the result payload
    if not result.success:
        print("crawl failed:", result.error_message)
        return

    # Display the final resolved URL (may differ from the input if redirects occurred)
    print("url:", result.url)

    # Extract the raw markdown from the result and show only the first 300
    # characters so the output stays readable in a terminal
    print("markdown:", preview(raw_markdown(result.markdown), 300))  # Truncate to 300 chars


################################# Entry Point ################################

# Standard Python entry-point guard — use asyncio.run() to execute the
# async main() coroutine from a synchronous context
if __name__ == "__main__":
    asyncio.run(main())

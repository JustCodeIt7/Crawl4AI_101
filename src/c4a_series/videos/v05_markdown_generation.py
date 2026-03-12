import asyncio
import sys
from pathlib import Path

############################# Path Configuration #############################

# When running this script directly (e.g., `python v05_markdown_generation.py`),
# __package__ will be None or empty. In that case, add the project root (two
# levels up) to sys.path so that sibling package imports resolve correctly.
if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

# DefaultMarkdownGenerator controls how Crawl4AI converts the crawled page into
# markdown. The key parameter is `content_source`, which selects which version
# of the page HTML is fed into the markdown pipeline.
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from c4a_series.common.io import preview, raw_markdown

# Define the target URL to crawl — the official Crawl4AI documentation site
URL = "https://docs.crawl4ai.com/"

########################## Per-Source Crawl Routine ##########################


async def crawl_with_source(source: str) -> None:
    """Crawl the target URL using a specific HTML content source and print a preview.

    Crawl4AI can derive markdown from three different representations of the
    page HTML. This function runs a full crawl for the given source, then
    prints the character count and a short preview of the resulting markdown
    so you can compare the outputs side-by-side.

    Args:
        source: One of "raw_html", "cleaned_html", or "fit_html" — controls
                which version of the page HTML is passed to the markdown
                generator (see inline comments below for details).
    """
    # Configure the markdown generator:
    #
    # content_source selects the HTML input fed into the markdown pipeline:
    #   "raw_html"     — the full, unmodified HTML returned by the browser,
    #                    including navigation, footers, ads, and script tags
    #   "cleaned_html" — Crawl4AI's pre-processed HTML with common boilerplate
    #                    (scripts, styles, hidden elements) stripped out
    #   "fit_html"     — the most aggressively filtered version, keeping only
    #                    the main content block most relevant to the page topic
    #
    # options tweak the markdown rendering behaviour:
    #   "ignore_links" — drop hyperlink syntax from the output so the markdown
    #                    reads as plain prose rather than being cluttered with URLs
    #   "body_width"   — wrap long lines at this column width (78 chars here) to
    #                    keep the output terminal-friendly
    generator = DefaultMarkdownGenerator(
        content_source=source,
        options={"ignore_links": True, "body_width": 78},
    )

    # Build the crawler run configuration:
    # - BYPASS cache so we always fetch the live page instead of stale data
    # - Attach our custom markdown generator to override the default pipeline
    # - Disable verbose logging to keep console output focused on our comparisons
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, markdown_generator=generator, verbose=False)

    # Launch an async crawler session using a context manager, which handles
    # browser startup and teardown (Crawl4AI uses a headless browser under the hood)
    async with AsyncWebCrawler() as crawler:
        # Perform the actual crawl — arun() fetches the page, renders any
        # JavaScript, and converts the visible content into markdown using our
        # configured generator
        result = await crawler.arun(url=URL, config=config)

    # Guard against crawl failures (e.g., network errors, timeouts) before
    # attempting to access the result payload
    if not result.success:
        print(source, "failed:", result.error_message)
        return

    # Extract the raw markdown string from the result object and display the
    # source label, total character count, and a 140-character preview so the
    # three variants can be compared at a glance
    markdown = raw_markdown(result.markdown)
    print(source, "chars=", len(markdown), "preview=", preview(markdown, 140))


############################## Main Entry Logic ##############################


async def main() -> None:
    """Run the same crawl three times, once for each supported content source.

    Iterating over all three content_source values lets you observe how the
    choice of HTML input affects the length and quality of the generated
    markdown — from verbose raw HTML all the way down to tightly filtered
    fit HTML.
    """
    # Cycle through each content source variant in order from least to most
    # filtered, printing a comparative summary line for each
    for source in ("raw_html", "cleaned_html", "fit_html"):
        await crawl_with_source(source)


################################# Entry Point ################################

# Standard Python entry-point guard — use asyncio.run() to execute the
# async main() coroutine from a synchronous context
if __name__ == "__main__":
    asyncio.run(main())

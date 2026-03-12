import asyncio
import sys
from pathlib import Path

############################# Path Configuration #############################

# When running this script directly (e.g., `python v04_crawlresult_masterclass.py`),
# __package__ will be None or empty. In that case, add the project root (two levels
# up) to sys.path so that sibling package imports resolve correctly.
if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

from c4a_series.common.io import episode_dir, fit_markdown, raw_markdown, write_text

# Define the target URL to crawl — the official Crawl4AI documentation site
URL = "https://docs.crawl4ai.com/"

############################ Main Crawl Routine ##############################


async def main() -> None:
    """Crawl a single URL and explore the key fields of the CrawlResult object.

    This demonstrates how Crawl4AI populates the result object after a crawl,
    including multiple HTML representations, markdown variants, extracted links,
    and discovered media assets. Each output is written to disk so the fields
    can be compared side-by-side.
    """
    # Resolve the per-episode output directory (e.g., outputs/v04/) so all
    # generated files are grouped together for easy inspection
    out_dir = episode_dir("v04")

    # Build the crawler run configuration:
    # - BYPASS cache so we always hit the live page instead of returning stale data
    # - Disable screenshot, PDF, and MHTML capture to keep the output focused on
    #   the text-based CrawlResult fields covered in this episode
    # - Disable verbose logging to keep the console output clean
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        screenshot=False,
        pdf=False,
        capture_mhtml=False,
        verbose=False,
    )

    # Launch an async crawler session using a context manager, which handles
    # browser startup and teardown (Crawl4AI uses a headless browser under the hood)
    async with AsyncWebCrawler() as crawler:
        # Perform the actual crawl — arun() fetches the page, renders any
        # JavaScript, and populates the CrawlResult with all extracted content
        result = await crawler.arun(url=URL, config=config)

    # Report whether the crawl succeeded and what HTTP status code was returned;
    # status_code may be absent on certain error paths so we use getattr safely
    print("success:", result.success, "status:", getattr(result, "status_code", None))

    # Guard against crawl failures (e.g., network errors, timeouts) before
    # attempting to access the result payload
    if not result.success:
        print("error:", result.error_message)
        return

    ########################### HTML Representations #########################

    # raw.html — the full, unmodified HTML exactly as the browser received it,
    # including all scripts, styles, and hidden elements
    write_text(out_dir / "raw.html", result.html or "")

    # cleaned.html — Crawl4AI's sanitised version: scripts, styles, and other
    # noise have been stripped, leaving only the meaningful document structure
    write_text(out_dir / "cleaned.html", result.cleaned_html or "")

    # fit.html — the "fit" (content-focused) HTML, further pruned to include
    # only the main body content; this is what feeds the fit markdown variant
    write_text(out_dir / "fit.html", result.fit_html or "")

    ########################### Markdown Variants ############################

    # raw.md — markdown converted from the full cleaned HTML; captures everything
    # on the page including navigation bars, footers, and sidebars
    write_text(out_dir / "raw.md", raw_markdown(result.markdown))

    # fit.md — markdown derived from the fit HTML; contains only the core page
    # content, making it more suitable for downstream LLM consumption
    write_text(out_dir / "fit.md", fit_markdown(result.markdown))

    ########################### Links and Media ##############################

    # result.links is a dict with "internal" and "external" keys, each holding
    # a list of link objects discovered on the page.
    # - internal: links pointing to pages within the same domain
    # - external: links pointing to third-party domains
    internal = (result.links or {}).get("internal", [])
    external = (result.links or {}).get("external", [])
    print("internal_links:", len(internal))
    print("external_links:", len(external))

    # result.media is a dict keyed by media type (e.g., "images", "videos",
    # "audios"). Printing the sorted keys reveals which asset categories
    # Crawl4AI discovered on the page without dumping the full payloads.
    print("media_keys:", sorted((result.media or {}).keys()))


################################# Entry Point ################################

# Standard Python entry-point guard — use asyncio.run() to execute the
# async main() coroutine from a synchronous context
if __name__ == "__main__":
    asyncio.run(main())

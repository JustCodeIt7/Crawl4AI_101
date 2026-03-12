import asyncio
import sys
from pathlib import Path

############################# Path Configuration #############################

# When running this script directly (e.g., `python v07_links_media.py`), __package__
# will be None or empty. In that case, add the project root (two levels up) to
# sys.path so that sibling package imports resolve correctly.
if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

# Define the target URL to crawl — the official Crawl4AI documentation site
URL = "https://docs.crawl4ai.com/"

############################ Helper: Summarize ###############################


def summarize(label: str, result) -> None:
    """Print a one-line summary of link and image counts from a crawl result.

    Crawl4AI populates two dicts on the result object after a successful crawl:

    result.links — a dict with two keys:
        "internal"  — links whose href stays within the same domain as the
                      crawled URL (useful for site-map discovery)
        "external"  — links that point to a different domain (useful for
                      auditing outbound references or filtering noise)

    result.media — a dict whose keys correspond to media types found on the
    page. The most commonly used key is:
        "images"    — a list of dicts, each describing a discovered <img>
                      element (src, alt text, score, etc.)

    Both dicts default to None when the crawl is configured to skip link or
    media extraction, so we guard with `or {}` before calling .get().

    Args:
        label:  A short string printed at the start of the line to identify
                which crawl result is being summarised (e.g. "base", "trimmed").
        result: A CrawlResult object returned by AsyncWebCrawler.arun().
    """
    # Safely unpack the links dict; fall back to an empty dict if links is None
    internal = (result.links or {}).get("internal", [])
    external = (result.links or {}).get("external", [])

    # Safely unpack the media dict; the "images" list may be absent if no
    # images were discovered or if external images were excluded
    images = (result.media or {}).get("images", [])

    print(
        label,
        "html_chars=",
        len(result.html or ""),      # Raw HTML length gives a rough page-size proxy
        "internal_links=",
        len(internal),
        "external_links=",
        len(external),
        "images=",
        len(images),
    )


############################ Main Crawl Routine ##############################


async def main() -> None:
    """Run two crawls of the same URL and compare their link/media counts.

    The first crawl ("base") uses default settings so we capture everything
    the page exposes: internal links, external links, and all images.

    The second crawl ("trimmed") applies two filters:
        exclude_external_images   — strips any <img> whose src points to a
                                    domain other than the one being crawled,
                                    reducing noise from CDN-hosted assets and
                                    third-party tracking pixels
        exclude_social_media_links — removes hrefs that resolve to known
                                    social-media domains (Twitter/X, Facebook,
                                    LinkedIn, etc.), keeping the link list
                                    focused on substantive content references

    Comparing the two summaries makes it easy to see how much external image
    and social-link clutter a typical documentation page carries.
    """
    async with AsyncWebCrawler() as crawler:
        # Base crawl — no filtering; captures the full set of links and media
        base = await crawler.arun(
            url=URL,
            config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False),
        )

        # Trimmed crawl — same page, but with external images and social-media
        # links excluded so the result is leaner and easier to process
        trimmed = await crawler.arun(
            url=URL,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                exclude_external_images=True,       # Drop images hosted off-domain
                exclude_social_media_links=True,    # Drop links to social platforms
                verbose=False,
            ),
        )

    # Guard against crawl failures before reading result attributes
    if base.success:
        summarize("base", base)
    if trimmed.success:
        summarize("trimmed", trimmed)


################################# Entry Point ################################

# Standard Python entry-point guard — use asyncio.run() to execute the
# async main() coroutine from a synchronous context
if __name__ == "__main__":
    asyncio.run(main())

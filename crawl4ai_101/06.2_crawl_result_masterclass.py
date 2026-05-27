import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from rich import print

# Target URL to crawl
URL = "https://en.wikipedia.org/wiki/Web_scraping"


##################### Main Crawl Routine #######################
async def main() -> None:
    """Crawl a single URL and explore key CrawlResult fields."""
    # Configure crawler: bypass cache, skip extra captures, quiet logs
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        screenshot=False,
        pdf=False,
        capture_mhtml=False,
        verbose=False,
    )

    # Run crawler within async context manager (handles browser lifecycle)
    async with AsyncWebCrawler() as crawler:
        # Fetch page, render JS, populate CrawlResult
        result = await crawler.arun(url=URL, config=config)

    # Print success flag and HTTP status (status_code may be missing on errors)
    print("success:", result.success, "status:", getattr(result, "status_code", None))

    ##################### HTML Representations ####################
    # Full unmodified HTML from the browser
    print(f"raw.html length: {len(result.html or '')}")

    # Sanitised HTML (scripts/styles stripped)
    print(f"cleaned.html length: {len(result.cleaned_html or '')}")

    # Content-focused HTML (main body only)
    print(f"fit.html length: {len(result.fit_html or '')}")

    ######################## Markdown Variants #########################
    # Markdown from full cleaned HTML (includes nav/footer/sidebar)
    markdown = result.markdown

    # Markdown from full cleaned HTML (includes nav/footer/sidebar)
    print(f"raw.md length: {len(markdown.raw_markdown or '')}")

    # Markdown from fit HTML (core content, LLM-friendly)
    print(f"fit.md length: {len(markdown.fit_markdown or '')}")

    ######################## Links and Media #########################

    # result.links: dict with "internal" (same domain) and "external" (third-party) lists
    internal = (result.links or {}).get("internal", [])
    external = (result.links or {}).get("external", [])
    print("internal_links:", len(internal))
    print("external_links:", len(external))

    # result.media: dict keyed by type (images/videos/audios); show keys only
    print("media_keys:", sorted((result.media or {}).keys()))


############################# Entry Point #########################
if __name__ == "__main__":
    asyncio.run(main())

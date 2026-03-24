"""Video 04: Content selection with css_selector and target_elements.

Demonstrates:
- css_selector for scoped extraction
- target_elements for markdown focus with broader page context
- feature detection for newer options like flatten_shadow_dom

Prerequisites:
- `pip install crawl4ai playwright`
"""

################# Imports & Constants #################
import asyncio
import inspect
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from rich import print

URL = "https://docs.crawl4ai.com/core/quickstart/"


################# Helper Functions #################
def supports_config_option(name: str) -> bool:
    """Check if a given option exists in CrawlerRunConfig's signature."""
    return name in inspect.signature(CrawlerRunConfig).parameters


################# Main Crawl Logic #################
async def main() -> None:
    """Run two crawls to compare css_selector vs target_elements extraction."""

    # Limit extraction to content inside the <main> element only
    scoped_config = CrawlerRunConfig(
        css_selector="main",
        delay_before_return_html=0.5,  # Allow dynamic content to render
        verbose=False,
    )

    # Extract markdown from multiple elements while preserving full page context for links
    focused_config = CrawlerRunConfig(
        target_elements=["main", "nav"],
        delay_before_return_html=0.5,
        verbose=False,
    )

    # Run both crawl strategies against the same URL
    async with AsyncWebCrawler() as crawler:
        scoped = await crawler.arun(URL, config=scoped_config)
        focused = await crawler.arun(URL, config=focused_config)

    # Bail early if either crawl failed
    if not scoped.success:
        print(f"css_selector crawl failed: {scoped.error_message}")
        return
    if not focused.success:
        print(f"target_elements crawl failed: {focused.error_message}")
        return

    ################# Compare Results #################
    # Extract raw markdown, falling back to string representation for older versions
    scoped_md = getattr(scoped.markdown, "raw_markdown", str(scoped.markdown))
    focused_md = getattr(focused.markdown, "raw_markdown", str(focused.markdown))

    # Display content size and link counts to illustrate the difference between strategies
    print(
        f"css_selector markdown={len(scoped_md)} "
        f"internal_links={len((scoped.links or {}).get('internal', []))}"
    )
    print(scoped.markdown[:500])
    print(
        f"target_elements markdown={len(focused_md)} "
        f"internal_links={len((focused.links or {}).get('internal', []))}"
    )
    print(focused.markdown[:500])


if __name__ == "__main__":
    asyncio.run(main())

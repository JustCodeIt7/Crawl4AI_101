"""Video 04: Content selection with css_selector and target_elements.

Demonstrates:
- css_selector for scoped extraction
- target_elements for markdown focus with broader page context
- feature detection for newer options like flatten_shadow_dom

Prerequisites:
- `pip install crawl4ai playwright`
- `playwright install`

Run:
- `python crawl4ai_101/video_04_content_selection.py`
"""

import asyncio
import inspect

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

URL = "https://docs.crawl4ai.com/core/quickstart/"


def supports_config_option(name: str) -> bool:
    return name in inspect.signature(CrawlerRunConfig).parameters


async def main() -> None:
    scoped_config = CrawlerRunConfig(
        css_selector="main",
        delay_before_return_html=0.5,
        verbose=False,
    )
    focused_config = CrawlerRunConfig(
        target_elements=["main", "nav"],
        delay_before_return_html=0.5,
        verbose=False,
    )

    async with AsyncWebCrawler() as crawler:
        scoped = await crawler.arun(URL, config=scoped_config)
        focused = await crawler.arun(URL, config=focused_config)

    if not scoped.success:
        print(f"css_selector crawl failed: {scoped.error_message}")
        return
    if not focused.success:
        print(f"target_elements crawl failed: {focused.error_message}")
        return

    scoped_md = getattr(scoped.markdown, "raw_markdown", str(scoped.markdown))
    focused_md = getattr(focused.markdown, "raw_markdown", str(focused.markdown))
    print(
        f"css_selector markdown={len(scoped_md)} "
        f"internal_links={len((scoped.links or {}).get('internal', []))}"
    )
    print(
        f"target_elements markdown={len(focused_md)} "
        f"internal_links={len((focused.links or {}).get('internal', []))}"
    )

    if supports_config_option("flatten_shadow_dom"):
        print("flatten_shadow_dom is available in this Crawl4AI version.")
    else:
        print("flatten_shadow_dom is not available in this installed version.")


if __name__ == "__main__":
    asyncio.run(main())

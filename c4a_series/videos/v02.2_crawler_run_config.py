"""Video 03: Tuning each crawl with CrawlerRunConfig.

Demonstrates:
- word_count_threshold and excluded_tags
- external link filtering
- cache modes and config cloning
- wait_for and page timeout

Prerequisites:
- `pip install crawl4ai playwright`
- `playwright install`

Run:
- `python crawl4ai_101/video_03_crawler_run_config.py`
"""

import asyncio

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

URL = "https://docs.crawl4ai.com/core/quickstart/"


def count_links(result) -> tuple[int, int]:
    internal = len((result.links or {}).get("internal", []))
    external = len((result.links or {}).get("external", []))
    return internal, external


async def main() -> None:
    base_config = CrawlerRunConfig(
        word_count_threshold=20,
        excluded_tags=["nav", "footer", "header"],
        exclude_external_links=True,
        exclude_social_media_links=True,
        remove_overlay_elements=True,
        wait_for="css:main",
        page_timeout=30000,
        cache_mode=CacheMode.ENABLED,
        verbose=False,
    )
    bypass_config = base_config.clone(cache_mode=CacheMode.BYPASS)

    async with AsyncWebCrawler() as crawler:
        cached = await crawler.arun(URL, config=base_config)
        fresh = await crawler.arun(URL, config=bypass_config)

    if not cached.success:
        print(f"Cached crawl failed: {cached.error_message}")
        return
    if not fresh.success:
        print(f"Fresh crawl failed: {fresh.error_message}")
        return

    cached_links = count_links(cached)
    fresh_links = count_links(fresh)
    cached_md = getattr(cached.markdown, "raw_markdown", str(cached.markdown))
    fresh_md = getattr(fresh.markdown, "raw_markdown", str(fresh.markdown))

    print(
        f"Cached crawl: markdown={len(cached_md)} "
        f"internal_links={cached_links[0]} external_links={cached_links[1]}"
    )
    print(
        f"Fresh crawl: markdown={len(fresh_md)} "
        f"internal_links={fresh_links[0]} external_links={fresh_links[1]}"
    )
    print(
        "Config clone demo: "
        f"base_cache={base_config.cache_mode.value} "
        f"variant_cache={bypass_config.cache_mode.value}"
    )


if __name__ == "__main__":
    asyncio.run(main())

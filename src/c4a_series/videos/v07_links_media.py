import asyncio
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

URL = "https://docs.crawl4ai.com/"


def summarize(label: str, result) -> None:
    internal = (result.links or {}).get("internal", [])
    external = (result.links or {}).get("external", [])
    images = (result.media or {}).get("images", [])
    print(
        label,
        "html_chars=",
        len(result.html or ""),
        "internal_links=",
        len(internal),
        "external_links=",
        len(external),
        "images=",
        len(images),
    )


async def main() -> None:
    async with AsyncWebCrawler() as crawler:
        base = await crawler.arun(
            url=URL,
            config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False),
        )
        trimmed = await crawler.arun(
            url=URL,
            config=CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                exclude_external_images=True,
                exclude_social_media_links=True,
                verbose=False,
            ),
        )

    if base.success:
        summarize("base", base)
    if trimmed.success:
        summarize("trimmed", trimmed)


if __name__ == "__main__":
    asyncio.run(main())

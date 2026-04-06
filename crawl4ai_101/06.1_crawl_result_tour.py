"""Video 06: Understanding every field in CrawlResult.

Demonstrates:
- markdown, html, cleaned_html, links, media
- screenshot, PDF, and MHTML capture
- saving output artifacts to the local output folder

Prerequisites:
- `pip install crawl4ai playwright`
- `playwright install`

Run:
- `python crawl4ai_101/video_06_crawl_result_tour.py`
"""

import asyncio
import base64
from pathlib import Path

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

URL = "https://en.wikipedia.org/wiki/Web_scraping"
OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "video_06"


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def save_bytes(path: Path, data: bytes | None) -> None:
    if data:
        path.write_bytes(data)


async def main() -> None:
    output_dir = ensure_output_dir()
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        screenshot=True,
        pdf=True,
        capture_mhtml=True,
        verbose=False,
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(URL, config=config)

    if not result.success:
        print(f"Crawl failed: {result.error_message}")
        return

    markdown = getattr(result.markdown, "raw_markdown", str(result.markdown))
    (output_dir / "page.md").write_text(markdown or "", encoding="utf-8")

    if result.screenshot:
        png_bytes = base64.b64decode(result.screenshot)
        save_bytes(output_dir / "page.png", png_bytes)
    save_bytes(output_dir / "page.pdf", result.pdf)
    if result.mhtml:
        (output_dir / "page.mhtml").write_text(result.mhtml, encoding="utf-8")

    internal_links = len((result.links or {}).get("internal", []))
    external_links = len((result.links or {}).get("external", []))
    image_count = len((result.media or {}).get("images", []))
    print(f"Saved markdown to: {output_dir / 'page.md'}")
    print(f"Internal links: {internal_links}, external links: {external_links}")
    print(f"Images discovered: {image_count}")
    print(
        "Artifacts available: "
        f"png={bool(result.screenshot)} pdf={bool(result.pdf)} mhtml={bool(result.mhtml)}"
    )


if __name__ == "__main__":
    asyncio.run(main())

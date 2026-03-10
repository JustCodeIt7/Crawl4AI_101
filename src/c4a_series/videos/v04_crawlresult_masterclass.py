import asyncio
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

from c4a_series.common.io import episode_dir, fit_markdown, raw_markdown, write_text

URL = "https://docs.crawl4ai.com/"


async def main() -> None:
    out_dir = episode_dir("v04")
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        screenshot=False,
        pdf=False,
        capture_mhtml=False,
        verbose=False,
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    print("success:", result.success, "status:", getattr(result, "status_code", None))
    if not result.success:
        print("error:", result.error_message)
        return

    write_text(out_dir / "raw.html", result.html or "")
    write_text(out_dir / "cleaned.html", result.cleaned_html or "")
    write_text(out_dir / "fit.html", result.fit_html or "")
    write_text(out_dir / "raw.md", raw_markdown(result.markdown))
    write_text(out_dir / "fit.md", fit_markdown(result.markdown))

    internal = (result.links or {}).get("internal", [])
    external = (result.links or {}).get("external", [])
    print("internal_links:", len(internal))
    print("external_links:", len(external))
    print("media_keys:", sorted((result.media or {}).keys()))


if __name__ == "__main__":
    asyncio.run(main())

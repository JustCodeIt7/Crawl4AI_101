import asyncio
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

URL = "https://example.com/"
JS_CODE = """
document.body.insertAdjacentHTML(
  "beforeend",
  "<div class='js-ready'><strong>Injected by js_code</strong></div>"
);
"""


async def main() -> None:
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        js_code=JS_CODE,
        wait_for=".js-ready",
        verbose=False,
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    print("success:", result.success)
    print("js_ready_present:", "js-ready" in (result.html or ""))


if __name__ == "__main__":
    asyncio.run(main())

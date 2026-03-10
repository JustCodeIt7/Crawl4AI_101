import asyncio
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

URL = "https://example.com/"
SCRIPT = """
WAIT 1
IF (EXISTS `body`) THEN EVAL `document.body.insertAdjacentHTML('beforeend', '<div class="dsl-ready">C4A-Script worked</div>')`
WAIT `.dsl-ready` 5
"""


async def main() -> None:
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        c4a_script=SCRIPT,
        wait_for=".dsl-ready",
        verbose=False,
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    print("success:", result.success)
    print("dsl_ready_present:", "dsl-ready" in (result.html or ""))


if __name__ == "__main__":
    asyncio.run(main())

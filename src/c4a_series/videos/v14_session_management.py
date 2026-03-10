import asyncio
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig

SESSION_ID = "v14_session_demo"
URL = "https://example.com/"
SET_STATE_JS = """
sessionStorage.setItem("tutorial_state", "session-kept");
document.body.setAttribute("data-session-step", "1");
"""
READ_STATE_JS = """
const value = sessionStorage.getItem("tutorial_state") || "missing";
console.log("tutorial_state=" + value);
document.body.insertAdjacentHTML("beforeend", `<p class="session-value">${value}</p>`);
"""


async def main() -> None:
    async with AsyncWebCrawler() as crawler:
        step1 = await crawler.arun(
            url=URL,
            config=CrawlerRunConfig(
                session_id=SESSION_ID,
                cache_mode=CacheMode.BYPASS,
                js_code=SET_STATE_JS,
                wait_for="body[data-session-step='1']",
                verbose=False,
            ),
        )
        step2 = await crawler.arun(
            url=URL,
            config=CrawlerRunConfig(
                session_id=SESSION_ID,
                cache_mode=CacheMode.BYPASS,
                js_code=READ_STATE_JS,
                wait_for=".session-value",
                capture_console_messages=True,
                verbose=False,
            ),
        )
        await crawler.crawler_strategy.kill_session(SESSION_ID)

    print("step1:", step1.success)
    print("step2:", step2.success)
    print("console:", getattr(step2, "console_messages", None))


if __name__ == "__main__":
    asyncio.run(main())

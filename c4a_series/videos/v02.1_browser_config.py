"""Video 02: BrowserConfig controls your browser session.

Demonstrates:
- BrowserConfig browser type, viewport, user agent, headless mode
- Using clone() for debug variants
- text_mode/light_mode for lighter crawls

Prerequisites:
- `pip install crawl4ai playwright`
- Install the browsers you plan to use, for example `playwright install firefox`

Run:
- `python crawl4ai_101/video_02_browser_config.py`
"""

import asyncio
import time
from crawl4ai import AsyncWebCrawler, BrowserConfig
from rich import print
########################### Constants & Defaults ############################

URL = "https://www.python.org/"
PRIMARY_BROWSER = "firefox"
LARGE_VIEWPORT = (1440, 900)
MOBILE_VIEWPORT = (430, 932)


############################# Helper Functions #############################

async def crawl_once(label: str, config: BrowserConfig) -> None:
    """Crawl a single URL and print timing and result summary."""
    started = time.perf_counter()
    # Open a browser instance, crawl, then auto-close via async context manager
    async with AsyncWebCrawler(config=config) as crawler:
        result = await crawler.arun(URL)
    elapsed = time.perf_counter() - started
    print(
        f"\n{label}:\nsuccess={result.success}"
        f"\nbrowser={config.browser_type} "
        f"\nviewport={config.viewport_width}x{config.viewport_height} "
        f"\nchars={len(result.markdown)} "
        f"\ntime={elapsed:.2f}s\n"
    )


############################### Main Workflow ###############################

async def main() -> None:
    """Configure multiple browser profiles and run crawls to compare results."""
    # Set up the base desktop browser config with randomized user agent
    base_browser = BrowserConfig(
        browser_type=PRIMARY_BROWSER,
        headless=True,
        viewport_width=LARGE_VIEWPORT[0],
        viewport_height=LARGE_VIEWPORT[1],
        user_agent_mode="random",              # Rotate user agents to avoid fingerprinting
        verbose=False,
    )
    # Derive a mobile variant by cloning and overriding only the viewport
    mobile_browser = base_browser.clone(
        viewport_width=MOBILE_VIEWPORT[0],
        viewport_height=MOBILE_VIEWPORT[1],
    )
    # Enable text_mode and light_mode to skip images/JS for faster crawls
    text_browser = base_browser.clone(text_mode=True, light_mode=True)
    # Create a visible, verbose config useful for interactive debugging
    debug_browser = base_browser.clone(headless=False, verbose=True)

    print("Running headless large viewport crawl...")
    # Attempt crawls with the primary browser, falling back to chromium on failure
    try:
        await crawl_once("desktop", base_browser)
        await crawl_once("mobile", mobile_browser)
        await crawl_once("text-mode", text_browser)
    except Exception as exc:
        print(f"Primary browser '{PRIMARY_BROWSER}' failed: {exc}")
        fallback = base_browser.clone(browser_type="chromium")
        print("Retrying with chromium for compatibility...")
        await crawl_once("desktop-fallback", fallback)

    print(
        "Debug config ready: "
        f"browser={debug_browser.browser_type}, headless={debug_browser.headless}"
    )


if __name__ == "__main__":
    asyncio.run(main())

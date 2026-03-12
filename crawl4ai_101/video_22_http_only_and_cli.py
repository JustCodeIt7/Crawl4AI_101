"""Video 22: HTTP-only crawling and the Crawl4AI CLI.

Demonstrates:
- AsyncHTTPCrawlerStrategy for browser-free crawling
- timing comparison against browser-based crawling
- wrapping the `crwl` CLI with subprocess and runtime-generated config files

Prerequisites:
- `pip install crawl4ai playwright`
- `playwright install`
- Optional: `crwl` available on PATH

Run:
- `python crawl4ai_101/video_22_http_only_and_cli.py`
"""

import asyncio
import json
import shutil
import subprocess
import time
from pathlib import Path

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig, HTTPCrawlerConfig
from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy

BROWSER_URL = "http://example.com/"
CLI_URL = "https://news.ycombinator.com/"
OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "video_22"


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


async def run_http_only_demo() -> None:
    browser_config = BrowserConfig(headless=True, verbose=False)
    browser_run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False)
    http_strategy = AsyncHTTPCrawlerStrategy(browser_config=HTTPCrawlerConfig())
    http_run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False)

    started = time.perf_counter()
    async with AsyncWebCrawler(config=browser_config) as crawler:
        browser_result = await crawler.arun(BROWSER_URL, config=browser_run_config)
    browser_time = time.perf_counter() - started

    started = time.perf_counter()
    async with AsyncWebCrawler(crawler_strategy=http_strategy) as crawler:
        http_result = await crawler.arun(BROWSER_URL, config=http_run_config)
    http_time = time.perf_counter() - started

    print(
        f"Browser crawl: success={browser_result.success} "
        f"time={browser_time:.2f}s chars={len(browser_result.html or '')}"
    )
    print(
        f"HTTP-only crawl: success={http_result.success} "
        f"time={http_time:.2f}s chars={len(http_result.html or '')} "
        f"error={http_result.error_message or 'none'}"
    )


def run_cli_demo() -> None:
    crwl = shutil.which("crwl")
    if not crwl:
        print("CLI demo skipped: `crwl` is not available on PATH.")
        return

    output_dir = ensure_output_dir()
    extraction_config = output_dir / "extract_css.yml"
    schema_path = output_dir / "css_schema.json"
    extraction_config.write_text('type: "json-css"\nparams: {}\n', encoding="utf-8")
    schema_path.write_text(
        json.dumps(
            {
                "name": "HNStories",
                "baseSelector": "tr.athing",
                "fields": [
                    {"name": "title", "selector": "span.titleline > a", "type": "text"},
                    {
                        "name": "url",
                        "selector": "span.titleline > a",
                        "type": "attribute",
                        "attribute": "href",
                    },
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [crwl, CLI_URL, "-e", str(extraction_config), "-s", str(schema_path), "-o", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    print(f"CLI return code: {result.returncode}")
    stdout_preview = result.stdout.strip().splitlines()[:5]
    print(f"CLI stdout preview: {stdout_preview}")


def main() -> None:
    asyncio.run(run_http_only_demo())
    run_cli_demo()


if __name__ == "__main__":
    main()

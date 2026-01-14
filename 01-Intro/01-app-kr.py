# A concise, beginner-friendly comparison of Crawl4AI, Scrapy, and BeautifulSoup.
# Each helper scrapes the same URL for headlines + links, then we time them.

import asyncio
import json
import time
from typing import Callable, Dict, List, Tuple

import requests
from bs4 import BeautifulSoup
from scrapy import Selector

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


TARGET_URL = "https://news.ycombinator.com/"
HEADLINE_SELECTOR = "span.titleline > a"


def _limit_rows(rows: List[Dict], limit: int) -> List[Dict]:
    return rows[:limit]


def _time_run(label: str, runner: Callable[[], List[Dict]]) -> Tuple[str, float, List[Dict]]:
    start = time.perf_counter()
    data = runner()
    duration = time.perf_counter() - start
    return label, duration, data


def _show_sample(label: str, rows: List[Dict], limit: int = 5) -> None:
    print(f"\n{label} sample ({min(len(rows), limit)} of {len(rows)}):")
    for item in _limit_rows(rows, limit):
        print(f"- {item.get('headline')}: {item.get('link')}")


async def scrape_with_crawl4ai(url: str, limit: int = 10) -> List[Dict]:
    """Use Crawl4AI's built-in extractor for a lightweight, one-shot crawl."""
    schema = {
        "name": "Headlines",
        "baseSelector": "span.titleline",
        "fields": [
            {"name": "headline", "selector": "a", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
        ],
    }
    strategy = JsonCssExtractionStrategy(schema)
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # always hit the network for fresh content
        extraction_strategy=strategy,
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        extracted = json.loads(result.extracted_content or "[]")
        return _limit_rows(extracted, limit)


def scrape_with_scrapy(url: str, limit: int = 10) -> List[Dict]:
    """Use Scrapy's Selector on top of requests; no spider boilerplate required."""
    response = requests.get(url, timeout=15)
    sel = Selector(text=response.text)

    items: List[Dict] = []
    for node in sel.css("span.titleline"):
        items.append(
            {
                "headline": (node.css("a::text").get("")).strip(),
                "link": node.css("a::attr(href)").get(),
            }
        )
        if len(items) >= limit:
            break
    return items


def scrape_with_bs4(url: str, limit: int = 10) -> List[Dict]:
    """Plain requests + BeautifulSoup."""
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    items: List[Dict] = []

    for anchor in soup.select(HEADLINE_SELECTOR):
        items.append({"headline": anchor.get_text(strip=True), "link": anchor.get("href")})
        if len(items) >= limit:
            break
    return items


def compare() -> None:
    """Run each approach, print samples, and show a simple timing table."""
    runners = [
        ("Crawl4AI", lambda: asyncio.run(scrape_with_crawl4ai(TARGET_URL))),
        ("Scrapy", lambda: scrape_with_scrapy(TARGET_URL)),
        ("BeautifulSoup", lambda: scrape_with_bs4(TARGET_URL)),
    ]

    results: List[Tuple[str, float, List[Dict]]] = []

    for label, runner in runners:
        try:
            timed = _time_run(label, runner)
            results.append(timed)
            _show_sample(timed[0], timed[2])
        except Exception as exc:  # keep the demo rolling even if one fails
            print(f"\n{label} failed: {exc}")
            results.append((label, float("inf"), []))

    print("\n=== Performance (lower is faster) ===")
    for name, duration, _ in sorted(results, key=lambda r: r[1]):
        dur_display = f"{duration:.3f}s" if duration != float("inf") else "error"
        print(f"{name:13} {dur_display}")


if __name__ == "__main__":
    compare()

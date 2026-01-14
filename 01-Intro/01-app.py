import asyncio
import time
import requests
from bs4 import BeautifulSoup
import scrapy
from scrapy.crawler import CrawlerProcess
from crawl4ai import AsyncWebCrawler

# Comparison configuration
TARGET_URL = "https://news.ycombinator.com/"
LIMIT = 5

print(f"--- Web Scraping Library Comparison ---\nTarget: {TARGET_URL}\n")


# 1. BeautifulSoup + Requests
# Best for: Simple, static pages, beginners, lightweight tasks.
def run_beautifulsoup():
    print("[BeautifulSoup] Starting...")
    start = time.time()

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(TARGET_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    data = []
    # Hacker News structure: title is in <span class="titleline"><a ...>
    for el in soup.select(".titleline > a")[:LIMIT]:
        data.append({"title": el.get_text(), "href": el.get("href")})

    duration = time.time() - start
    print(f"[BeautifulSoup] Finished in {duration:.4f}s. Extracted {len(data)} items.")
    return data


# 2. Crawl4AI
# Best for: LLM data extraction, dynamic JS pages (Playwright based), clean markdown.
async def run_crawl4ai():
    print("[Crawl4AI] Starting...")
    start = time.time()

    # AsyncWebCrawler manages the browser session automatically
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=TARGET_URL)

        # We can use the raw HTML with BS4 or regex, or rely on Crawl4AI's extraction strategies.
        # For consistency in this specific comparison, we'll parse the HTML similarly.
        # Note: Crawl4AI executed JS, so it handles dynamic content better than BS4.
        soup = BeautifulSoup(result.html, "html.parser")

        data = []
        for el in soup.select(".titleline > a")[:LIMIT]:
            data.append({"title": el.get_text(), "href": el.get("href")})

    duration = time.time() - start
    print(f"[Crawl4AI] Finished in {duration:.4f}s. Extracted {len(data)} items.")
    return data


# 3. Scrapy
# Best for: Large scale, complex spiders, concurrency, pipelines.
# Note: Scrapy in a single script requires some boilerplate.
class HNSpider(scrapy.Spider):
    name = "hn_spider"
    start_urls = [TARGET_URL]
    custom_settings = {"LOG_LEVEL": "ERROR"}  # Suppressed logging
    extracted_data = []

    def parse(self, response):
        # Scrapy uses CSS selectors or XPath natively
        for el in response.css(".titleline > a")[:LIMIT]:
            item = {"title": el.css("::text").get(), "href": el.css("::attr(href)").get()}
            self.extracted_data.append(item)


def run_scrapy():
    print("[Scrapy] Starting...")
    start = time.time()

    # CrawlerProcess controls the Twisted reactor
    process = CrawlerProcess()
    process.crawl(HNSpider)
    process.start()  # Blocks execution until finish

    duration = time.time() - start
    print(f"[Scrapy] Finished in {duration:.4f}s. Extracted {len(HNSpider.extracted_data)} items.")
    return HNSpider.extracted_data


if __name__ == "__main__":
    # 1. Run BeautifulSoup (Sync)
    bs_results = run_beautifulsoup()

    # 2. Run Crawl4AI (Async)
    # Using asyncio.run to manage the event loop
    c4_results = asyncio.run(run_crawl4ai())

    # 3. Run Scrapy (Blocks Process)
    # Must be last because it starts a Twisted reactor that cannot be restarted in the same process
    sc_results = run_scrapy()

    print("\n--- Syntax Comparison Summary ---")
    print("BS4:      requests.get() -> BeautifulSoup(html) -> soup.select()")
    print("Crawl4AI: crawler.arun() -> result.html/.markdown")
    print("Scrapy:   Spider class -> parse method -> response.css() / yield")

import time
import requests
import asyncio
import json
from bs4 import BeautifulSoup
import scrapy
from scrapy.crawler import CrawlerProcess
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

# --- CONFIGURATION ---
TARGET_URL = "https://books.toscrape.com/"
RESULTS = {}  # Store timing results


# ==========================================
# 1. BEAUTIFUL SOUP (The Simple Synchronous Approach)
# ==========================================
def run_bs4():
    print(f"--- Running BeautifulSoup ---")
    start_time = time.perf_counter()

    response = requests.get(TARGET_URL)
    soup = BeautifulSoup(response.content, "html.parser")

    books = []
    # Select all articles with class 'product_pod'
    for article in soup.select("article.product_pod"):
        title = article.select_one("h3 > a")["title"]
        price = article.select_one(".price_color").text
        books.append({"title": title, "price": price})

    duration = time.perf_counter() - start_time
    print(f"✅ Extracted {len(books)} items.")
    return duration, books[:3]  # Return time and sample data


# ==========================================
# 2. CRAWL4AI (The Modern Async/AI Approach)
# ==========================================
async def run_crawl4ai():
    print(f"\n--- Running Crawl4AI ---")
    start_time = time.perf_counter()

    # Define a CSS extraction strategy (Extracts structured JSON directly)
    schema = {
        "name": "Books",
        "baseSelector": "article.product_pod",
        "fields": [
            {"name": "title", "selector": "h3 > a", "type": "attribute", "attribute": "title"},
            {"name": "price", "selector": ".price_color", "type": "text"},
        ],
    }

    extraction_strategy = JsonCssExtractionStrategy(schema)
    config = CrawlerRunConfig(extraction_strategy=extraction_strategy, cache_mode=CacheMode.BYPASS)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=TARGET_URL, config=config)

        # Crawl4AI returns a JSON string in extracted_content
        books = json.loads(result.extracted_content)

    duration = time.perf_counter() - start_time
    print(f"✅ Extracted {len(books)} items.")
    return duration, books[:3]


# ==========================================
# 3. SCRAPY (The Robust Framework Approach)
# ==========================================
# Scrapy usually runs as a project, but we can run it inline.
# We use a global list here for simplicity in this specific script context.
scrapy_books = []


class BookSpider(scrapy.Spider):
    name = "book_spider"
    start_urls = [TARGET_URL]
    custom_settings = {"LOG_LEVEL": "ERROR"}  # Suppress verbose logs

    def parse(self, response):
        for article in response.css("article.product_pod"):
            yield {"title": article.css("h3 > a::attr(title)").get(), "price": article.css(".price_color::text").get()}


def run_scrapy():
    print(f"\n--- Running Scrapy ---")
    start_time = time.perf_counter()

    # Define a pipeline to capture items into our list
    def capture_item(item, response, spider):
        scrapy_books.append(item)

    process = CrawlerProcess()
    crawler = process.create_crawler(BookSpider)
    # Connect a signal to catch items as they are scraped
    crawler.signals.connect(capture_item, signal=scrapy.signals.item_scraped)

    process.crawl(crawler)
    process.start()  # Blocks here until finished

    duration = time.perf_counter() - start_time
    print(f"✅ Extracted {len(scrapy_books)} items.")
    return duration, scrapy_books[:3]


# ==========================================
# MAIN EXECUTION & COMPARISON
# ==========================================
if __name__ == "__main__":
    print(f"Comparing scrapers on: {TARGET_URL}\n")

    # 1. Run BS4
    bs4_time, bs4_sample = run_bs4()
    RESULTS["BeautifulSoup"] = bs4_time

    # 2. Run Crawl4AI (Requires asyncio loop)
    crawl_time, crawl_sample = asyncio.run(run_crawl4ai())
    RESULTS["Crawl4AI"] = crawl_time

    # 3. Run Scrapy (Must run last because Reactor cannot be restarted)
    scrapy_time, scrapy_sample = run_scrapy()
    RESULTS["Scrapy"] = scrapy_time

    # --- FINAL REPORT ---
    print(f"\n{'=' * 40}")
    print(f"{'LIBRARY':<15} | {'TIME (s)':<10} | {'NOTES'}")
    print(f"{'-' * 40}")
    print(f"{'BeautifulSoup':<15} | {RESULTS['BeautifulSoup']:.4f}     | Best for simple, static HTML")
    print(f"{'Crawl4AI':<15} | {RESULTS['Crawl4AI']:.4f}     | Best for LLMs & Dynamic JS")
    print(f"{'Scrapy':<15} | {RESULTS['Scrapy']:.4f}     | Best for large scale/speed")
    print(f"{'=' * 40}")

    # Data Verification
    print(f"\nSample Data Verification (First Item):")
    print(f"BS4:      {bs4_sample[0]}")
    print(f"Crawl4AI: {crawl_sample[0]}")
    print(f"Scrapy:   {scrapy_sample[0]}")

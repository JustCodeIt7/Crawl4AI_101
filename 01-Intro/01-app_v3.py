"""
Web Scraper Comparison: Crawl4AI vs Scrapy vs BeautifulSoup
=============================================================

This script demonstrates why Crawl4AI is the superior choice for AI-powered
web scraping, especially when you need clean markdown output for LLMs.

Key Advantages of Crawl4AI:
1. Built-in markdown conversion - perfect for AI/LLM workflows
2. Async support out of the box - blazing fast performance
3. JavaScript rendering - handles modern SPAs effortlessly
4. Minimal code - simple API that just works
5. AI-ready output - structured data optimized for language models
"""

import asyncio
import time
from typing import Dict, List
from dataclasses import dataclass


# ==============================================================================
# CRAWL4AI IMPLEMENTATION - The Modern AI-First Approach
# ==============================================================================

async def scrape_with_crawl4ai(url: str) -> Dict:
    """
    Crawl4AI: The simplest and most powerful option for AI workflows.

    Advantages:
    - Automatic markdown conversion
    - JavaScript rendering built-in
    - Async by default (fast!)
    - AI-optimized output
    """
    from crawl4ai import AsyncWebCrawler

    start_time = time.time()

    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=url)

        return {
            "scraper": "Crawl4AI",
            "success": result.success,
            "markdown": result.markdown[:500],  # First 500 chars for demo
            "html_length": len(result.html),
            "markdown_length": len(result.markdown),
            "links_found": len(result.links.get("internal", [])) if result.links else 0,
            "time_taken": time.time() - start_time,
            "code_complexity": "LOW - Just 3 lines!",
            "ai_ready": "YES - Perfect markdown output"
        }


# ==============================================================================
# BEAUTIFULSOUP IMPLEMENTATION - The Traditional Approach
# ==============================================================================

def scrape_with_beautifulsoup(url: str) -> Dict:
    """
    BeautifulSoup: Simple but requires manual work.

    Limitations:
    - No JavaScript rendering
    - Manual markdown conversion needed
    - Synchronous only (slower)
    - Requires additional libraries for full functionality
    """
    import requests
    from bs4 import BeautifulSoup

    start_time = time.time()

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Manual text extraction (not true markdown!)
        text = soup.get_text(separator='\n', strip=True)

        # Manual link extraction
        links = [a.get('href') for a in soup.find_all('a', href=True)]

        return {
            "scraper": "BeautifulSoup",
            "success": response.status_code == 200,
            "markdown": text[:500],  # Not real markdown, just text
            "html_length": len(response.content),
            "markdown_length": len(text),
            "links_found": len(links),
            "time_taken": time.time() - start_time,
            "code_complexity": "MEDIUM - Manual extraction needed",
            "ai_ready": "PARTIAL - Just plain text, not structured markdown"
        }
    except Exception as e:
        return {
            "scraper": "BeautifulSoup",
            "success": False,
            "error": str(e),
            "time_taken": time.time() - start_time
        }


# ==============================================================================
# SCRAPY IMPLEMENTATION - The Framework Approach
# ==============================================================================

def scrape_with_scrapy(url: str) -> Dict:
    """
    Scrapy: Powerful but heavyweight for simple tasks.

    Limitations:
    - Requires full project setup
    - Steep learning curve
    - Overkill for single-page scraping
    - No built-in markdown conversion
    - Complex async configuration
    """
    from scrapy import Spider
    from scrapy.crawler import CrawlerProcess
    from scrapy.http import Request
    import logging

    start_time = time.time()
    results = {}

    class SimpleSpider(Spider):
        name = 'simple_spider'
        start_urls = [url]

        def parse(self, response):
            # Manual text extraction
            text = ' '.join(response.css('*::text').getall())
            links = response.css('a::attr(href)').getall()

            results.update({
                "scraper": "Scrapy",
                "success": True,
                "markdown": text[:500],  # Not real markdown
                "html_length": len(response.body),
                "markdown_length": len(text),
                "links_found": len(links),
                "code_complexity": "HIGH - Requires Spider class + setup",
                "ai_ready": "NO - Manual conversion required"
            })

    # Suppress Scrapy logs for cleaner output
    logging.getLogger('scrapy').setLevel(logging.ERROR)

    try:
        process = CrawlerProcess(settings={
            'LOG_ENABLED': False,
            'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7'
        })
        process.crawl(SimpleSpider)
        process.start()

        results["time_taken"] = time.time() - start_time
        return results
    except Exception as e:
        return {
            "scraper": "Scrapy",
            "success": False,
            "error": str(e),
            "time_taken": time.time() - start_time
        }


# ==============================================================================
# COMPARISON & DEMO
# ==============================================================================

async def run_comparison(url: str):
    """Run all three scrapers and compare results."""

    print("\n" + "="*80)
    print("WEB SCRAPER COMPARISON FOR AI WORKFLOWS")
    print("="*80)
    print(f"\nTarget URL: {url}\n")

    # 1. Crawl4AI (The Winner!)
    print("\n" + "-"*80)
    print("🚀 CRAWL4AI - The AI-First Solution")
    print("-"*80)
    crawl4ai_result = await scrape_with_crawl4ai(url)
    print_results(crawl4ai_result)

    # 2. BeautifulSoup
    print("\n" + "-"*80)
    print("🍲 BEAUTIFULSOUP - The Traditional Approach")
    print("-"*80)
    bs_result = scrape_with_beautifulsoup(url)
    print_results(bs_result)

    # 3. Scrapy
    print("\n" + "-"*80)
    print("🕷️  SCRAPY - The Framework Approach")
    print("-"*80)
    print("⚠️  Note: Scrapy requires full project setup for production use")
    scrapy_result = scrape_with_scrapy(url)
    print_results(scrapy_result)

    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY: Why Crawl4AI Wins for AI Workflows")
    print("="*80)
    print_summary(crawl4ai_result, bs_result, scrapy_result)


def print_results(result: Dict):
    """Pretty print scraper results."""
    if not result.get("success"):
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        return

    print(f"✅ Success: {result['success']}")
    print(f"⏱️  Time: {result['time_taken']:.3f}s")
    print(f"📄 HTML Size: {result['html_length']:,} bytes")
    print(f"📝 Markdown Size: {result['markdown_length']:,} chars")
    print(f"🔗 Links Found: {result['links_found']}")
    print(f"🧩 Complexity: {result.get('code_complexity', 'N/A')}")
    print(f"🤖 AI-Ready: {result.get('ai_ready', 'N/A')}")
    print(f"\n📋 Markdown Preview:\n{result['markdown'][:200]}...")


def print_summary(crawl4ai: Dict, bs: Dict, scrapy: Dict):
    """Print comparison summary."""

    print("\n✨ CRAWL4AI ADVANTAGES:\n")

    advantages = [
        ("Simplicity", "3 lines of code vs 20+ for others"),
        ("Markdown Output", "Native markdown - perfect for LLMs"),
        ("JavaScript Support", "Built-in - handles modern sites"),
        ("Async Performance", "Native async - fastest execution"),
        ("AI-Optimized", "Structured output ready for AI consumption"),
        ("Learning Curve", "Minimal - start scraping in minutes"),
        ("Maintenance", "Low - simple API, fewer dependencies")
    ]

    for feature, description in advantages:
        print(f"  ✓ {feature:20s} - {description}")

    print("\n⚡ SPEED COMPARISON:\n")
    print(f"  Crawl4AI:      {crawl4ai.get('time_taken', 0):.3f}s")
    print(f"  BeautifulSoup: {bs.get('time_taken', 0):.3f}s")
    print(f"  Scrapy:        {scrapy.get('time_taken', 0):.3f}s")

    print("\n🎯 USE CASES:\n")
    print("  Crawl4AI:      ✅ AI/LLM workflows, content extraction, RAG systems")
    print("  BeautifulSoup: ⚠️  Simple static sites, learning web scraping")
    print("  Scrapy:        ⚠️  Large-scale crawling projects with complex requirements")

    print("\n💡 THE VERDICT:\n")
    print("  For AI-powered applications, Crawl4AI is the clear winner!")
    print("  - Less code to write and maintain")
    print("  - Perfect markdown output for LLMs")
    print("  - Built for modern, JavaScript-heavy websites")
    print("  - Async performance out of the box")


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

async def main():
    """Main entry point."""

    # Example URLs to test (use sites that allow scraping)
    test_urls = [
        "https://example.com",
        # Add more URLs as needed
    ]

    for url in test_urls:
        await run_comparison(url)
        print("\n")


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════════════╗
    ║                                                                        ║
    ║           WEB SCRAPER SHOWDOWN: CRAWL4AI VS THE REST                  ║
    ║                                                                        ║
    ║  Comparing Crawl4AI, BeautifulSoup, and Scrapy for AI workflows       ║
    ║                                                                        ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """)

    asyncio.run(main())

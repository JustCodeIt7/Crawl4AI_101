import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig


async def test():
    async with AsyncWebCrawler() as crawler:
        # 1. Fresh fetch (populates cache)
        config1 = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
        res1 = await crawler.arun("https://example.com", config=config1)
        print(f"Fresh Fetch:")
        print(f"  Status: {res1.status_code}")
        print(
            f"  Markdown Length: {len(res1.markdown.raw_markdown) if res1.markdown else 0}"
        )
        print(f"  Success: {res1.success}")

        # 2. Cached fetch
        config2 = CrawlerRunConfig(cache_mode=CacheMode.ENABLED)
        res2 = await crawler.arun("https://example.com", config=config2)
        print(f"\nCached Fetch:")
        print(f"  Status: {res2.status_code}")
        print(
            f"  Markdown Length: {len(res2.markdown.raw_markdown) if res2.markdown else 0}"
        )
        print(f"  Success: {res2.success}")


if __name__ == "__main__":
    asyncio.run(test())

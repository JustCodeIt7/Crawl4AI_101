import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig


async def test():
    async with AsyncWebCrawler() as crawler:
        # 1. Fresh fetch (populates cache)
        # Use a fresh URL to ensure non-dirty cache
        url = "https://crawl4ai.com/mkdocs-tutorial/"
        config1 = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
        res1 = await crawler.arun(url, config=config1)
        print(f"Fresh Fetch:")
        print(f"  Status: {res1.status_code}")
        print(
            f"  Markdown Length: {len(res1.markdown.raw_markdown) if res1.markdown else 0}"
        )
        print(f"  Internal Links: {len(res1.links.get('internal', []))}")

        # 2. Cached fetch
        config2 = CrawlerRunConfig(cache_mode=CacheMode.ENABLED)
        res2 = await crawler.arun(url, config=config2)
        print(f"\nCached Fetch:")
        print(f"  Status: {res2.status_code}")
        print(f"  Markdown Object: {res2.markdown}")
        print(
            f"  Raw Markdown Preview: {res2.markdown.raw_markdown[:50] if res2.markdown else 'None'}"
        )
        print(f"  Internal Links Key Present: {'internal' in res2.links}")
        print(f"  Internal Links Count: {len(res2.links.get('internal', []))}")


if __name__ == "__main__":
    asyncio.run(test())

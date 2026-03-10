import asyncio
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import AsyncUrlSeeder, AsyncWebCrawler, CacheMode, CrawlerRunConfig, SeedingConfig

DOMAIN = "docs.crawl4ai.com"


async def main() -> None:
    async with AsyncUrlSeeder() as seeder:
        seeded = await seeder.urls(
            DOMAIN,
            SeedingConfig(source="sitemap", pattern="*docs.crawl4ai.com*", max_urls=25, extract_head=True),
        )

    valid_urls = [row["url"] for row in seeded if row.get("status") == "valid"][:5]
    print("seeded:", len(seeded), "valid:", len(valid_urls))

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun_many(
            valid_urls,
            config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False),
        )

    print("crawled:", sum(1 for result in results if result.success), "of", len(results))


if __name__ == "__main__":
    asyncio.run(main())

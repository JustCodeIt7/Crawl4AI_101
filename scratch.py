#%%
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://docs.crawl4ai.com/core/installation/",
        )
        print(result.markdown[:900])  # Show the first 300 characters of extracted text|

if __name__ == "__main__":
    asyncio.run(main())

# %%

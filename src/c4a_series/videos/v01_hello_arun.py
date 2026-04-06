import asyncio
from crawl4ai import AsyncWebCrawler

URL = "httpshttps://example.com"

async def main() -> None:
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL)

        if not result.success:
            print("Crawl failed:", result.error_message)
            return

        # result.markdown can be a string or MarkdownGenerationResult depending on config.
        md = result.markdown.raw_markdown if hasattr(result.markdown, "raw_markdown") else str(result.markdown)
        print(md[:300])

if __name__ == "__main__":
    asyncio_run_task = asyncio.run(main())

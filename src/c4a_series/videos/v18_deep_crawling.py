import asyncio
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import (
    AsyncWebCrawler,
    BestFirstCrawlingStrategy,
    CrawlerRunConfig,
    FilterChain,
    KeywordRelevanceScorer,
    URLPatternFilter,
)

START_URL = "https://docs.crawl4ai.com/"


async def main() -> None:
    strategy = BestFirstCrawlingStrategy(
        max_depth=1,
        max_pages=6,
        include_external=False,
        url_scorer=KeywordRelevanceScorer(keywords=["crawl", "config", "quickstart"], weight=0.7),
        filter_chain=FilterChain([URLPatternFilter(patterns=["*docs.crawl4ai.com*"])]),
    )
    config = CrawlerRunConfig(deep_crawl_strategy=strategy, stream=True, verbose=False)

    async with AsyncWebCrawler() as crawler:
        stream = await crawler.arun(START_URL, config=config)
        async for result in stream:
            metadata = result.metadata or {}
            print(
                "depth=",
                metadata.get("depth", 0),
                "score=",
                metadata.get("score", 0.0),
                "url=",
                result.url,
            )


if __name__ == "__main__":
    asyncio.run(main())

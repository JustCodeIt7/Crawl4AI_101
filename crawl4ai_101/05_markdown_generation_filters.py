"""Video 05: Markdown generation and fit filters.

Demonstrates:
- content_source: raw_html, cleaned_html, fit_html
- PruningContentFilter and BM25ContentFilter
- raw_markdown, fit_markdown, and references preview

Run:
- python crawl4ai_101/05_markdown_generation_filters.py
"""

import asyncio

from crawl4ai import (
    AsyncWebCrawler,
    BM25ContentFilter,
    CacheMode,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
)

from common.io import fit_markdown, preview, raw_markdown

URL = "https://docs.crawl4ai.com/core/browser-crawler-config/"
QUERY = "proxy configuration user agent browser config"


async def show_result(
    crawler: AsyncWebCrawler,
    label: str,
    generator: DefaultMarkdownGenerator,
    fit_view: bool = False,
):
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=generator,
        verbose=False,
    )
    result = await crawler.arun(URL, config=config)
    if not result.success:
        print(f"{label} failed: {result.error_message}")
        return None
    raw_text = raw_markdown(result.markdown)
    if not fit_view:
        print(f"{label}: chars={len(raw_text)} preview={preview(raw_text, 120)}")
        return result
    fit_text = fit_markdown(result.markdown)
    print(f"{label}: raw={len(raw_text)} fit={len(fit_text)} preview={preview(fit_text, 120)}")
    return result


async def main() -> None:
    async with AsyncWebCrawler() as crawler:
        print("== content_source ==")
        for source in ("raw_html", "cleaned_html", "fit_html"):
            await show_result(
                crawler,
                source,
                DefaultMarkdownGenerator(
                    content_source=source,
                    options={"ignore_links": True, "body_width": 80},
                ),
            )

        print("\n== content_filters ==")
        pruning = DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(
                threshold=0.45,
                threshold_type="dynamic",
                min_word_threshold=5,
            ),
            options={"citations": True, "body_width": 80},
        )
        bm25 = DefaultMarkdownGenerator(
            content_filter=BM25ContentFilter(user_query=QUERY, bm25_threshold=1.0),
            options={"citations": True, "body_width": 80},
        )
        await show_result(crawler, "pruning", pruning, fit_view=True)
        bm25_result = await show_result(crawler, "bm25", bm25, fit_view=True)
        if bm25_result:
            refs = (bm25_result.markdown.references_markdown or "").splitlines()[:3]
            print(f"references: {refs}")


if __name__ == "__main__":
    asyncio.run(main())

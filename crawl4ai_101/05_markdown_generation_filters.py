"""Video 05: Markdown generation and fit filters.

Demonstrates:
- content_source: raw_html, cleaned_html, fit_html
- PruningContentFilter and BM25ContentFilter
- raw markdown, fit markdown, and references preview

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
from rich import print

URL = "https://docs.crawl4ai.com/core/browser-crawler-config/"
QUERY = "proxy configuration user agent browser config"


async def show_result(
    crawler: AsyncWebCrawler,
    label: str,
    generator: DefaultMarkdownGenerator,
    fit_view: bool = False,
):
    """Crawl the page and print either raw-only or raw-vs-fit markdown stats."""
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=generator,
        verbose=False,
    )
    result = await crawler.arun(URL, config=config)
    if not result.success:
        print(f"{label} failed: {result.error_message}")
        return None

    markdown = result.markdown
    raw_text = markdown.raw_markdown or ""

    preview_text = raw_text
    summary = f"{label}: chars={len(raw_text)}"
    if fit_view:
        fit_text = markdown.fit_markdown or ""
        preview_text = fit_text
        summary = f"{label}: raw={len(raw_text)} fit={len(fit_text)}"

    preview = preview_text[:120].replace("\n", " ").strip()
    print(f"{summary} preview={preview}")
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

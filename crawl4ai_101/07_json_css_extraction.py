"""Video 07: JsonCssExtractionStrategy — structured data without LLMs.

Demonstrates:
- Schema structure: name, baseSelector, fields
- Field types: text, attribute, nested_list
- Transforms (strip, lowercase, uppercase) and default values
- baseFields for extracting attributes from the base element
- Nested extraction for hierarchical data
- Result handling with result.success and json.loads()

Prerequisites:
- `pip install crawl4ai playwright`
- `playwright install`

Run:
- `python crawl4ai_101/07_json_css_extraction.py`
"""

import asyncio
import json

from crawl4ai import (
    AsyncWebCrawler,
    CacheMode,
    CrawlerRunConfig,
    JsonCssExtractionStrategy,
)
from rich import print
# ── Demo URLs / raw HTML ─────────────────────────────────────────────────────

DOCS_URL = "https://docs.crawl4ai.com/"
HN_URL = "https://news.ycombinator.com/"

RAW_CATALOG_HTML = """
<section class="catalog">
  <div class="product" data-sku="kb-001">
    <h2 class="name">Mechanical Keyboard</h2>
    <span class="price">$129.00</span>
    <div class="reviews">
      <div class="review"><span class="author">Ava</span><span class="rating">5</span></div>
      <div class="review"><span class="author">Noah</span><span class="rating">4</span></div>
    </div>
  </div>
  <div class="product" data-sku="ms-002">
    <h2 class="name">Vertical Mouse</h2>
    <span class="price">$89.00</span>
    <div class="reviews">
      <div class="review"><span class="author">Mia</span><span class="rating">5</span></div>
    </div>
  </div>
</section>
"""


# ═══════════════════════════════════════════════════════════════════════════════
# Demo 1 — Basic CSS extraction (text + attribute)
# ═══════════════════════════════════════════════════════════════════════════════


async def demo_basic_extraction() -> None:
    """Extract navigation link text and href attributes from docs.crawl4ai.com.

    Schema keys:
        name          — human-readable label
        baseSelector  — CSS selector identifying each repeating record
        fields        — list of field descriptors (name, type, selector, etc.)
    """
    schema = {
        "name": "Docs navigation links",
        "baseSelector": "nav a",
        "fields": [
            # type="text" + transform="strip" → clean visible text
            {"name": "text", "type": "text", "transform": "strip"},
            # type="attribute" → pull an HTML attribute from the element
            {
                "name": "href",
                "selector": "a",
                "type": "attribute",
                "attribute": "href",
                "default": "",
            },
        ],
    }

    strategy = JsonCssExtractionStrategy(schema, verbose=False)
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=strategy,
        verbose=False,
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=DOCS_URL, config=config)

    if not result.success:
        print(f"Demo 1 failed: {result.error_message}")
        return

    rows = json.loads(result.extracted_content or "[]")
    print(f"Demo 1 — Basic (docs nav links): {len(rows)} items")
    if rows:
        print("First:")
        print(rows[0])
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# Demo 2 — baseFields + live site (Hacker News)
# ═══════════════════════════════════════════════════════════════════════════════


async def demo_hn_extraction() -> None:
    """Extract Hacker News stories with baseFields for element attributes.

    baseFields extracts attributes from the *baseSelector* element itself
    (here: the id on each <tr>), while fields extracts from child elements
    relative to the base.
    """
    schema = {
        "name": "Hacker News Stories",
        "baseSelector": "tr.athing",
        # Pull the HTML id attribute from each matched <tr> row
        "baseFields": [{"name": "story_id", "type": "attribute", "attribute": "id"}],
        "fields": [
            {"name": "rank", "selector": "span.rank", "type": "text", "transform": "strip"},
            {
                "name": "title",
                "selector": "span.titleline > a",
                "type": "text",
                "transform": "strip",
            },
            {
                "name": "url",
                "selector": "span.titleline > a",
                "type": "attribute",
                "attribute": "href",
            },
        ],
    }

    config = CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(schema, verbose=False),
        css_selector="tr.athing",  # only render story rows
        verbose=False,
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(HN_URL, config=config)

    if not result.success:
        print(f"Demo 2 failed: {result.error_message}")
        return

    items = json.loads(result.extracted_content or "[]")
    print(f"Demo 2 — HN stories: {len(items)} items")
    if items:
        print("First:")
        print(items[0])
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# Demo 3 — Nested extraction (type="nested_list")
# ═══════════════════════════════════════════════════════════════════════════════


async def demo_nested_extraction() -> None:
    """Extract product cards with nested reviews from raw HTML.

    type="nested_list" tells the extractor that the matched selector
    produces a list of sub-objects, each with their own fields.
    """
    schema = {
        "name": "Catalog",
        "baseSelector": "div.product",
        "baseFields": [{"name": "sku", "type": "attribute", "attribute": "data-sku"}],
        "fields": [
            {"name": "name", "selector": "h2.name", "type": "text"},
            {"name": "price", "selector": "span.price", "type": "text"},
            {
                "name": "reviews",
                "selector": "div.review",
                "type": "nested_list",
                "fields": [
                    {"name": "author", "selector": "span.author", "type": "text"},
                    {"name": "rating", "selector": "span.rating", "type": "text"},
                ],
            },
        ],
    }

    config = CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(schema, verbose=False),
        verbose=False,
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(f"raw://{RAW_CATALOG_HTML}", config=config)

    items = json.loads(result.extracted_content or "[]")
    print(f"Demo 3 — Nested products: {len(items)} items")
    if items:
        print("First:")
        print(items[0])
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════


async def main() -> None:
    await demo_basic_extraction()
    await demo_hn_extraction()
    await demo_nested_extraction()


if __name__ == "__main__":
    asyncio.run(main())

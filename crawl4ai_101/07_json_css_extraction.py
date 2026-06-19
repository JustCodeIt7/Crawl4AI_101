"""Video 07: JsonCssExtractionStrategy — structured data without LLMs.

Demonstrates:
- Schema structure: name, baseSelector, fields
- Field types: text, attribute, nested_list
- Transforms (strip, lowercase, uppercase) and default values
- baseFields for extracting attributes from the base element
- Nested extraction for hierarchical data
- Result handling with result.success and json.loads()


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

################################ Demo URLs & Raw HTML ################################

# Live sites used to demonstrate extraction against real pages
DOCS_URL = "https://docs.crawl4ai.com/"
HN_URL = "https://news.ycombinator.com/"

# Inline HTML fixture for the nested-extraction demo (no network call needed)
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


################################ Demo 1 — Basic CSS Extraction ################################


async def demo_basic_extraction() -> None:
    """Extract navigation link text and href attributes from the docs site."""
    # Define the extraction schema: one record per matched nav link
    schema = {
        "name": "Docs navigation links",
        "baseSelector": "nav a",  # Each matched element becomes one record
        "fields": [
            # type="text" + transform="strip" → clean visible text
            {"name": "text", "type": "text", "transform": "strip"},
            # type="attribute" → pull an HTML attribute from the element
            {
                "name": "href",
                "selector": "a",
                "type": "attribute",
                "attribute": "href",
                "default": "",  # Fall back to empty string when missing
            },
        ],
    }

    # Wire the schema into the strategy and crawler run configuration
    strategy = JsonCssExtractionStrategy(schema, verbose=False)
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # Always fetch fresh for demo accuracy
        extraction_strategy=strategy,
        verbose=False,
    )

    # Run the crawl with the configured extraction strategy
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=DOCS_URL, config=config)

    # Parse the JSON string into Python objects (empty list if nothing extracted)
    rows = json.loads(result.extracted_content or "[]")
    print(f"Demo 1 — Basic (docs nav links): {len(rows)} items")
    if rows:
        print("First:")
        print(rows[0])
    print()


################################ Demo 2 — baseFields + Live Site ################################


async def demo_hn_extraction() -> None:
    """Extract Hacker News stories using baseFields for row-level attributes."""
    # Define schema; baseFields read attributes from the matched <tr> itself
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
        css_selector="tr.athing",  # Limit rendering to just the story rows
        verbose=False,
    )

    # Crawl Hacker News and extract structured story data
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(HN_URL, config=config)

    items = json.loads(result.extracted_content or "[]")
    print(f"Demo 2 — HN stories: {len(items)} items")
    if items:
        print("First:")
        print(items[0])
    print()


################################ Demo 3 — Nested Extraction ################################


async def demo_nested_extraction() -> None:
    """Extract product cards with nested reviews from raw HTML."""
    # Schema uses nested_list to capture child review objects per product
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
                "type": "nested_list",  # Produce a list of sub-objects per match
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

    # Use the raw:// scheme to parse inline HTML without a network request
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(f"raw://{RAW_CATALOG_HTML}", config=config)

    items = json.loads(result.extracted_content or "[]")
    print(f"Demo 3 — Nested products: {len(items)} items")
    if items:
        print("First:")
        print(items[0])
    print()


################################ Entry Point ################################


async def main() -> None:
    """Run all three extraction demos in sequence."""
    await demo_basic_extraction()
    await demo_hn_extraction()
    await demo_nested_extraction()


# Launch the async event loop only when run as a script
if __name__ == "__main__":
    asyncio.run(main())

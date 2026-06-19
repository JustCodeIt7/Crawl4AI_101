import asyncio
import json
import sys
from pathlib import Path
from crawl4ai import (
    AsyncWebCrawler,
    CacheMode,
    CrawlerRunConfig,
    JsonCssExtractionStrategy,
)
from rich import print


URL = "https://docs.crawl4ai.com/"

############################ Extraction Schema ###############################
# JsonCssExtractionStrategy uses a declarative schema to map CSS selectors
# directly onto structured JSON output — no custom parsing code required.
#
# Schema keys:
#   name          - human-readable label for the schema (used in logging)
#   baseSelector  - CSS selector that identifies each repeating item on the
#                   page; one output record is produced per matched element
#   fields        - list of field descriptors that define what data to pull
#                   out of each matched element
SCHEMA = {
    "name": "Docs navigation links",
    # Match every <a> element inside any <nav> — each anchor becomes one row
    # in the output list
    "baseSelector": "nav a",
    "fields": [
        # "text" field: grab the visible inner text of the element.
        # type="text"        — extract the element's text content
        # transform="strip"  — trim leading/trailing whitespace from the value
        {"name": "text", "type": "text", "transform": "strip"},
        # "href" field: pull a specific HTML attribute value from the element.
        # selector="a"       — look for an <a> tag within (or at) the base element
        # type="attribute"   — extract an attribute rather than text content
        # attribute="href"   — the specific attribute to read
        # default=""         — fall back to an empty string if the attribute is absent
        # extract the link from the anchor tag inside the nav item, defaulting to empty string when missing
        {
            "name": "href",
            "type": "attribute",
            "attribute": "href",
            "default": "",
        },
    ],
}

# A secondary schema illustrating how to extract other types of elements.
# Here we extract headings (<h2>) from the page to get their titles and ID anchors.
SCHEMA_2 = {
    "name": "Content Headings",
    # Scope the extraction to <h2> elements, so each heading becomes one record in the output list
    "baseSelector": "h2",
    # Extract the visible text of the heading as the "title" field, trimming whitespace
    "fields": [
        {"name": "title", "type": "text", "transform": "strip"},  # Extract the heading text, stripping whitespace
        {  # Extract the "id" attribute from the <h2> as "anchor_id", defaulting to "no-id" when missing
            "name": "anchor_id",
            "type": "attribute",
            "attribute": "id",
            "default": "no-id",
        },
    ],
}


############################ Main Crawl Routine ##############################
async def main() -> None:
    """Crawl a single URL and extract structured data using CSS selectors."""
    # Attach the extraction strategy to a CrawlerRunConfig so it runs
    # automatically after the page is fetched and rendered
    strategy = JsonCssExtractionStrategy(SCHEMA, verbose=False)
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, extraction_strategy=strategy, verbose=False)

    # Launch an async crawler session using a context manager, which handles
    # browser startup and teardown (Crawl4AI uses a headless browser under the hood)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

        # Let's also demonstrate SCHEMA_2
        strategy_2 = JsonCssExtractionStrategy(SCHEMA_2, verbose=False)
        config_2 = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, extraction_strategy=strategy_2, verbose=False)
        result_2 = await crawler.arun(url=URL, config=config_2)

    # result.extracted_content is a JSON string. Parse it to a Python list.
    nav_links = json.loads(result.extracted_content)
    print("--- SCHEMA 1 (Nav Links) ---")
    print(json.dumps(nav_links[:5], indent=4))
    print("items:", len(nav_links))
    if nav_links:
        print("first:", nav_links[0])

    headings = json.loads(result_2.extracted_content)
    print("\n--- SCHEMA 2 (Headings) ---")
    print("items:", len(headings))
    if headings:
        print("first:", headings[0])
        print("all:\n", json.dumps(headings, indent=4))


################################# Entry Point ################################
if __name__ == "__main__":
    asyncio.run(main())

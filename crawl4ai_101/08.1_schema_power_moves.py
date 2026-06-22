import asyncio
import json
from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig, JsonCssExtractionStrategy
from rich import print

URL = "https://docs.crawl4ai.com/core/quickstart/"

################################ Schema Definition ###########################

# JsonCssExtractionStrategy accepts a schema dict that describes *what* to
# extract and *how* to structure the output.  This schema demonstrates three
# advanced features:
#
#   1. baseSelector  — scopes ALL extraction to a single root element.
#                      Using "main" means only content inside <main> is
#                      considered; headers, footers, and nav bars are ignored.
#
#   2. baseFields    — fields extracted ONCE from the baseSelector element
#                      itself (not repeated).  Use these for page-level
#                      metadata that appears exactly once, such as the <h1>
#                      title.
#
#   3. fields        — repeated or structured fields extracted relative to the
#                      baseSelector.  Two sub-types are used here:
#
#       • nested_list — each matched element becomes its own dict inside a
#                       list.  Sub-fields are extracted *relative to each
#                       matched element*, so you get per-item attribute data
#                       (e.g., the anchor href that lives inside each heading).
#                       Use nested_list when you need structured objects, not
#                       just plain text.
#
#       • list        — similar to nested_list but optimised for simpler
#                       cases where you primarily want a single value per
#                       matched element (e.g., the full text of each <pre>
#                       block).  The distinction matters: nested_list builds
#                       richer per-item dicts, while list keeps the output
#                       flat and concise.
SCHEMA = {
    "name": "Docs article outline",
    # Scope the entire extraction to the <main> element so we skip chrome (nav, sidebar, footer) and focus on the article body
    "baseSelector": "main",
    # baseFields are extracted once from the root element — perfect for page-level data like the primary <h1> heading
    "baseFields": [
        {"name": "page_title", "selector": "h1", "type": "text", "transform": "strip", "default": "Untitled"},
    ],
    "fields": [
        {
            # nested_list: each <h2> or <h3> becomes a dict with both its
            # visible text AND the href of its anchor link — two sub-fields per matched element
            "name": "sections",
            "type": "nested_list",
            "selector": "h2, h3",
            "fields": [
                # The visible heading text, whitespace-normalised
                {"name": "heading", "type": "text", "transform": "strip", "default": ""},
                {  # Extract the "id" attribute from the <h2> as "anchor_id", defaulting to "no-id" when missing
                    "name": "anchor_id",
                    "type": "attribute",
                    "attribute": "id",
                    "default": "no-id",
                },
            ],
        },
        {
            # list: each <pre> block yields a single text snippet — only one
            # sub-field per element, so the simpler list type is appropriate
            "name": "code_blocks",
            "type": "list",
            "selector": "pre",
            "fields": [
                # Full text content of the code block, stripped of leading/trailing whitespace
                {"name": "snippet", "type": "text", "transform": "strip", "default": ""},
            ],
        },
    ],
}

# SCHEMA_2 demonstrates additional advanced features:
#   1. extract raw HTML using type: "html"
#   2. multiple attributes from the same element
#   3. apply string transformations (e.g. uppercase)
SCHEMA_2 = {
    "name": "Advanced Extractions",
    "baseSelector": "main",
    "fields": [
        {
            # nested_list: extract links, apply uppercase transform to the text
            # and pull both href and class attributes
            "name": "links",
            "type": "nested_list",
            "selector": "a",
            "fields": [
                {"name": "text", "type": "text", "transform": "uppercase"},
                {"name": "href", "type": "attribute", "attribute": "href"},
                {"name": "css_class", "type": "attribute", "attribute": "class", "default": ""},
            ],
        },
        {
            # nested_list: extract both the clean text and the raw HTML of paragraphs
            "name": "paragraphs",
            "type": "nested_list",
            "selector": "p",
            "fields": [
                {"name": "text", "type": "text"},
                {"name": "raw_html", "type": "html"},
            ],
        },
    ],
}


############################ Main Crawl Routine ##############################
async def main() -> None:
    """Crawl the Crawl4AI quickstart page and extract a structured outline."""
    strategy = JsonCssExtractionStrategy(SCHEMA, verbose=False)

    # Build the crawler run config:
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, extraction_strategy=strategy, verbose=False)

    # Launch the headless browser session, crawl the page
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    # Guard against network errors, timeouts, or selector mismatches
    if result.success:
        # extracted_content is a JSON string containing a list of records — one
        # record per baseSelector match (here, one record for the single <main>)
        rows = json.loads(result.extracted_content or "[]")
        record = rows[0] if rows else {}
        print("\n######## Page Title ########")
        print(record["page_title"])  # print the full extracted record for reference
        # Report the page-level title captured via baseFields
        print("title:", record.get("page_title"))
        # Report how many headings were captured by the nested_list "sections" field
        print("\n###### sections ######")
        print(record["sections"][:3])  # print the first section dict for reference
        print("section_count:", len(record.get("sections", [])))
        # Report how many code blocks were captured by the list "code_blocks" field
        print("\n###### code blocks ######")
        print(record["code_blocks"][:3])  # print the first code block snippet for reference
        print("code_block_count:", len(record.get("code_blocks", [])))

    # --- Run SCHEMA_2 to see advanced extractions in action ---
    strategy_2 = JsonCssExtractionStrategy(SCHEMA_2, verbose=False)
    config_2 = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, extraction_strategy=strategy_2, verbose=False)

    async with AsyncWebCrawler() as crawler:
        result_2 = await crawler.arun(url=URL, config=config_2)

    if result_2.success:
        rows_2 = json.loads(result_2.extracted_content or "[]")
        record_2 = rows_2[0] if rows_2 else {}
        print("\n######## SCHEMA_2: Advanced Extractions ########")
        print("First 2 links (uppercase text & multiple attrs):")
        print(record_2.get("links", [])[:5])

        print("\nFirst paragraph (text vs raw_html):")
        print(record_2.get("paragraphs", [])[:3])


################################# Entry Point ################################
if __name__ == "__main__":
    asyncio.run(main())

"""Video 09: Deterministic extraction with XPath and Regex strategies.

Demonstrates:
- JsonXPathExtractionStrategy for positional table scraping
- RegexExtractionStrategy with built-in + custom patterns
- running both strategies without a single LLM call
"""

import asyncio
import json

from crawl4ai import (
    AsyncWebCrawler,
    CacheMode,
    CrawlerRunConfig,
    JsonXPathExtractionStrategy,
    RegexExtractionStrategy,
)
from rich import print

############################## Target Configuration ##############################

# The devguide renders release branches in <table class="docutils"> blocks.
# We target the first table (active branches) for the XPath demo.
URL = "https://devguide.python.org/versions/"


############################### XPath Extraction ################################
async def run_xpath_demo() -> None:
    """Extract version-table rows with XPath — no LLM, deterministic, fast.

    The schema mirrors the table layout: one record per <tr> that contains
    <td> cells (header rows only have <th>, so they're skipped). Each field
    uses a relative XPath ('./td[N]') to pick a column by position.
    """
    # Define the record shape: one object per matched row, one field per column
    schema = {
        "name": "Python Versions",
        # [td] keeps only data rows; position()>1 would also work but is
        # fragile if the table gains extra header/foot rows later.
        "baseSelector": '//table[contains(@class,"docutils")][1]//tr[td]',
        # Selectors are relative to baseSelector, so index columns by position
        "fields": [
            {"name": "branch", "selector": "./td[1]", "type": "text"},
            {"name": "schedule", "selector": "./td[2]", "type": "text"},
            {"name": "status", "selector": "./td[3]", "type": "text"},
            {"name": "first_release", "selector": "./td[4]", "type": "text"},
            {"name": "end_of_life", "selector": "./td[5]", "type": "text"},
            {"name": "release_manager", "selector": "./td[6]", "type": "text"},
        ],
    }
    # Attach the schema-driven strategy so parsing happens during the crawl
    config = CrawlerRunConfig(
        extraction_strategy=JsonXPathExtractionStrategy(schema),
        cache_mode=CacheMode.BYPASS,  # live page; never serve a stale run
        verbose=False,
    )
    # Open a browser session just long enough to fetch and parse the page
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(URL, config=config)
    # extracted_content is a JSON string; coerce "" -> [] when nothing matched
    rows = json.loads(result.extracted_content or "[]")
    print(f"[bold green]XPath:[/] extracted {len(rows)} version rows")
    # print(rows[:3])  # show first 3 for brevity
    print(rows)


############################### Regex Extraction ################################


async def run_regex_demo() -> None:
    """Pull dates and PEP numbers out of the same page with regex.

    Built-in patterns (DateIso) are combined with a custom `pep` pattern:
    `pattern=` is an IntFlag covering common types, while `custom=` adds
    site-specific ones by name. Each result is {url, label, value, span}.
    """
    # Combine a built-in pattern flag with a domain-specific custom pattern
    strategy = RegexExtractionStrategy(
        pattern=RegexExtractionStrategy.DateIso,
        custom={"pep": r"\bPEP\s?\d{3,4}\b"},  # label becomes "pep" in results
    )
    config = CrawlerRunConfig(
        extraction_strategy=strategy,
        cache_mode=CacheMode.BYPASS,
        verbose=False,
    )
    # Reuse the same page so the two strategies can be compared directly
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(URL, config=config)
    matches = json.loads(result.extracted_content or "[]")
    # Group matches by label for a tidy per-type summary
    by_label: dict[str, list[str]] = {}
    print("Regex matches (label, value, span):")
    print(matches)  # show first 3 for brevity
    for m in matches:
        by_label.setdefault(m["label"], []).append(m["value"])
    print(f"[bold green]Regex:[/] {len(matches)} matches across {len(by_label)} labels")
    # Report a small sample per label instead of dumping every hit
    for label, values in by_label.items():
        uniq = list(dict.fromkeys(values))  # dedupe, keep first-seen order
        print(f"  {label} ({len(values)}): {uniq[:4]}")


################################## Entry Point ##################################
async def main() -> None:
    """Run both extraction demos in sequence for side-by-side comparison."""
    await run_xpath_demo()
    await run_regex_demo()


if __name__ == "__main__":
    asyncio.run(main())

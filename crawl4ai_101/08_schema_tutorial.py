"""Video 08 — Schema-Based Extraction with Crawl4AI (Full Tutorial)

Three lessons in one runnable file:

  Lesson 1  Power moves of a HAND-WRITTEN schema
            (baseSelector, baseFields, nested_list, list)

  Lesson 2  AUTO-GENERATE a schema from sample HTML with an LLM
            (generate_schema on a tiny inline HTML snippet)

  Lesson 3  GENERATE-ONCE, REUSE-FOREVER on a live page
            (cache the LLM schema to disk to save tokens/cost)

Prerequisites:
  pip install crawl4ai playwright python-dotenv
  playwright install
  export OPENAI_API_KEY=...        # only needed for Lessons 2 & 3

Run:
  python 08_schema_tutorial.py 1     # run Lesson 1
  python 08_schema_tutorial.py 2     # run Lesson 2
  python 08_schema_tutorial.py 3     # run Lesson 3
  python 08_schema_tutorial.py all   # run everything (default)
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from crawl4ai import (
    AsyncWebCrawler,
    CacheMode,
    CrawlerRunConfig,
    JsonCssExtractionStrategy,
    LLMConfig,
)

# --------------------------------------------------------------------------- #
# Shared configuration & tiny helpers (inlined so the file is self-contained)
# --------------------------------------------------------------------------- #

URL = "https://docs.crawl4ai.com/core/quickstart/"
OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "video_08"
SCHEMA_FILE = OUTPUT_DIR / "quickstart_schema.json"


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def require_api_key() -> str | None:
    """Return the OpenAI key, or print a friendly skip message and return None."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("SKIP: set OPENAI_API_KEY to run LLM-based schema generation.")
    return key


# A tiny inline page used for Lesson 2 — no network needed.
SAMPLE_HTML = """
<section class="products">
  <article class="product-card">
    <h2>Starter Drone</h2>
    <p class="price">$249.00</p>
    <p class="rating">4.7 stars</p>
  </article>
  <article class="product-card">
    <h2>Studio Microphone</h2>
    <p class="price">$189.00</p>
    <p class="rating">4.9 stars</p>
  </article>
</section>
"""


# =========================================================================== #
# LESSON 1 — Power moves of a HAND-WRITTEN schema
# =========================================================================== #
#
#   baseSelector  scopes ALL extraction to one root element (here <main>),
#                 so nav/header/footer noise is ignored.
#
#   baseFields    fields extracted ONCE from the baseSelector element itself —
#                 perfect for page-level metadata like the single <h1>.
#
#   fields        repeated/structured fields extracted relative to baseSelector:
#       nested_list  each match becomes a dict with multiple sub-fields
#                    (e.g., heading text + the anchor href inside it).
#       list         each match yields a single value (e.g., one code snippet).
#
POWER_MOVES_SCHEMA = {
    "name": "Docs article outline",
    "baseSelector": "main",
    "baseFields": [
        {"name": "page_title", "selector": "h1", "type": "text", "transform": "strip", "default": "Untitled"},
    ],
    "fields": [
        {
            "name": "sections",
            "type": "nested_list",  # richer per-item dicts
            "selector": "h2, h3",
            "fields": [
                {"name": "heading", "type": "text", "transform": "strip", "default": ""},
                {"name": "anchor", "selector": "a", "type": "attribute", "attribute": "href", "default": ""},
            ],
        },
        {
            "name": "code_blocks",
            "type": "list",  # flat list of single values
            "selector": "pre",
            "fields": [
                {"name": "snippet", "type": "text", "transform": "strip", "default": ""},
            ],
        },
    ],
}


async def lesson_1_power_moves() -> None:
    print("\n=== LESSON 1: hand-written schema power moves ===")
    strategy = JsonCssExtractionStrategy(POWER_MOVES_SCHEMA, verbose=False)
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=strategy,
        verbose=False,
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    if not result.success:
        print("schema extraction failed:", result.error_message)
        return

    rows = json.loads(result.extracted_content or "[]")
    record = rows[0] if rows else {}
    print("title:", record.get("page_title"))
    print("section_count:", len(record.get("sections", [])))
    print("code_block_count:", len(record.get("code_blocks", [])))


# =========================================================================== #
# LESSON 2 — AUTO-GENERATE a schema from sample HTML with an LLM
# =========================================================================== #
async def lesson_2_generate_from_sample() -> None:
    print("\n=== LESSON 2: LLM-generated schema from inline HTML ===")
    api_key = require_api_key()
    if not api_key:
        return
    if not hasattr(JsonCssExtractionStrategy, "generate_schema"):
        print("SKIP: this Crawl4AI version does not expose generate_schema().")
        return

    output_dir = ensure_output_dir()

    # The LLM inspects the markup and returns a CSS extraction schema.
    schema = JsonCssExtractionStrategy.generate_schema(
        SAMPLE_HTML,
        query="Extract each product name, price, and rating as a flat record.",
        llm_config=LLMConfig(provider="openai/gpt-4o-mini", api_token=api_key),
    )
    schema_path = output_dir / "product_schema.json"
    write_json(schema_path, schema)

    # Reuse the generated schema deterministically — no further LLM call.
    config = CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(schema),
        verbose=False,
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(f"raw://{SAMPLE_HTML}", config=config)

    if not result.success:
        print(f"Generated-schema crawl failed: {result.error_message}")
        return

    items = json.loads(result.extracted_content or "[]")
    print(f"Generated schema saved to: {schema_path}")
    print(f"Reusable extraction rows: {len(items)}")
    if items:
        print(f"First row: {items[0]}")


# =========================================================================== #
# LESSON 3 — GENERATE-ONCE, REUSE-FOREVER on a live page (token-saving)
# =========================================================================== #
async def fetch_sample_html() -> str:
    """Fetch a truncated HTML slice of the target page for schema generation.

    The LLM only needs a representative sample — sending the full document
    wastes tokens and may exceed context limits. Prefer cleaned_html and cap
    at 12,000 chars.
    """
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=URL,
            config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False),
        )
    if not result.success:
        raise RuntimeError(result.error_message)
    return (result.cleaned_html or result.html or "")[:12000]


async def lesson_3_generate_and_cache() -> None:
    print("\n=== LESSON 3: generate-once, cache, reuse (save tokens) ===")
    api_key = require_api_key()
    if not api_key:
        return

    ensure_output_dir()

    if SCHEMA_FILE.exists():
        # Cached from a previous run — skip the billable LLM call.
        schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
        print("using cached schema:", SCHEMA_FILE)
    else:
        schema = JsonCssExtractionStrategy.generate_schema(
            html=await fetch_sample_html(),
            schema_type="CSS",
            query="Extract the article title and major quickstart sections from this page.",
            llm_config=LLMConfig(provider="openai/gpt-4o-mini", api_token=api_key),
        )
        write_json(SCHEMA_FILE, schema)
        print("generated schema:", SCHEMA_FILE)

    # Deterministic extraction — no further LLM calls.
    strategy = JsonCssExtractionStrategy(schema, verbose=False)
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=strategy,
        verbose=False,
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=URL, config=config)

    print("success:", result.success)
    print("extracted preview:", (result.extracted_content or "")[:250])


# =========================================================================== #
# Entry point — pick a lesson from the command line
# =========================================================================== #
LESSONS = {
    "1": lesson_1_power_moves,
    "2": lesson_2_generate_from_sample,
    "3": lesson_3_generate_and_cache,
}


async def main() -> None:
    choice = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    if choice == "all":
        for lesson in LESSONS.values():
            await lesson()
    elif choice in LESSONS:
        await LESSONS[choice]()
    else:
        print(f"Unknown lesson '{choice}'. Choose one of: 1, 2, 3, all")


if __name__ == "__main__":
    asyncio.run(main())

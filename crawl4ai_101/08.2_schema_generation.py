"""Video 08: Auto-generate extraction schemas with an LLM.

Demonstrates:
- JsonCssExtractionStrategy.generate_schema()
- saving a generated schema for reuse
- running the generated schema without another LLM call
"""

import asyncio
import json
from pathlib import Path

from crawl4ai import (
    AsyncWebCrawler,
    CacheMode,
    CrawlerRunConfig,
    JsonCssExtractionStrategy,
    LLMConfig,
)
from rich import print
import os
from dotenv import load_dotenv

load_dotenv()
############################### Configuration & Constants ################################
# Ollama runs locally and needs no API key — the provider string follows
OLLAMA_MODEL = "gemma4:26b"
# OLLAMA_BASE_URL from environment variable or default to localhost
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://eos.local:11434")

# Resolve output directory relative to this script so results land consistently
OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "video_08"

# URL = "https://docs.crawl4ai.com/"
URL = "https://en.wikipedia.org/wiki/Computer_programming"


################################ Helper Functions ################################
def ensure_output_dir() -> Path:
    """Create the output directory if needed and return its path."""
    # Use parents=True/exist_ok=True to safely create nested dirs without errors
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


################################ Main Workflow ################################
async def main() -> None:
    """Generate a schema via LLM, persist it, then reuse it for extraction without a second LLM call."""
    output_dir = ensure_output_dir()

    # Step 1: Crawl the target page to get its HTML and learn its structure
    print(f"Crawling {URL} to get sample HTML...")
    async with AsyncWebCrawler() as crawler:
        initial_result = await crawler.arun(URL, config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False))
        if not initial_result.success:
            print(f"Initial crawl failed: {initial_result.error_message}")
            return

        # Prefer cleaned_html (boilerplate stripped) over raw html so the local
        # model sees a compact, signal-rich view. Truncate to 12 000 chars to stay
        # within the model's context window — sending the full raw HTML to a
        # locally-hosted model often truncates the JSON response mid-schema.
        sample_html = (initial_result.cleaned_html or initial_result.html or "")[:10000]

    # Query of what you want to extract
    QUERY = f"""Extract the main page title, and list of the main pages content for each section header.
    HTML Sample:
    {sample_html}
    """
    # QUERY = f"""Extract the main page title, and list of the section title and section content.
    # HTML Sample:
    # {sample_html}
    # """
    provider = f"ollama/{OLLAMA_MODEL}"

    # Ollama serves models locally, so no api_token is required — only the
    # provider/model name and the base URL where the Ollama API is listening.
    # max_tokens must be large enough for the model to emit a complete JSON
    # schema; too small a budget causes truncated output and JSON parse errors.
    llm_config = LLMConfig(provider=provider, base_url=OLLAMA_BASE_URL, temperature=0)

    print("Generating schema via LLM...")
    schema = JsonCssExtractionStrategy.generate_schema(sample_html, query=QUERY, llm_config=llm_config)
    print("Generated schema:")
    print(json.dumps(schema, indent=2))

    # Persist the generated schema so future runs can skip the LLM entirely
    schema_path = output_dir / "08.2-schema_generation.json"
    schema_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")

    # Step 3: Configure the crawler to apply the generated schema purely via CSS rules
    print("Re-crawling with the generated, LLM-free schema...")
    config = CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(schema),
        cache_mode=CacheMode.BYPASS,
        verbose=False,
    )

    # Run the crawler against the original URL using the reusable, LLM-free schema
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(URL, config=config)

    # Bail out early if the crawl did not succeed
    if not result.success:
        print(f"Generated-schema crawl failed: {result.error_message}")
        return

    # Parse the extracted JSON, defaulting to an empty list when nothing was returned
    items = json.loads(result.extracted_content or "[]")
    print(f"Reusable extraction records: {len(items)}")

    # Preview the records to confirm the schema captured the expected fields
    print(items)


################################ Entry Point ################################
if __name__ == "__main__":
    asyncio.run(main())

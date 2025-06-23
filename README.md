# Crawl4AI Examples and Sitemap Tool

This repository contains examples and a sitemap crawling tool for the `crawl4ai` Python library. `crawl4ai` is an asynchronous web crawler for AI-driven content extraction.

## Key Features of `crawl4ai`

*   Asynchronous crawling with `asyncio` and `playwright`.
*   JavaScript execution for dynamic content.
*   HTML cleaning and Markdown generation.
*   Link and media analysis.
*   Advanced extraction strategies: CSS Selectors, LLM-based, Cosine Similarity.
*   Session management and customizable hooks.

## Getting Started

### Installation

1.  **Install libraries**:
    ```bash
    pip install -U crawl4ai nest_asyncio
    ```
2.  **Setup Playwright**:
    ```bash
    crawl4ai-setup
    # Or: playwright install --with-deps chrome
    ```
3.  **Verify**:
    ```bash
    crawl4ai-doctor
    ```

### Running Examples

*   `crawl4ai_quickstart.ipynb`: Jupyter Notebook with detailed examples.
*   `crawl4ai_quickstart.py`: Python script version.

Run script: `python crawl4ai_quickstart.py`
Run notebook: `jupyter notebook crawl4ai_quickstart.ipynb`

The examples cover basic crawling, dynamic content, content cleaning, link/media analysis, custom hooks, session management, and various extraction strategies.

## Sitemap Crawler Tool (`crawl_sitmap.py`)

Crawls a sitemap and saves page content as Markdown.

### Usage:
`python crawl_sitmap.py <sitemap_url> [-o OUTPUT_DIR]`

**Example:**
`python crawl_sitmap.py https://example.com/sitemap.xml -o crawled_data`

## Dependencies

*   `crawl4ai`
*   `nest_asyncio`
*   (Playwright is handled by `crawl4ai` setup)

See `requirements.txt`:
```bash
pip install -r requirements.txt
```

## Contributing

Issues and pull requests are welcome.

## License

Licensed under the terms of the `LICENSE` file.
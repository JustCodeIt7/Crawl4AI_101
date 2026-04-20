# Repository Guidelines

## Project Overview

This repository is an educational resource for [Crawl4AI](https://github.com/unclecode/crawl4ai), an AI-powered web crawling library. It accompanies a YouTube tutorial series and contains runnable examples, quickstart scripts, and Jupyter notebooks.

## Project Structure

- **`crawl4ai_101/`** — Core tutorial scripts. Numbered files follow a progressive path from basic crawling to advanced topics like LLM extraction and deep crawling.
- **`crawl4ai_quickstart.py` / `.ipynb`** — Starter examples for new users.
- **`crawl_sitmap.py`** — Sitemap-based site crawler example.
- **`web_scraper_comparison.ipynb`** — Notebook comparing Crawl4AI against BeautifulSoup, Scrapy, Selenium, and Playwright.
- **`archive/`** — Deprecated notebooks and scripts. Not actively maintained.
- **`Crawl4AI_Outline.md`** — Full video tutorial outline with cross-references to runnable scripts.

## Setup & Running

This project requires **Python 3.13+**.

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -e "."
   playwright install
   ```
3. Run a tutorial script:
   ```bash
   python crawl4ai_101/01.1_first_crawl.py
   ```

## LLM Features

Scripts using LLM extraction (e.g., `10.1_llm_extraction.py`, `10.3_knowledge_graph.py`) read `OPENAI_API_KEY` from `.env`. Populate `.env` before running these examples.

## Coding Style

- **Language:** Python 3.13
- **Formatting:** PEP 8, 4-space indentation.
- **Naming:** `snake_case` for modules. Zero-padded numbers for tutorial ordering (e.g., `05_markdown_generation_filters.py`).
- **Comments:** Descriptive docstrings for new functions; comments should explain *why*, not *what*.

## Testing

No formal test suite — this is an educational project. Validate new examples by running them end-to-end and confirming expected output.

## Commit & PR Guidelines

**Commit messages** follow conventional style:
- `feat: <description>` — new scripts or features
- `refactor: <description>` — structural changes
- `docs: <description>` — documentation updates

**Pull requests** should include:
- A brief description of what changed and why.
- Confirmation that relevant script(s) run successfully.
- Screenshots or output snippets for visual changes.

## Security & Configuration

- Never commit secrets (API keys, tokens). Use `.env` for credentials — it is git-ignored.
- Respect `robots.txt` and website terms of service when running scraping examples.

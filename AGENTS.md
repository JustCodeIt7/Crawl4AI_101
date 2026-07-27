You are an experienced, pragmatic software engineering AI agent. Do not over-engineer a solution when a simple one is possible. Keep edits minimal. If you want an exception to ANY rule, you MUST stop and get permission first.

# Repository Guidelines

## Project Overview

Educational resource for [Crawl4AI](https://github.com/unclecode/crawl4ai), accompanying a YouTube tutorial series. Runnable Python examples and Jupyter notebooks, no library/package being published.

`README.md` is partially stale (references a nonexistent `src/c4_series/videos/`, says Python 3.8+, suggests `conda activate py312`). Trust `pyproject.toml` and `.python-version` (Python 3.13) over the README.

## Project Structure

- **`crawl4ai_101/`** — Core tutorial scripts, zero-padded numbered in lesson order (see `crawl4ai_101/README.md` for the full sequence). Run from repo root.
- **`crawl4ai_101/common/io.py`** — Shared helpers used by LLM/schema episodes: `load_env()` (custom, no python-dotenv), `SCHEMA_CACHE_DIR`, `episode_dir()`, `write_json()`. Creates `crawl4ai_101/runs/`, `schema_cache/`, `pattern_cache/` at runtime.
- **`crawl4ai_quickstart.py` / `.ipynb`** — Starter examples.
- **`crawl_sitmap.py`** — Sitemap crawler example (note the typo in filename, preserve it).
- **`web_scraper_comparison.ipynb`** — Cross-library comparison.
- **`archive/`** — Deprecated. Not maintained; don't edit.
- **`Crawl4AI_Outline.md`** — Full video outline with script cross-references.

## Setup & Running

Requires **Python 3.13** (`pyproject.toml` `requires-python = ">=3.13"`, `.python-version` = 3.13).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e "."
playwright install
```

Run scripts from the **repo root** so `from crawl4ai_101.common.io import ...` resolves:

```bash
python crawl4ai_101/01.1_first_crawl.py
```

### Dependency gotcha

`pyproject.toml` only declares `crawl4ai` and `rich`. The comparison/quickstart scripts also import `beautifulsoup4`, `requests`, `scrapy`, `selenium`, and Jupyter — these are **not** in `pyproject`. Install manually when running those files:

```bash
pip install beautifulsoup4 requests scrapy selenium jupyter
```

Do not add them to `pyproject.toml` unless asked — the tutorial intentionally keeps core deps minimal.

## LLM Features

LLM/schema episodes (`08.3_generate_schema_tokenusage.py`, `10.1_llm_extraction.py`, `10.2_llm_extraction_chunking.py`, `10.3_knowledge_graph.py`, `21.2_production_self_hosting.py`) call `load_env()` from `crawl4ai_101.common.io`, which reads `OPENAI_API_KEY` from `.env` at the repo root. `.env` is git-ignored.

`08.2_schema_generation.py` and `08.3` cache generated schemas under `crawl4ai_101/schema_cache/`; clear that dir to force regeneration.

## Coding Style

- Python 3.13, PEP 8, 4-space indent.
- `snake_case` modules; zero-padded lesson numbers (`05.2_markdown_filters.py`). Preserve dotted-number filenames.
- Docstrings on new functions; comments explain *why*, not *what*.
- No comments unless explaining a non-obvious decision.

## Testing

No formal test suite, no lint/typecheck configured. Validate changes by running the affected script end-to-end and confirming expected output.

## Commit & PR Guidelines

Conventional commits: `feat:`, `refactor:`, `docs:`. PRs should confirm the relevant script(s) run successfully.

## Security & Configuration

- Never commit secrets. Use `.env` (git-ignored) for `OPENAI_API_KEY`.
- Respect `robots.txt` and site ToS when running scraping examples.
# AGENT OPERATIONS GUIDE
- Audience: autonomous agents working in this repo (Crawl4AI tutorial/examples).
- Goal: quickly recall commands, conventions, and guardrails without re-reading the codebase.

# PROJECT SNAPSHOT
- Language: Python 3.8+; async heavy for Crawl4AI/Playwright.
- Main scripts: `01-Intro/01-app.py`, `01-Intro/01-app_v3.py`, `crawl4ai_quickstart.py`, `crawl_sitmap.py`, `use-browser_101/01-intro.py`, notebooks (ipynb) for demos.
- No package manager files committed; install deps manually.
- No CI, no tests folder, no lint config, no Cursor rules, no Copilot rules.

# ENV & DEPENDENCIES
- Install core packages:
  - `pip install crawl4ai playwright beautifulsoup4 requests scrapy selenium rich nest_asyncio` (plus `jupyter` for notebooks, `pydantic` used in quickstart, `jsonschema` optional).
  - After installing Playwright: `playwright install` (downloads browsers).
- Recommended but not enforced: `pip install ruff black mypy pytest`.
- Use virtualenv/conda; avoid polluting system Python.
- Some examples need network access; respect robots.txt and site ToS.

# BUILD / RUN COMMANDS
- Run quickstart crawler: `python crawl4ai_quickstart.py` (ensure Playwright browsers installed).
- Run intro comparison (HN scraper): `python 01-Intro/01-app.py`.
- Run verbose comparison with type hints and rich output: `python 01-Intro/01-app_v3.py`.
- Run sitemap example: `python crawl_sitmap.py`.
- Run browser sanity check: `python use-browser_101/01-intro.py`.
- Execute specific snippet in quickstart: comment/uncomment sections; the file chains multiple `asyncio.run(...)` calls.
- Notebooks: `jupyter notebook crawl4ai_quickstart.ipynb` or `web_scraper_comparison.ipynb`.

# TESTING (NONE CONFIGURED)
- There is no automated test suite in the repo today.
- If you add tests, prefer `pytest` with async support: `pytest -q`.
- Run a single test file (once added): `pytest tests/test_file.py -q`.
- Run a single test by name: `pytest tests/test_file.py -k name_substring -q`.
- If you need smoke coverage now, wrap scripts into small functions and call via pytest.

# LINT & FORMAT (AD HOC)
- No linters configured; recommended workflow:
  - Format: `black .` (or target files) with default 88 width.
  - Lint: `ruff .` (flags imports, style, unused vars).
  - Types: `mypy .` (opt into strict mode for new modules).
- Keep imports sorted (use `ruff --select I` or `isort` style if needed).
- Avoid enforcing tools in repo; document new tooling if you add configs.

# IMPORT GUIDELINES
- Order: stdlib, third-party, local; blank line between groups.
- Avoid wildcard imports; prefer explicit functions/classes.
- Keep import-side effects minimal; in Playwright/Crawl4AI examples, defer heavyweight imports inside functions if optional.
- For type-only imports, guard with `if TYPE_CHECKING:` when costly.

# PYTHON STYLE
- Use snake_case for functions/vars, CapWords for classes, UPPER_SNAKE for constants (see `TARGET_URL`, `LIMIT`).
- Favor type hints for new/edited code (`Dict`, `List`, concrete types like `str`, `int`).
- Docstrings for public functions explaining purpose and params; concise summary line.
- Prefer f-strings for interpolation; keep user-facing prints short.
- Keep line length ~100 max; wrap chained calls.
- Use `async with AsyncWebCrawler(...) as crawler:` for lifecycle safety.
- Prefer `pathlib.Path` over string paths when adding filesystem work.

# ERROR HANDLING
- Network calls: set timeouts (`requests.get(..., timeout=10)` as in quickstart), handle HTTP errors with `raise_for_status` when appropriate.
- Catch broad exceptions only to report actionable context; log/print minimal detail to avoid leaking secrets.
- When scraping multiple steps, fail softly per-step and continue aggregating successes.
- For async tasks, use `asyncio.gather(..., return_exceptions=True)` if running multiple crawls.
- Clean up Playwright/Crawl4AI sessions; rely on context managers.

# ASYNC / EVENT LOOP NOTES
- Many scripts stack `asyncio.run(...)`; avoid nesting when composing—refactor to a single `main()` that awaits sub-coroutines.
- For notebooks or environments with active loops, apply `nest_asyncio` as shown in `crawl4ai_quickstart.py` before running Playwright.
- When mixing sync + async (e.g., Scrapy and asyncio), ensure Scrapy runs last since Twisted reactor cannot restart (see `01-Intro/01-app.py`).

# SCRAPING PRACTICES
- Respect robots.txt; throttle requests when iterating URLs.
- Use realistic User-Agent headers for `requests`; Crawl4AI handles browser headers automatically.
- When executing custom JS via Crawl4AI, keep scripts idempotent and short; wait for DOM changes with polling or selectors.
- Use `CacheMode.ENABLED` for repeatable dev runs; bypass when freshness matters.
- For extraction strategies (`JsonCssExtractionStrategy`, `LLMExtractionStrategy`, `CosineStrategy`), store schemas alongside code for reproducibility.

# DATA HANDLING
- Trim printed markdown for logs (see quickstart slicing to 500 chars).
- When persisting data, prefer JSON/Parquet over ad-hoc prints; sanitize URLs.
- Avoid embedding API keys in source; load from env vars (e.g., `OPENAI_API_KEY`) if adding LLM-backed extraction.

# LOGGING & OUTPUT
- Current samples use `print` and `rich.print`; keep outputs concise and emoji-light for terminals.
- For reusable modules, switch to `logging` with module-level logger; keep default INFO.
- Avoid noisy third-party logs; adjust Scrapy log level via `custom_settings` or settings dict as in examples.

# STRUCTURE & MODULARITY
- If expanding, move shared utilities (headers, parsing, timing) into a `utils.py` module under `01-Intro/` or root.
- Keep demo scripts single-purpose; gate execution with `if __name__ == "__main__":` to allow import without side effects.
- For notebook parity, keep code snippets in plain `.py` for agents; notebooks should call into modules, not duplicate logic.

# NAMING & CONSTANTS
- Use clear names like `TARGET_URL`, `LIMIT`, `js_code`, `session_id`; avoid abbreviations without meaning.
- Keep magic numbers as named constants; document why (e.g., polling interval 100ms for commit pagination).

# DEPENDENCY SAFETY
- Pin versions in a future `requirements.txt` if reproducibility matters; current repo leaves versions open.
- After `playwright install`, CI-less environments need manual browser cache; note platform differences (darwin, linux).

# PERFORMANCE
- Batch DOM queries where possible; avoid tight loops without sleeps when waiting for page updates.
- Use caching when re-crawling similar pages; prefer `CacheMode.ENABLED` during development.

# SECURITY & COMPLIANCE
- Do not commit secrets or cookies; use env vars and `.env` excluded from VCS.
- Avoid scraping sites that forbid automation; provide attribution if required.
- Respect rate limits; add `asyncio.sleep` between requests when hitting same domain.

# GIT & CONTRIBUTIONS
- Branch naming: `feature/<slug>` or `fix/<slug>`.
- Keep commits focused; include rationale in messages ("explain why" > "what").
- Do not amend or force push unless explicitly requested.

# AGENT WORKFLOW (RECOMMENDED STEPS)
- Inspect current tree: `ls` and glance at README.md for context.
- Ensure env: activate venv, install deps, run `playwright install` once.
- Run target script; confirm browser downloads if Playwright fails.
- Make changes with `apply_patch`; keep ASCII only.
- If adding tooling/tests, document commands in this file and README.
- If adding new examples, mirror existing patterns: clear constants, async entry point, summary prints.

# TROUBLESHOOTING QUICK HINTS
- Playwright "Executable doesn't exist": rerun `playwright install chromium`.
- Event loop already running (notebooks): call `nest_asyncio.apply()` before `asyncio.run` or use `await` in cells.
- Scrapy reactor errors: avoid multiple runs in same process; separate invocations or refactor to spiders inside a proper project.
- Network 403/429: set headers, slow down, or switch target URL for demos.

# FUTURE IMPROVEMENTS (IF TIME ALLOWS)
- Add `requirements.txt` with locked versions and optional extras for lint/test.
- Add `pytest` smoke tests wrapping key scripts to validate imports and basic crawl flow with mocked responses.
- Add `ruff`/`black` config to standardize style and import sorting.
- Factor repetitive crawl snippets into reusable helper module.

# CONTACT & CONTEXT
- Primary reference: README.md (overview, install commands, feature summary).
- External docs: Crawl4AI docs, Playwright Python docs.
- No additional policy files detected (Cursor/Copilot rules absent).
- Notebook parity: mirror code in `.py` modules so agents can diff easily.
- Large artifacts (data dumps, screenshots) should live outside repo or be gitignored.
- Keep sample URLs stable and scrape-friendly; prefer `example.com` when unsure.

# REMINDER
- Keep outputs minimal and deterministic where possible; avoid live network dependence in tests.
- Default to safe targets like `https://example.com` when demonstrating.
- Maintain this AGENTS.md alongside new tooling changes; update line counts loosely ~150 lines for readability.
- Prefer small, composable functions over monolith scripts when extending examples.
- When adding CLI flags, provide defaults so scripts run without extra args.
- Document any new environment variables at the top of the modified script.
- For long-running crawls, log progress every N pages with timestamps.

# Crawl4AI 101 Organized

This folder merges the tutorial material from `crawl4ai_101/` and `c4a_series/` into one start-to-finish sequence for a YouTube series.

## Lesson order

### Foundations
- `01.1_first_crawl.py` — first crawl starter (`crawl4ai_101/01_first_crawl.py`)
- `01.2_hello_arun.py` — alternate intro (`c4a_series/01_hello_arun.py`)
- `02_config_objects.py` — config overview
- `02.1_browser_config.py` — browser config deep dive
- `02.2_crawler_run_config.py` — crawler run config deep dive
- `03_cache_modes.py` — cache behavior
- `04_content_selection.py` — CSS/targeted content selection
- `05.1_markdown_generation.py` — markdown generation basics
- `05.2_markdown_filters.py` — markdown filtering walkthrough
- `05.3_fit_markdown_filters.py` — advanced fit markdown filters
- `06.1_crawl_result_tour.py` — CrawlResult tour
- `06.2_crawl_result_masterclass.py` — deeper CrawlResult walkthrough
- `06.3_links_and_media.py` — links and media extraction

### Structured extraction
- `07.1_css_extraction.py` — CSS extraction basics
- `07.2_json_css_extraction.py` — JSON CSS extraction
- `08.1_schema_power_moves.py` — advanced schema design patterns
- `08.2_schema_generation.py` — LLM-assisted schema generation
- `08.3_generate_schema_tokenusage.py` — schema generation with token usage notes
- `09.1_xpath_and_regex.py` — XPath plus regex extraction
- `09.2_regex_extraction.py` — regex extraction deep dive
- `10.1_llm_extraction.py` — basic LLM extraction
- `10.2_llm_extraction_chunking.py` — chunking long pages for LLM extraction
- `10.3_knowledge_graph.py` — knowledge graph extraction example
- `11_strategy_selection.py` — choosing the right extraction strategy

### Dynamic pages and state
- `12.1_page_interaction.py` — interaction basics
- `12.2_js_and_waits.py` — JavaScript execution and waits
- `13.1_virtual_scroll.py` — virtual scroll walkthrough
- `13.2_virtual_scroll_alt.py` — alternate virtual scroll version
- `14.1_session_management.py` — session management walkthrough
- `14.2_session_management_alt.py` — alternate session patterns
- `15_c4a_script_dsl.py` — Crawl4AI script DSL
- `16_hooks_and_auth.py` — hooks and auth
- `17_identity_and_magic_mode.py` — identity and magic mode
- `18_proxy_and_stealth.py` — proxies and stealth

### Scale and deployment
- `19.1_deep_crawling.py` — deep crawling walkthrough
- `19.2_deep_crawling_alt.py` — alternate deep crawling version
- `19.3_url_seeding.py` — URL seeding
- `20.1_multi_url_dispatchers.py` — multi-URL dispatchers
- `20.2_arun_many_dispatchers.py` — alternate `arun_many()` dispatcher example
- `21.1_docker_rest_api.py` — Docker and REST API
- `21.2_production_self_hosting.py` — self-hosting and production notes
- `22_http_only_and_cli.py` — HTTP-only crawling and CLI
- `23_downloads_screenshots_ssl.py` — downloads, screenshots, and SSL
- `24_ai_ready_pipeline.py` — end-to-end AI-ready pipeline

## Support folders

- `common/` — normalized helper utilities for the reorganized lessons.
- `reference/` — copied outlines plus `output/` sample artifacts from `crawl4ai_101/`.
- `extras/conflicted_copies/` — preserved Dropbox conflicted copies so nothing tutorial-related was lost.
- `support/original_c4a_series/` — original package helper files preserved for reference.

## Notes

- Overlapping topics were grouped with sub-numbering like `05.1`, `05.2`, and `05.3`.
- A few copied lessons had imports normalized to use the local `common.io` helper package.
- The original project root `.env` file is still the one used for API-key-based demos.

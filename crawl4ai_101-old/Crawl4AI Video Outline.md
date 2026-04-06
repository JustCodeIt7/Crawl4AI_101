# Crawl4AI YouTube tutorial series: 24 videos from zero to production

**Crawl4AI is the #1 open-source, LLM-friendly web crawler on GitHub, purpose-built for AI agents, RAG pipelines, and large-scale data extraction.** This 24-video tutorial series covers the full breadth of its capabilities — from a first 5-line crawl to production-grade Docker deployments with crash recovery. Every video stays under 10 minutes, keeps code under 200 lines, and focuses exclusively on hands-on coding. The series is organized into four progressive modules: Foundations, Extraction Mastery, Dynamic Web Handling, and Production & Scale.

The outline below maps directly to Crawl4AI v0.8.x documentation and API surface. Each video builds on concepts from previous videos, creating a coherent learning path that takes viewers from their first `arun()` call to orchestrating thousands of concurrent crawls with intelligent dispatching.

---

## Module 1 — Foundations (Videos 1–6)

These six videos establish the architectural mental model every Crawl4AI user needs: the three-config pattern (`BrowserConfig` → `CrawlerRunConfig` → `CrawlResult`), the async-first design, and the content pipeline from raw HTML to clean, AI-ready markdown.

---

### Video 1: Your first crawl in 5 lines of Python

**Description:** Viewers write their first async crawl, inspect the `CrawlResult` object, and print clean markdown. This video establishes the foundational pattern — `async with AsyncWebCrawler() as crawler` — that every subsequent video builds on.

**Key concepts covered:**
- `AsyncWebCrawler` as the core class
- The `arun(url, config)` method
- `CrawlResult` fields: `success`, `markdown`, `html`, `cleaned_html`, `status_code`
- Python `asyncio.run()` entry point

**Sample code demonstrated:**
- Minimal 5-line crawl of `https://example.com`, printing `result.markdown[:500]`
- Checking `result.success` and `result.error_message` for error handling
- Accessing `result.html` vs `result.cleaned_html` vs `result.markdown`

**Estimated duration:** 6 minutes

---

### Video 2: BrowserConfig — controlling your headless browser

**Description:** Deep dive into `BrowserConfig`, the class that controls how the browser launches. Viewers learn to switch browser engines, set viewport sizes, configure user agents, and toggle headless mode for visual debugging.

**Key concepts covered:**
- `browser_type`: `"chromium"`, `"firefox"`, `"webkit"`
- `headless=True/False` for debugging
- `viewport_width`, `viewport_height` for responsive content
- `user_agent` and `user_agent_mode="random"`
- `java_script_enabled`, `text_mode`, `light_mode` for performance
- `verbose=True` for debug logging

**Sample code demonstrated:**
- Creating a `BrowserConfig` with Firefox in non-headless mode
- Crawling a responsive site at different viewport sizes and comparing markdown output
- Enabling `text_mode=True` for speed benchmarking (no images loaded)

**Estimated duration:** 7 minutes

---

### Video 3: CrawlerRunConfig — tuning every crawl

**Description:** Walks through the most important `CrawlerRunConfig` parameters that shape each individual crawl. Viewers learn content filtering, tag exclusion, cache control, and wait conditions — the settings they'll use on every project.

**Key concepts covered:**
- `word_count_threshold` — minimum words per content block
- `excluded_tags` — removing `nav`, `footer`, `header`
- `exclude_external_links`, `exclude_social_media_links`, `exclude_domains`
- `remove_overlay_elements` — auto-remove popups/modals
- `process_iframes` — merge iframe content
- `cache_mode`: `CacheMode.ENABLED`, `BYPASS`, `WRITE_ONLY`, `READ_ONLY`
- `wait_for` — CSS selector or JS condition before capture
- `page_timeout` — maximum wait time
- The `clone()` method for config variations

**Sample code demonstrated:**
- Crawling a news site with `excluded_tags=["nav", "footer"]` and `word_count_threshold=15`
- Comparing cached vs. bypassed crawl results
- Using `wait_for="css:.main-content"` on a slow-loading site
- Creating config variants with `base_config.clone(cache_mode=CacheMode.BYPASS)`

**Estimated duration:** 8 minutes

---

### Video 4: Content selection with `css_selector` and `target_elements`

**Description:** Compares the two CSS-based content scoping mechanisms. `css_selector` narrows everything (HTML, links, media) to one element. `target_elements` focuses markdown on multiple elements while preserving full-page context for link and media extraction.

**Key concepts covered:**
- `css_selector` — basic single-element scoping for all extraction
- `target_elements` — multi-element targeting with preserved page context
- `flatten_shadow_dom=True` — accessing web component content
- `delay_before_return_html` — waiting for hydration
- When to use which approach (full scoping vs. markdown focus)

**Sample code demonstrated:**
- Crawling a blog with `css_selector="article.main-content"` and showing scoped output
- Using `target_elements=["article.main-content", "aside.sidebar"]` and comparing how links/media differ
- Crawling a web-component-heavy site with `flatten_shadow_dom=True`

**Estimated duration:** 7 minutes

---

### Video 5: Markdown generation and content filters

**Description:** Explores `DefaultMarkdownGenerator` with its three content filters. Viewers learn the difference between `raw_markdown` and `fit_markdown`, and when to use pruning (no query), BM25 (with a query), or LLM-based filtering.

**Key concepts covered:**
- `DefaultMarkdownGenerator` with `options` dict (e.g., `ignore_links`, `citations`, `body_width`)
- `PruningContentFilter` — heuristic noise removal (threshold, threshold_type, min_word_threshold)
- `BM25ContentFilter` — query-based relevance ranking (user_query, bm25_threshold)
- `LLMContentFilter` — AI-powered content filtering
- `result.markdown.raw_markdown` vs `result.markdown.fit_markdown`
- `result.markdown.markdown_with_citations` and `result.markdown.references_markdown`

**Sample code demonstrated:**
- Crawling a cluttered news page with `PruningContentFilter(threshold=0.48, threshold_type="dynamic")`
- Same page with `BM25ContentFilter(user_query="climate policy", bm25_threshold=1.2)`
- Comparing raw vs. fit markdown side-by-side
- Enabling citations with `options={"citations": True}`

**Estimated duration:** 8 minutes

---

### Video 6: Understanding CrawlResult — every field explained

**Description:** A practical tour of every field in the `CrawlResult` object. Viewers build a utility function that inspects and saves all output types — markdown, HTML, screenshots, PDFs, media, links, and metadata.

**Key concepts covered:**
- Full `CrawlResult` model: `url`, `html`, `cleaned_html`, `fit_html`, `markdown`, `extracted_content`
- `media` dict: `images`, `videos`, `audios` with scoring metadata
- `links` dict: `internal` vs. `external` with `href`, `text`
- `screenshot` (base64 PNG), `pdf` (bytes), `mhtml` (full page archive)
- `metadata`, `response_headers`, `ssl_certificate`, `status_code`
- `downloaded_files`, `js_execution_result`

**Sample code demonstrated:**
- Crawling Wikipedia with `screenshot=True, pdf=True, capture_mhtml=True`
- Writing a `save_result()` helper that saves screenshot as PNG, PDF to file, and markdown to `.md`
- Iterating `result.media["images"]` and filtering by `score > 5`
- Listing all internal vs. external links

**Estimated duration:** 8 minutes

---

## Module 2 — Extraction mastery (Videos 7–12)

This module covers every extraction strategy in Crawl4AI — from zero-cost CSS/XPath/regex approaches to LLM-powered semantic extraction. Viewers learn to pick the right strategy for each use case and combine them.

---

### Video 7: JsonCssExtractionStrategy — structured data without LLMs

**Description:** The workhorse of Crawl4AI extraction. Viewers learn to define schemas with `baseSelector` and `fields`, handle text, attributes, HTML, regex field types, and use nested fields for hierarchical data.

**Key concepts covered:**
- Schema structure: `name`, `baseSelector`, `fields`
- Field types: `text`, `attribute`, `html`, `regex`, `nested`
- `transform` options: `lowercase`, `uppercase`, `strip`
- `default` values for missing data
- `result.extracted_content` as JSON string

**Sample code demonstrated:**
- Extracting Hacker News stories: title, URL, score from `tr.athing` elements
- Nested extraction: product cards with `name`, `price`, and nested `reviews` containing `author` and `rating`
- Using `type="attribute"` for `href` and `src` extraction
- Parsing `result.extracted_content` with `json.loads()`

**Estimated duration:** 8 minutes

---

### Video 8: Auto-generating schemas with LLMs (one-time cost)

**Description:** Instead of manually writing CSS selectors, use `JsonCssExtractionStrategy.generate_schema()` to have an LLM create the schema for you. This is a one-time cost that produces a reusable, LLM-free schema for fast repeated extractions.

**Key concepts covered:**
- `JsonCssExtractionStrategy.generate_schema(html, llm_config=LLMConfig(...))`
- `JsonXPathExtractionStrategy.generate_schema()` — same for XPath
- `LLMConfig` for provider setup (OpenAI, Ollama, Gemini)
- Saving generated schemas to JSON for reuse
- One-time LLM cost vs. repeated free extractions

**Sample code demonstrated:**
- Fetching a product page, then calling `generate_schema()` with GPT-4o-mini
- Same with `ollama/llama3.3` for a free local alternative
- Saving the schema to `product_schema.json` and loading it for subsequent crawls
- Running the generated schema on 10 product pages (zero LLM cost)

**Estimated duration:** 7 minutes

---

### Video 9: JsonXPathExtractionStrategy and RegexExtractionStrategy

**Description:** Covers the two other LLM-free strategies. XPath for complex HTML traversal and Regex for pattern matching (emails, phones, prices, URLs). Viewers learn built-in regex patterns and custom pattern creation.

**Key concepts covered:**
- `JsonXPathExtractionStrategy` — when XPath beats CSS (sibling navigation, text predicates)
- `RegexExtractionStrategy` — bit flag patterns (`Email | PhoneUS | Url`)
- Built-in patterns: `Email`, `Url`, `Currency`, `DateIso`, `IPv4`, `CreditCard`, etc.
- Custom patterns: `custom={"usd_price": r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?"}`
- `generate_pattern()` with LLM assistance for complex regex
- `input_format`: `"html"`, `"markdown"`, `"fit_html"`

**Sample code demonstrated:**
- XPath extraction of a table with sibling-based relationships
- Using `RegexExtractionStrategy(pattern=RegexExtractionStrategy.Email | RegexExtractionStrategy.Url)` on a contact page
- Custom price regex extraction from an e-commerce listing
- Combining CSS extraction first, then regex on specific fields (hybrid approach)

**Estimated duration:** 8 minutes

---

### Video 10: LLMExtractionStrategy — AI-powered data extraction

**Description:** For semantically complex or unstructured content, `LLMExtractionStrategy` uses any LLM via LiteLLM. Viewers learn schema-based extraction with Pydantic models, chunking for long documents, and token usage monitoring.

**Key concepts covered:**
- `LLMExtractionStrategy` with `LLMConfig` (provider-agnostic via LiteLLM)
- `extraction_type`: `"block"` (freeform) vs. `"schema"` (Pydantic)
- `input_format`: `"markdown"`, `"html"`, `"fit_markdown"`
- Chunking: `chunk_token_threshold`, `overlap_rate`, `apply_chunking`
- `extra_args`: `temperature`, `max_tokens`, `top_p`
- `show_usage()` for token cost tracking

**Sample code demonstrated:**
- Defining a Pydantic `Product` model and extracting products from an unstructured page
- Using `instruction` to guide extraction ("Extract all product names, prices, and descriptions")
- Comparing `input_format="markdown"` vs `"fit_markdown"` for cost savings
- Calling `strategy.show_usage()` to print token consumption

**Estimated duration:** 9 minutes

---

### Video 11: Building knowledge graphs with LLM extraction

**Description:** A practical project combining Pydantic models for entities and relationships to build a knowledge graph from a Wikipedia article. Demonstrates advanced schema design and multi-model extraction patterns.

**Key concepts covered:**
- Pydantic schemas for `Entity`, `Relationship`, `KnowledgeGraph`
- Complex `instruction` prompts for relationship extraction
- Handling multi-chunk results for long articles
- Serializing knowledge graphs to JSON
- When LLM extraction is worth the cost vs. simpler approaches

**Sample code demonstrated:**
- Defining `Entity(name, description)`, `Relationship(entity1, entity2, description, relation_type)`, `KnowledgeGraph(entities, relationships)`
- Crawling a Wikipedia article with `LLMExtractionStrategy(schema=KnowledgeGraph.model_json_schema())`
- Parsing and printing the entity-relationship graph
- Adjusting `chunk_token_threshold` for long articles

**Estimated duration:** 9 minutes

---

### Video 12: Choosing and combining extraction strategies

**Description:** A decision-framework video. Viewers learn when to use CSS vs. XPath vs. Regex vs. LLM vs. Cosine strategies, and how to combine them in multi-pass pipelines for maximum accuracy at minimum cost.

**Key concepts covered:**
- Decision tree: structured HTML → CSS/XPath; common patterns → Regex; unstructured → LLM; topic similarity → Cosine
- Multi-pass extraction: CSS first for structure, then regex for specific fields, then LLM for analysis
- `CosineStrategy` for semantic clustering (with `sentence-transformers`)
- Cost-performance tradeoffs across strategies
- Chunking strategies: `RegexChunking`, `SlidingWindowChunking`, `OverlappingWindowChunking`

**Sample code demonstrated:**
- Pipeline: `JsonCssExtractionStrategy` → extract product descriptions → `RegexExtractionStrategy` for dimensions/weights
- Configuring `CosineStrategy(semantic_filter="machine learning", top_k=3)`
- Setting up `OverlappingWindowChunking(window_size=500, overlap=50)` for long-document LLM extraction
- Benchmark: comparing speed/cost of CSS vs. LLM on the same page

**Estimated duration:** 8 minutes

---

## Module 3 — Dynamic web handling (Videos 13–18)

Modern websites are interactive: they load content via JavaScript, paginate with "Load More" buttons, use infinite scroll, and require authentication. This module covers every tool Crawl4AI provides for dynamic content.

---

### Video 13: JavaScript execution and wait conditions

**Description:** Master `js_code` for scrolling, clicking, and form filling. Learn `wait_for` conditions (CSS selectors and JS expressions) that ensure content is fully loaded before capture.

**Key concepts covered:**
- `js_code` — single string or list of JS snippets (runs after `wait_for`)
- `js_code_before_wait` — JS that runs before `wait_for` (triggers loading)
- `wait_for="css:.loaded-block"` — CSS selector wait
- `wait_for="js:() => document.querySelectorAll('.item').length > 10"` — JS expression wait
- `delay_before_return_html` — additional pause
- `scan_full_page=True` with `scroll_delay` for lazy loading

**Sample code demonstrated:**
- Scrolling to page bottom and clicking "Load More" on Hacker News
- Using `wait_for="css:.dynamic-content"` after triggering AJAX load
- Multi-step JS: scroll → click tab → wait → extract
- `scan_full_page=True` with `scroll_delay=0.5` for lazy-loaded images

**Estimated duration:** 8 minutes

---

### Video 14: Virtual scrolling — capturing Twitter, Instagram, and data tables

**Description:** Virtual scroll sites replace DOM content as you scroll (unlike infinite scroll which appends). `VirtualScrollConfig` handles this by capturing content incrementally. Viewers crawl a virtual-scrolling feed.

**Key concepts covered:**
- Virtual scroll vs. infinite scroll (content replaced vs. appended)
- `VirtualScrollConfig`: `container_selector`, `scroll_count`, `scroll_by`, `wait_after_scroll`
- `scroll_by` options: `"container_height"`, `"page_height"`, or pixel value
- When to use `virtual_scroll_config` vs. `scan_full_page`
- Combining virtual scroll with extraction strategies

**Sample code demonstrated:**
- Configuring `VirtualScrollConfig` for a social media feed-style page
- Fast scrolling config (`scroll_by=500, wait_after_scroll=0.1`) vs. careful config (`scroll_by="container_height", wait_after_scroll=1.5`)
- Combining virtual scroll with `JsonCssExtractionStrategy` to extract structured feed data
- Counting total items captured across all scroll iterations

**Estimated duration:** 8 minutes

---

### Video 15: Session management for multi-page workflows

**Description:** Reuse the same browser tab across multiple `arun()` calls with `session_id`. Perfect for paginated content, multi-step forms, and authenticated sequences where you need to preserve state.

**Key concepts covered:**
- `session_id` — identifies and reuses a browser tab
- `js_only=True` — skip full page reload on subsequent calls
- Sequential workflow pattern: initial load → JS click → re-extract
- `crawler.crawler_strategy.kill_session(session_id)` — cleanup
- Session vs. identity-based crawling (when to use each)

**Sample code demonstrated:**
- Paginating through GitHub commits: first `arun()` loads the page, subsequent calls click "Next" with `js_only=True`
- JS that clicks next page and waits for content change before returning
- Extracting items from each page, accumulating results
- Proper session cleanup with `kill_session()`

**Estimated duration:** 8 minutes

---

### Video 16: Hooks and authentication — 8 lifecycle injection points

**Description:** Crawl4AI's hook system lets you inject async functions at 8 points in the crawl pipeline. Viewers implement login flows, resource blocking, and custom header injection using hooks.

**Key concepts covered:**
- 8 hooks in order: `on_browser_created`, `on_page_context_created`, `before_goto`, `after_goto`, `on_user_agent_updated`, `on_execution_started`, `before_retrieve_html`, `before_return_html`
- `crawler.crawler_strategy.set_hook("hook_name", async_func)`
- Hook functions receive `page` (Playwright Page), `context`, and `**kwargs`
- Best hook for auth: `on_page_context_created`
- Route filtering: blocking images, ads, analytics scripts

**Sample code demonstrated:**
- Login hook: navigating to login page, filling credentials, clicking submit in `on_page_context_created`
- Resource blocking: `context.route("**/*.{png,jpg}", lambda route: route.abort())` to speed up crawls
- Custom header injection in `before_goto`
- Lazy-load trigger in `before_retrieve_html` (scroll to bottom)

**Estimated duration:** 9 minutes

---

### Video 17: Identity-based crawling and magic mode

**Description:** Two approaches to appearing as a real human. Managed browsers create persistent profiles with saved cookies/logins. Magic mode is a quick-start flag for basic bot evasion. Viewers also learn locale, timezone, and geolocation spoofing.

**Key concepts covered:**
- `BrowserConfig(use_managed_browser=True, user_data_dir="...")` — persistent profiles
- Manual profile setup: launching Playwright Chromium, logging in, saving profile
- `BrowserProfiler` class for profile management
- `CrawlerRunConfig(magic=True)` — simplified automation mode
- `locale="fr-FR"`, `timezone_id="Europe/Paris"` — regional spoofing
- Managed browsers vs. magic mode: when to use each

**Sample code demonstrated:**
- Setting up a persistent browser profile directory and crawling an authenticated page
- Using `magic=True` with `remove_overlay_elements=True` for quick bot evasion
- Crawling with `locale="de-DE"` and `timezone_id="Europe/Berlin"` for geo-targeted content
- Comparing authenticated vs. anonymous crawl results

**Estimated duration:** 8 minutes

---

### Video 18: Proxy rotation and anti-bot stealth

**Description:** Covers proxy configuration, stealth mode, and undetected browser mode for bypassing Cloudflare, DataDome, and other bot detection systems. Viewers set up proxy rotation and combine it with fingerprint masking.

**Key concepts covered:**
- `BrowserConfig(proxy_config={"server": "...", "username": "...", "password": "..."})` 
- `ProxyConfig.from_string()` for multiple proxy formats (HTTP, SOCKS5, IP:port)
- `BrowserConfig(enable_stealth=True)` — playwright-stealth fingerprint masking
- `BrowserConfig(browser_type="undetected")` — undetected Chrome for sophisticated detection
- `extra_args=["--disable-blink-features=AutomationControlled"]`
- `CrawlerRunConfig(simulate_user=True)` — human-like behavior simulation
- Combining proxy + stealth + identity for maximum evasion

**Sample code demonstrated:**
- Basic proxy crawl checking IP at whatismyip.com
- Enabling stealth mode with `enable_stealth=True`
- Using `browser_type="undetected"` for Cloudflare-protected sites
- Combined config: proxy + stealth + simulate_user

**Estimated duration:** 7 minutes

---

## Module 4 — Production and scale (Videos 19–24)

This final module covers everything needed for production deployments: deep crawling entire sites, concurrent multi-URL crawling with intelligent dispatching, Docker deployment, API usage, and real-world project patterns.

---

### Video 19: Deep crawling with BFS, DFS, and BestFirst strategies

**Description:** Crawl entire websites beyond a single page. Viewers implement BFS (breadth-first), DFS (depth-first), and BestFirst (scorer-prioritized) strategies with filters and URL scorers for precision targeting.

**Key concepts covered:**
- `BFSDeepCrawlStrategy(max_depth, include_external, max_pages, score_threshold)`
- `DFSDeepCrawlStrategy` — depth-first exploration
- `BestFirstCrawlingStrategy` with `KeywordRelevanceScorer`
- `FilterChain` combining `URLPatternFilter`, `DomainFilter`, `ContentRelevanceFilter`, `SEOFilter`
- Streaming mode: `stream=True` with `async for result in await crawler.arun(...)`
- Crash recovery: `resume_state` and `on_state_change` callbacks
- `prefetch=True` for 5-10× faster URL discovery

**Sample code demonstrated:**
- BFS crawl of documentation site: `max_depth=2, max_pages=50`
- Adding `FilterChain([URLPatternFilter(patterns=["*docs*", "*guide*"])])` 
- BestFirst with `KeywordRelevanceScorer(keywords=["API", "reference"], weight=0.7)`
- Streaming deep crawl with real-time result processing

**Estimated duration:** 9 minutes

---

### Video 20: Multi-URL crawling with intelligent dispatchers

**Description:** Scale to hundreds or thousands of URLs with `arun_many()`. Learn `MemoryAdaptiveDispatcher` for resource-aware concurrency, `RateLimiter` for respectful crawling, and URL-specific configs for mixed workloads.

**Key concepts covered:**
- `arun_many(urls, config, dispatcher)` — concurrent crawling
- `MemoryAdaptiveDispatcher`: `memory_threshold_percent`, `max_session_permit`, `check_interval`
- `SemaphoreDispatcher` — fixed concurrency limit
- `RateLimiter`: `base_delay`, `max_delay`, `max_retries`, `rate_limit_codes`
- `CrawlerMonitor` with `DisplayMode.DETAILED` / `AGGREGATED`
- URL-specific configs with `url_matcher` patterns and `MatchMode`
- `DispatchResult` with memory and timing stats
- Streaming mode for real-time result processing

**Sample code demonstrated:**
- Crawling 50 URLs with `MemoryAdaptiveDispatcher(memory_threshold_percent=80, max_session_permit=10)`
- Adding `RateLimiter(base_delay=(1.0, 2.0), max_retries=3)`
- URL-specific configs: blog pages get `PruningContentFilter`, product pages get `JsonCssExtractionStrategy`, PDFs get `PDFContentScrapingStrategy`
- Streaming results with progress monitoring

**Estimated duration:** 9 minutes

---

### Video 21: Docker deployment and the REST API

**Description:** Deploy Crawl4AI as a Docker service with FastAPI, Redis job queue, and a monitoring dashboard. Viewers learn key API endpoints, hook injection, and the Python SDK for remote crawling.

**Key concepts covered:**
- `docker pull unclecode/crawl4ai:latest` and `docker run -p 11235:11235 --shm-size=1g`
- Docker Compose setup with environment files for LLM keys
- Key endpoints: `POST /crawl`, `POST /crawl/stream`, `POST /crawl/job`
- `/playground` — interactive web UI for testing
- `/dashboard` — real-time monitoring
- Hooks API: string-based (REST) and function-based (Python SDK)
- Security: hooks disabled by default, JWT authentication
- MCP (Model Context Protocol) support for AI assistants

**Sample code demonstrated:**
- Docker run command with `.llm.env` for API keys
- Python `requests.post("http://localhost:11235/crawl", json={...})` with extraction config
- Streaming endpoint consumption
- Using hooks via the REST API (string-based hook code)

**Estimated duration:** 8 minutes

---

### Video 22: HTTP-only crawling and the CLI

**Description:** Not every page needs a full browser. `AsyncHTTPCrawlerStrategy` bypasses Playwright entirely for 10× faster static page crawling. Also covers the `crwl` CLI for quick command-line operations and YAML configs.

**Key concepts covered:**
- `AsyncHTTPCrawlerStrategy` — no browser, pure HTTP, much faster
- `HTTPCrawlerConfig` for HTTP-specific settings
- When to use HTTP-only vs. browser-based (static vs. dynamic content)
- `crwl` CLI: basic usage, output formats (`markdown`, `json`, `markdown-fit`)
- YAML config files for browser, crawler, extraction, and filter settings
- CLI LLM Q&A: `crwl https://example.com -q "What is the main topic?"`
- Deep crawl via CLI: `crwl https://docs.crawl4ai.com --deep-crawl bfs --max-pages 10`

**Sample code demonstrated:**
- HTTP-only crawl with `AsyncHTTPCrawlerStrategy` and `JsonCssExtractionStrategy`
- Comparing speed: HTTP-only vs. Playwright on a static page
- CLI examples: `crwl` with YAML browser config, CSS extraction schema, and BM25 filter
- Interactive Q&A session via CLI

**Estimated duration:** 8 minutes

---

### Video 23: File downloads, screenshots, PDFs, and SSL inspection

**Description:** A practical toolkit video covering media capture and file handling. Viewers download files triggered by JavaScript clicks, capture full-page screenshots, generate PDFs, and inspect SSL certificates programmatically.

**Key concepts covered:**
- `BrowserConfig(accept_downloads=True, downloads_path="...")` — enable file downloads
- JS-triggered downloads with `js_code` click simulation
- `result.downloaded_files` — paths to downloaded files
- `CrawlerRunConfig(screenshot=True, pdf=True, capture_mhtml=True)`
- `screenshot_wait_for` — delay before capture
- `fetch_ssl_certificate=True` and `result.ssl_certificate`
- MHTML snapshots for complete page archiving

**Sample code demonstrated:**
- Clicking a download button via `js_code` and retrieving `result.downloaded_files`
- Full-page screenshot with `scan_full_page=True` and saving as PNG
- PDF generation and save
- SSL certificate inspection: printing issuer, expiry, and certificate chain
- MHTML capture for offline page archiving

**Estimated duration:** 7 minutes

---

### Video 24: Real-world project — building an AI-ready data pipeline

**Description:** The capstone video ties everything together. Viewers build a complete pipeline that deep-crawls a documentation site, extracts structured data, generates AI-ready markdown with citations, handles errors, and exports results — using techniques from every prior video.

**Key concepts covered:**
- End-to-end pipeline design: discover → crawl → extract → filter → export
- Combining deep crawl (BFS) with extraction strategies per page type
- Using `url_matcher` for route-specific extraction configs
- Content filtering pipeline: `PruningContentFilter` → `BM25ContentFilter`
- Error handling, retry logic, and `check_robots_txt=True`
- Exporting structured JSON + clean markdown for RAG ingestion
- Performance optimization: `text_mode`, `light_mode`, cache warming

**Sample code demonstrated:**
- BFS deep crawl of a docs site with `max_depth=2, max_pages=100`
- URL-specific configs: API reference pages get `JsonCssExtractionStrategy`; tutorial pages get `BM25ContentFilter` with query
- Memory-adaptive dispatcher with rate limiting for respectful crawling
- Saving results: JSON structured data to file, markdown to directory
- Final stats: pages crawled, data extracted, time elapsed

**Estimated duration:** 9 minutes

---

## Series summary at a glance

| Module | Videos | Focus | Complexity |
|---|---|---|---|
| **Foundations** | 1–6 | Core architecture, config, markdown, content pipeline | Beginner |
| **Extraction mastery** | 7–12 | CSS, XPath, Regex, LLM, knowledge graphs, strategy selection | Intermediate |
| **Dynamic web handling** | 13–18 | JS execution, virtual scroll, sessions, hooks, auth, anti-bot | Intermediate–Advanced |
| **Production & scale** | 19–24 | Deep crawling, multi-URL dispatch, Docker, CLI, real-world projects | Advanced |

**Total: 24 videos × ~8 min average = ~192 minutes of focused, code-driven content** covering the complete Crawl4AI API surface. Each video is self-contained enough to watch independently, yet the progressive structure rewards sequential viewing. Every code sample stays under 200 lines, uses real-world target sites, and runs as a standalone async Python script.
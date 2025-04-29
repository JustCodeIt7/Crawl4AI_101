# Commented out IPython magic to ensure Python compatibility.
# %%capture

import asyncio
import nest_asyncio
nest_asyncio.apply()

import asyncio
from playwright.async_api import async_playwright, Page, BrowserContext

async def test_browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://example.com')
        print(f'Title: {await page.title()}')
        await browser.close()

asyncio.run(test_browser())

#%% #### 2. **Basic Setup and Simple Crawl**
import asyncio
import nest_asyncio
nest_asyncio.apply()

from crawl4ai import AsyncWebCrawler, CacheMode, BrowserConfig, CrawlerRunConfig, CacheMode

async def simple_crawl():
    crawler_run_config = CrawlerRunConfig( cache_mode=CacheMode.BYPASS)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.kidocode.com/degrees/technology",
            config=crawler_run_config
        )
        print(result.markdown.raw_markdown[:500].replace("\n", " -- "))  # Print the first 500 characters

asyncio.run(simple_crawl())

#%% #### 3. **Dynamic Content Handling**
async def crawl_dynamic_content():
    # wait_for = """() => {
    #     return Array.from(document.querySelectorAll('article.tease-card')).length > 10;
    # }"""

    # wait_for can be also just a css selector
    # wait_for = "article.tease-card:nth-child(10)"

    async with AsyncWebCrawler() as crawler:
        js_code = [
            "const loadMoreButton = Array.from(document.querySelectorAll('button')).find(button => button.textContent.includes('Load More')); loadMoreButton && loadMoreButton.click();"
        ]
        config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            js_code=js_code,
            # wait_for=wait_for,
        )
        result = await crawler.arun(
            url="https://www.nbcnews.com/business",
            config=config,

        )
        print(result.markdown.raw_markdown[:500].replace("\n", " -- "))  # Print first 500 characters

asyncio.run(crawl_dynamic_content())

#%% #### 4. **Content Cleaning and Fit Markdown**
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def clean_content():
    async with AsyncWebCrawler(verbose=True) as crawler:
        config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            excluded_tags=['nav', 'footer', 'aside'],
            remove_overlay_elements=True,
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(threshold=0.48, threshold_type="fixed", min_word_threshold=0),
                options={
                    "ignore_links": True
                }
            ),
        )
        result = await crawler.arun(
            url="https://en.wikipedia.org/wiki/Apple",
            config=config,
        )
        full_markdown_length = len(result.markdown.raw_markdown)
        fit_markdown_length = len(result.markdown.fit_markdown)
        print(f"Full Markdown Length: {full_markdown_length}")
        print(f"Fit Markdown Length: {fit_markdown_length}")


asyncio.run(clean_content())

#%% #### 5. **Link Analysis and Smart Filtering**
async def link_analysis():
    async with AsyncWebCrawler() as crawler:
        config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            exclude_external_links=True,
            exclude_social_media_links=True,
            # exclude_domains=["facebook.com", "twitter.com"]
        )
        result = await crawler.arun(
            url="https://www.nbcnews.com/business",
            config=config,
        )
        print(f"Found {len(result.links['internal'])} internal links")
        print(f"Found {len(result.links['external'])} external links")

        for link in result.links['internal'][:5]:
            print(f"Href: {link['href']}\nText: {link['text']}\n")


asyncio.run(link_analysis())

#%% #### 6. **Media Handling**
async def media_handling():
    async with AsyncWebCrawler() as crawler:
        config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            exclude_external_images=False,
            # screenshot=True # Set this to True if you want to take a screenshot
        )
        result = await crawler.arun(
            url="https://www.nbcnews.com/business",
            config=config,
        )
        for img in result.media['images'][:5]:
            print(f"Image URL: {img['src']}, Alt: {img['alt']}, Score: {img['score']}")

asyncio.run(media_handling())

#%% #### 7. **Using Hooks for Custom Workflow**


async def before_goto(page: Page, context: BrowserContext, url: str, **kwargs):
        # Hook called before navigating to each URL
        print(f"[HOOK] before_goto - About to visit: {url}")
        # Example: Add custom headers for the request
        await page.set_extra_http_headers({
            "Custom-Header": "my-value"
        })
        return page

async def custom_hook_workflow(verbose=True):
    async with AsyncWebCrawler(config=BrowserConfig( verbose=verbose)) as crawler:
        # Set a 'before_goto' hook to run custom code just before navigation
        crawler.crawler_strategy.set_hook("before_goto", before_goto)

        # Perform the crawl operation
        result = await crawler.arun(
            url="https://crawl4ai.com",
            config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
        )
        print(result.markdown.raw_markdown[:500].replace("\n", " -- "))

asyncio.run(custom_hook_workflow())

#%% #### 8. **Session-Based Crawling**


from crawl4ai.extraction_strategy import (
    JsonCssExtractionStrategy,
    LLMExtractionStrategy,
)
import json

async def crawl_dynamic_content_pages_method_2():
    print("\n--- Advanced Multi-Page Crawling with JavaScript Execution ---")

    async with AsyncWebCrawler() as crawler:
        url = "https://github.com/microsoft/TypeScript/commits/main"
        session_id = "typescript_commits_session"
        all_commits = []
        last_commit = ""

        js_next_page_and_wait = """
        (async () => {
            const getCurrentCommit = () => {
                const commits = document.querySelectorAll('li.Box-sc-g0xbh4-0 h4');
                return commits.length > 0 ? commits[0].textContent.trim() : null;
            };

            const initialCommit = getCurrentCommit();
            const button = document.querySelector('a[data-testid="pagination-next-button"]');
            if (button) button.click();

            // Poll for changes
            while (true) {
                await new Promise(resolve => setTimeout(resolve, 100)); // Wait 100ms
                const newCommit = getCurrentCommit();
                if (newCommit && newCommit !== initialCommit) {
                    break;
                }
            }
        })();
        """

        schema = {
            "name": "Commit Extractor",
            "baseSelector": "li.Box-sc-g0xbh4-0",
            "fields": [
                {
                    "name": "title",
                    "selector": "h4.markdown-title",
                    "type": "text",
                    "transform": "strip",
                },
            ],
        }
        extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)

        for page in range(2):  # Crawl 2 pages
            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                session_id=session_id,
                css_selector="li.Box-sc-g0xbh4-0",
                extraction_strategy=extraction_strategy,
                js_code=js_next_page_and_wait if page > 0 else None,
                js_only=page > 0,
            )
            result = await crawler.arun(
                url=url,
                config=config
            )

            assert result.success, f"Failed to crawl page {page + 1}"

            commits = json.loads(result.extracted_content)
            all_commits.extend(commits)

            print(f"Page {page + 1}: Found {len(commits)} commits")

        await crawler.crawler_strategy.kill_session(session_id)
        print(f"Successfully crawled {len(all_commits)} commits across 3 pages")

asyncio.run(crawl_dynamic_content_pages_method_2())

#%% #### 9. **Using Extraction Strategies**

#%% ##### Executing JavaScript & Extract Structured Data without LLMs
from crawl4ai.extraction_strategy import (
    JsonCssExtractionStrategy,
    LLMExtractionStrategy,
)
import json
async def extract():
    schema = {
        "name": "KidoCode Courses",
        "baseSelector": "section.charge-methodology .div-block-214.p-extraxx",
        "fields": [
            {
                "name": "section_title",
                "selector": "h3.heading-50",
                "type": "text",
            },
            {
                "name": "section_description",
                "selector": ".charge-content",
                "type": "text",
            },
            {
                "name": "course_name",
                "selector": ".text-block-93",
                "type": "text",
            },
            {
                "name": "course_description",
                "selector": ".course-content-text",
                "type": "text",
            },
            {
                "name": "course_icon",
                "selector": ".image-92",
                "type": "attribute",
                "attribute": "src"
            }
        ]
    }

    extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)

    async with AsyncWebCrawler() as crawler:

        # Create the JavaScript that handles clicking multiple times
        js_click_tabs = """
        (async () => {
            const tabs = document.querySelectorAll("section.charge-methodology .tabs-menu-3 > div");

            for(let tab of tabs) {
                // scroll to the tab
                tab.scrollIntoView();
                tab.click();
                // Wait for content to load and animations to complete
                await new Promise(r => setTimeout(r, 500));
            }
        })();
        """

        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=extraction_strategy,
            js_code=[js_click_tabs],
        )
        result = await crawler.arun(
            url="https://www.kidocode.com/degrees/technology",
            config=config
        )

        courses = json.loads(result.extracted_content)
        print(result.extracted_content)
        print(f"Successfully extracted {len(courses)} courses")
        print(len(result.markdown))
        # print(json.dumps(courses[0], indent=2))

await extract()

#%% #####  LLM Extraction
# This example demonstrates how to use language model-based extraction to retrieve
# structured data from a pricing page on OpenAI’s site.

from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai import LLMConfig  # Corrected import path
from pydantic import BaseModel, Field
import os, json

class OpenAIModelFee(BaseModel):
    model_name: str = Field(..., description="Name of the OpenAI model.")
    input_fee: str = Field(..., description="Fee for input token for the OpenAI model.")
    output_fee: str = Field(
        ..., description="Fee for output token for the OpenAI model."
    )

async def extract_structured_data_using_llm(provider: str, api_token: str = None, extra_headers: dict = None):
    print(f"\n--- Extracting Structured Data with {provider} ---")

    # Skip if API token is missing (for providers that require it)
    if api_token is None and provider != "ollama":
        print(f"API token is required for {provider}. Skipping this example.")
        return

    extra_args = {"extra_headers": extra_headers} if extra_headers else {}

    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url="https://openai.com/api/pricing/",
            word_count_threshold=1,
            extraction_strategy=LLMExtractionStrategy(
                llm_config=LLMConfig(provider=provider, api_token=api_token),
                schema=OpenAIModelFee.schema(),
                extraction_type="schema",
                instruction="""Extract all model names along with fees for input and output tokens."
                "{model_name: 'GPT-4', input_fee: 'US$10.00 / 1M tokens', output_fee: 'US$30.00 / 1M tokens'}.""",
                **extra_args
            ),
            cache_mode = CacheMode.ENABLED
        )
        print(json.loads(result.extracted_content)[:5])

await extract_structured_data_using_llm("openai/gpt-4o-mini", os.getenv("OPENAI_API_KEY"))

#%% **Cosine Similarity Strategy**


from crawl4ai.extraction_strategy import CosineStrategy

async def cosine_similarity_extraction():
    async with AsyncWebCrawler() as crawler:
        strategy = CosineStrategy(
            word_count_threshold=10,
            max_dist=0.2, # Maximum distance between two words
            linkage_method="ward", # Linkage method for hierarchical clustering (ward, complete, average, single)
            top_k=3, # Number of top keywords to extract
            sim_threshold=0.3, # Similarity threshold for clustering
            semantic_filter="McDonald's economic impact, American consumer trends", # Keywords to filter the content semantically using embeddings
            verbose=True
        )

        result = await crawler.arun(
            url="https://www.nbcnews.com/business/consumer/how-mcdonalds-e-coli-crisis-inflation-politics-reflect-american-story-rcna177156",
            extraction_strategy=strategy,
            cache_mode = CacheMode.ENABLED
        )
        print(json.loads(result.extracted_content)[:5])

asyncio.run(cosine_similarity_extraction())

# %%

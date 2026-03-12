# Crawl4AI 101 - Web Scraping Tutorial

A comprehensive tutorial project demonstrating web scraping techniques using [Crawl4AI](https://github.com/unclecode/crawl4ai), a powerful AI-powered web crawling and scraping library built on Playwright.

## 📖 Overview

This repository contains practical examples and comparisons of different web scraping approaches, with a focus on Crawl4AI's capabilities for modern web applications. Whether you're dealing with static HTML or dynamic JavaScript-rendered content, you'll find examples that demonstrate best practices and effective techniques.

## ✨ Features

- **Basic Web Crawling**: Simple examples to get started with Crawl4AI
- **Dynamic Content Handling**: Techniques for scraping JavaScript-heavy websites
- **Library Comparisons**: Side-by-side comparisons of BeautifulSoup, Scrapy, Selenium, Playwright, and Crawl4AI
- **Sitemap Crawling**: Examples of crawling entire websites using sitemaps
- **Jupyter Notebooks**: Interactive notebooks for learning and experimentation

## 🗂️ Project Structure

```
├── 01-Intro/                          # Introduction and beginner examples
│   ├── 01-app.py                      # Basic Crawl4AI application
│   └── 01-app_v3.py                   # Verbose comparison with rich output
├── src/c4a_series/videos/             # 20 short YouTube tutorial scripts
├── use-browser_101/                   # Browser sanity checks and intro
├── crawl4ai_quickstart.py             # Quick start guide script
├── crawl4ai_quickstart.ipynb          # Interactive quickstart notebook
├── crawl_sitmap.py                    # Sitemap crawling example
├── web_scraper_comparison.ipynb       # Comprehensive library comparison
└── archive/                           # Older scraper comparison notebooks
```

## 🎬 YouTube Tutorial Series Scripts

The full 20-video tutorial outline in `Crawl4AI_Outline.md` now has runnable scripts under `src/c4a_series/videos/`.
Each episode stays under 200 lines and focuses on one Crawl4AI concept.

Examples:

```bash
conda activate py312
python src/c4a_series/videos/v01_hello_arun.py
python src/c4a_series/videos/v08_css_extraction.py
python src/c4a_series/videos/v17_arun_many_dispatchers.py
```

LLM-based episodes:

- `v11_generate_schema_tokenusage.py`
- `v12_llm_extraction_chunking.py`

These read `OPENAI_API_KEY` from `.env` if present.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip or conda for package management

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Crawl4AI_101.git
cd Crawl4AI_101
```

2. Install required dependencies:
```bash
pip install crawl4ai playwright beautifulsoup4 requests scrapy selenium rich
```

3. Install Playwright browsers:
```bash
playwright install
```

### Quick Start

Run the basic quickstart example:
```bash
python crawl4ai_quickstart.py
```

Or explore the interactive Jupyter notebook:
```bash
jupyter notebook crawl4ai_quickstart.ipynb
```

## 📚 Examples

### Basic Crawling
```python
from crawl4ai import AsyncWebCrawler

async def simple_crawl():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com")
        print(result.markdown.raw_markdown)
```

### Dynamic Content
The repository includes examples of handling dynamic JavaScript content, including:
- Waiting for specific elements to load
- Clicking buttons and interacting with pages
- Handling infinite scroll and lazy loading

### Library Comparisons
Compare the performance and capabilities of different scraping libraries:
- **BeautifulSoup**: Simple, static pages
- **Scrapy**: Large-scale, production crawling
- **Selenium**: Full browser automation
- **Playwright**: Modern browser automation
- **Crawl4AI**: AI-powered extraction with LLM integration

## 🎯 Use Cases

- **Data Extraction**: Extract structured data from websites
- **Content Monitoring**: Track changes on web pages
- **Research**: Gather data for analysis and research projects
- **LLM Training**: Collect clean, markdown-formatted content for AI models
- **Testing**: Compare different scraping approaches and performance

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs and issues
- Suggest new features or examples
- Submit pull requests with improvements

## 🔗 Resources

- [Crawl4AI Documentation](https://crawl4ai.com/docs)
- [Crawl4AI GitHub Repository](https://github.com/unclecode/crawl4ai)
- [Playwright Documentation](https://playwright.dev/python/)

## 💡 Tips

- Start with the quickstart examples in the `01-Intro` folder
- Use the comparison notebooks to understand when to use each library
- Refer to the Crawl4AI documentation for advanced features like LLM extraction strategies

## ⚠️ Disclaimer

Please respect websites' `robots.txt` files and terms of service when scraping. This repository is for educational purposes.

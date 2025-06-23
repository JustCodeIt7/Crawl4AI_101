#%% Imports
import argparse
import os
from pathlib import Path
from urllib.parse import urlparse, unquote
from crawl4ai import CrawlerHub

#%% Sitemap Crawler Function
def crawl_and_save_sitemap(sitemap_url: str, output_dir: str):
    # Initialize the crawler
    crawler = CrawlerHub()

    # Create the base output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {Path(output_dir).resolve()}")

    def process_url(url: str, success: bool, html_content: str, error_message: str | None):
        if not success:
            print(f"Failed to crawl {url}: {error_message}")
            return

        print(f"Processing: {url}")
        try:
            # Scrape content as Markdown
            result = crawler.scrape(url=url, output_format="markdown")

            if not result or not result.content:
                print(f"No content scraped from {url}")
                return

            # Determine the file path based on the URL path
            parsed_url = urlparse(url)
            # Decode URL-encoded characters in the path
            url_path = unquote(parsed_url.path.lstrip('/'))

            # Handle index pages (e.g., /about/ -> /about/index.md)
            if not url_path or url_path.endswith('/'):
                file_name = "index.md"
            else:
                # Ensure it ends with .md, handling cases with existing extensions
                path_parts = url_path.split('/')
                last_part = path_parts[-1]
                if '.' in last_part:  # Check if there's an extension
                    file_name = os.path.splitext(last_part)[0] + ".md"
                else:
                    file_name = last_part + ".md"
                # Reconstruct path without the original last part
                url_path = '/'.join(path_parts[:-1])

            # Construct the full path within the output directory
            relative_dir = Path(url_path)
            full_dir_path = Path(output_dir) / relative_dir
            full_file_path = full_dir_path / file_name

            # Create necessary directories
            full_dir_path.mkdir(parents=True, exist_ok=True)

            # Save the Markdown content
            with open(full_file_path, "w", encoding="utf-8") as f:
                f.write(result.content)
            print(f"Saved: {full_file_path}")

        except Exception as e:
            print(f"Error processing {url}: {e}")

    # Start crawling the sitemap
    print(f"Starting crawl for sitemap: {sitemap_url}")
    crawler.crawl_sitemap(
        sitemap_url=sitemap_url,
        callback=process_url,
        # You can adjust concurrency if needed
        concurrency=5
    )
    print("Sitemap crawl finished.")

#%% Command Line Interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crawl a sitemap, scrape pages, and save as Markdown."
    )
    parser.add_argument(
        "sitemap_url",
        type=str,
        help="The URL of the sitemap.xml file."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="sitemap_output",
        help="The directory to save the scraped Markdown files (default: sitemap_output)."
    )

    args = parser.parse_args()
    crawl_and_save_sitemap(args.sitemap_url, args.output)

#%% Interactive Testing
# Uncomment and modify the line below to test interactively
# crawl_and_save_sitemap("https://example.com/sitemap.xml", "test_output")
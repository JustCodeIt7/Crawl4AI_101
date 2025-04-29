#%% Imports
import argparse
import os
from pathlib import Path
from urllib.parse import urlparse, unquote
from crawl4ai import Crawl4ai

#%% Main Function
def crawl_and_save_sitemap(sitemap_url: str, output_dir: str):
    """
    Crawls a sitemap, scrapes content from each URL, and saves it as Markdown
    in a directory structure mirroring the website path.

    Args:
        sitemap_url: The URL of the sitemap.xml file.
        output_dir: The base directory to save the Markdown files.
    """
    try:
        # Initialize the crawler
        crawler = Crawl4ai()

        # Create the base output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"Output directory: {output_path.resolve()}")

    except Exception as e:
        print(f"Error initializing crawler or creating output directory: {e}")
        return

    def process_url(url: str, success: bool, html_content: str, error_message: str | None):
        """Callback function to process each crawled URL."""
        if not success:
            print(f"Failed to crawl {url}: {error_message}")
            return

        print(f"Processing: {url}")
        try:
            # Scrape content as Markdown
            result = crawler.scrape(url=url, output_format="markdown")

            if not result or not result.content:
                print(f"No content scraped or returned from {url}")
                return

            # --- Refined Path Generation using pathlib ---
            parsed_url = urlparse(url)
            # Decode URL-encoded characters and remove leading slash
            url_path_decoded = unquote(parsed_url.path.lstrip('/')) # e.g., 'about/team' or 'faq.html' or 'about/' or ''

            # Create a Path object from the decoded path
            relative_path = Path(url_path_decoded)

            # Determine the final file path within the output directory
            if not url_path_decoded or url_path_decoded.endswith('/'):
                # Handle root or directory index: save as index.md inside the directory
                full_dir_path = output_path / relative_path
                full_file_path = full_dir_path / "index.md"
            else:
                # Handle paths ending with a filename (with or without extension)
                full_dir_path = output_path / relative_path.parent
                # Change the suffix to .md
                full_file_path = full_dir_path / (relative_path.stem + ".md")

            # Create necessary directories
            full_dir_path.mkdir(parents=True, exist_ok=True)

            # Save the Markdown content
            with open(full_file_path, "w", encoding="utf-8") as f:
                f.write(result.content)
            print(f"Saved: {full_file_path}")

        except OSError as e:
            print(f"File system error processing {url} -> {full_file_path}: {e}")
        except Exception as e:
            print(f"Unexpected error processing {url}: {e}")

    # Start crawling the sitemap
    try:
        print(f"Starting crawl for sitemap: {sitemap_url}")
        crawler.crawl_sitemap(
            sitemap_url=sitemap_url,
            callback=process_url,
            # Optional: Add concurrency if needed, e.g., concurrency=5
        )
        print("Sitemap crawl finished.")
    except Exception as e:
        print(f"Error during sitemap crawl initiation for {sitemap_url}: {e}")


#%% Argument Parser and Execution Block
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crawl a sitemap, scrape pages, and save as Markdown."
    )
    parser.add_argument(
        "sitemap_url",
        type=str,
        help="The URL of the sitemap.xml file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="sitemap_output",
        help="The directory to save the scraped Markdown files (default: sitemap_output).",
    )

    args = parser.parse_args()

    crawl_and_save_sitemap(args.sitemap_url, args.output)

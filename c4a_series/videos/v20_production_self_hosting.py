import asyncio
import os
import sys
from pathlib import Path

############################# Path Configuration #############################

# When running this script directly (e.g., `python v20_production_self_hosting.py`),
# __package__ will be None or empty. In that case, add the project root (two levels
# up) to sys.path so that sibling package imports resolve correctly.
if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    Crawl4aiDockerClient,
    CrawlerRunConfig,
    ProxyConfig,
    RoundRobinProxyStrategy,
)

from c4a_series.common.io import load_env

# Define the target URL to crawl — the official Crawl4AI documentation site
URL = "https://docs.crawl4ai.com/"

########################### Local SDK Demo ###################################


async def local_sdk_demo() -> None:
    """Crawl a URL using the local Crawl4AI SDK with production-grade settings.

    Demonstrates how to configure proxy support, SSL certificate capture,
    network request interception, and console message capture — features
    commonly needed in production scraping pipelines.

    Proxy behaviour is driven by the PROXIES environment variable:
    - Not set / empty: no proxy is used.
    - One proxy entry: that single proxy is applied directly.
    - Multiple proxy entries: requests are distributed via round-robin rotation.
    """
    # ProxyConfig.from_env() reads proxy connection details (host, port,
    # username, password) from environment variables, returning a list of
    # ProxyConfig objects — one per configured proxy endpoint.
    proxies = ProxyConfig.from_env() if os.getenv("PROXIES") else []

    run_config = CrawlerRunConfig(
        # Always fetch the live page instead of returning cached data
        cache_mode=CacheMode.BYPASS,
        # If exactly one proxy is configured, apply it directly to every request
        proxy_config=proxies[0] if len(proxies) == 1 else None,
        # RoundRobinProxyStrategy rotates through the proxy list in order,
        # distributing requests evenly to avoid hitting per-IP rate limits
        proxy_rotation_strategy=RoundRobinProxyStrategy(proxies) if len(proxies) > 1 else None,
        # fetch_ssl_certificate=True retrieves the TLS certificate presented by
        # the server, enabling downstream validation or certificate pinning checks
        fetch_ssl_certificate=True,
        # capture_console_messages=True records all browser console output
        # (console.log, console.warn, console.error), useful for debugging
        # client-side scripts or detecting hidden error signals on the page
        capture_console_messages=True,
        # capture_network_requests=True intercepts every HTTP request the
        # browser makes while rendering the page, giving full visibility into
        # XHR calls, API requests, and third-party resource loads
        capture_network_requests=True,
        # Inject a small JS snippet so we can verify console capture is working;
        # this message should appear in the captured console_messages list
        js_code="console.log('production-demo');",
        # Wait until the <body> element is present before extracting content,
        # ensuring the page has at least partially rendered
        wait_for="body",
        verbose=False,
    )

    # enable_stealth=True activates a collection of bot-detection evasion
    # techniques (e.g., masking navigator.webdriver, spoofing browser
    # fingerprints) to make the headless browser appear more like a real user
    async with AsyncWebCrawler(config=BrowserConfig(headless=True, enable_stealth=True, verbose=False)) as crawler:
        result = await crawler.arun(url=URL, config=run_config)

    # Safely extract the optional production-feature fields from the result
    # using getattr so the code stays compatible if these fields are absent
    certificate = getattr(result, "ssl_certificate", None)
    requests = getattr(result, "network_requests", None) or []
    console = getattr(result, "console_messages", None) or []

    # Report the crawl outcome and counts of captured network/console events
    print("local_success:", result.success)
    print("network_requests:", len(requests), "console_messages:", len(console))

    # Print the SSL issuer to confirm certificate capture worked; None if no
    # certificate was returned (e.g., plain HTTP or capture disabled)
    print("ssl_issuer:", getattr(certificate, "issuer", None) if certificate else None)


########################## Self-Hosted Server Demo ###########################


async def self_host_demo() -> None:
    """Crawl a URL via a self-hosted Crawl4AI Docker server.

    Crawl4aiDockerClient connects to a remote Crawl4AI instance running inside
    a Docker container and exposes the same crawl API over HTTP. This lets you
    offload browser workloads to a dedicated server rather than running a
    headless browser in the calling process.

    The C4AI_SERVER environment variable must be set to the base URL of the
    self-hosted server (e.g., "http://localhost:11235"). If it is not set this
    demo is skipped gracefully so the script can still run in environments
    without a server configured.
    """
    # C4AI_SERVER is the base URL of the self-hosted Crawl4AI Docker server
    # (e.g., "http://localhost:11235" or a remote address). The client uses
    # this to route all crawl requests to the correct endpoint.
    base_url = os.getenv("C4AI_SERVER")
    if not base_url:
        print("C4AI_SERVER not set; skipping self-host demo.")
        return

    try:
        # Crawl4aiDockerClient wraps the server's REST API in the same async
        # context-manager interface used by the local AsyncWebCrawler, so
        # switching between local and remote execution requires minimal code changes
        async with Crawl4aiDockerClient(base_url=base_url, verbose=False) as client:
            result = await client.crawl(
                [URL],
                browser_config=BrowserConfig(headless=True, verbose=False),
                crawler_config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False),
            )

        # client.crawl() returns either a list of results (one per URL) or a
        # single result object depending on the server version; normalise to
        # a single result for display
        first = result[0] if isinstance(result, list) else result
        print("server_success:", first.success, "url:", first.url)

    except Exception as exc:
        # Surface connection errors or unexpected server responses without
        # crashing the overall script
        print("self-host demo failed:", exc)


################################# Entry Point ################################


async def main() -> None:
    """Load environment variables and run both crawl demos sequentially.

    Calls load_env() to populate os.environ from a .env file (if present)
    before any demo logic reads environment variables, ensuring that proxy
    settings and server configuration are available at runtime.
    """
    # Populate environment variables from a .env file before any demo reads them
    load_env()

    # Run the local SDK demo first, then attempt the self-hosted server demo
    await local_sdk_demo()
    await self_host_demo()


# Standard Python entry-point guard — use asyncio.run() to execute the
# async main() coroutine from a synchronous context
if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import os
import sys
from pathlib import Path

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

URL = "https://docs.crawl4ai.com/"


async def local_sdk_demo() -> None:
    proxies = ProxyConfig.from_env() if os.getenv("PROXIES") else []
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        proxy_config=proxies[0] if len(proxies) == 1 else None,
        proxy_rotation_strategy=RoundRobinProxyStrategy(proxies) if len(proxies) > 1 else None,
        fetch_ssl_certificate=True,
        capture_console_messages=True,
        capture_network_requests=True,
        js_code="console.log('production-demo');",
        wait_for="body",
        verbose=False,
    )

    async with AsyncWebCrawler(config=BrowserConfig(headless=True, enable_stealth=True, verbose=False)) as crawler:
        result = await crawler.arun(url=URL, config=run_config)

    certificate = getattr(result, "ssl_certificate", None)
    requests = getattr(result, "network_requests", None) or []
    console = getattr(result, "console_messages", None) or []
    print("local_success:", result.success)
    print("network_requests:", len(requests), "console_messages:", len(console))
    print("ssl_issuer:", getattr(certificate, "issuer", None) if certificate else None)


async def self_host_demo() -> None:
    base_url = os.getenv("C4AI_SERVER")
    if not base_url:
        print("C4AI_SERVER not set; skipping self-host demo.")
        return

    try:
        async with Crawl4aiDockerClient(base_url=base_url, verbose=False) as client:
            result = await client.crawl(
                [URL],
                browser_config=BrowserConfig(headless=True, verbose=False),
                crawler_config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS, verbose=False),
            )
        first = result[0] if isinstance(result, list) else result
        print("server_success:", first.success, "url:", first.url)
    except Exception as exc:
        print("self-host demo failed:", exc)


async def main() -> None:
    load_env()
    await local_sdk_demo()
    await self_host_demo()


if __name__ == "__main__":
    asyncio.run(main())

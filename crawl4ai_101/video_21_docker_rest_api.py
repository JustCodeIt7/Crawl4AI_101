"""Video 21: Crawl4AI Docker deployment and REST API usage.

Demonstrates:
- calling a local/self-hosted Crawl4AI server
- /crawl, /crawl/stream, /html, and /execute_js endpoints
- graceful skipping when the local server is unavailable

Prerequisites:
- `pip install requests`
- Crawl4AI server running locally, for example via Docker

Run:
- `python crawl4ai_101/video_21_docker_rest_api.py`
"""

import json
import os

import requests

BASE_URL = os.getenv("CRAWL4AI_BASE_URL", "http://localhost:11235").rstrip("/")
TARGET_URL = "https://example.com"
TIMEOUT = 20


def post_json(path: str, payload: dict, stream: bool = False):
    return requests.post(
        f"{BASE_URL}{path}",
        json=payload,
        timeout=TIMEOUT,
        stream=stream,
    )


def main() -> None:
    try:
        requests.get(f"{BASE_URL}/playground", timeout=5)
    except requests.RequestException as exc:
        print(f"SKIP: Crawl4AI server is not reachable at {BASE_URL}: {exc}")
        return

    crawl_response = post_json("/crawl", {"urls": [TARGET_URL]})
    print(f"/crawl status: {crawl_response.status_code}")
    if crawl_response.ok:
        payload = crawl_response.json()
        print(f"/crawl keys: {sorted(payload.keys())[:8]}")

    html_response = post_json("/html", {"url": TARGET_URL})
    print(f"/html status: {html_response.status_code}")
    if html_response.ok:
        html_payload = html_response.json()
        print(f"/html keys: {sorted(html_payload.keys())[:6]}")

    js_response = post_json(
        "/execute_js",
        {"url": TARGET_URL, "scripts": ["return document.title", "return window.location.href"]},
    )
    print(f"/execute_js status: {js_response.status_code}")
    if js_response.ok:
        js_payload = js_response.json()
        print(f"/execute_js preview: {json.dumps(js_payload)[:180]}...")

    stream_response = post_json("/crawl/stream", {"urls": [TARGET_URL]}, stream=True)
    print(f"/crawl/stream status: {stream_response.status_code}")
    if stream_response.ok:
        lines = [line.decode("utf-8") for line in stream_response.iter_lines() if line][:3]
        print(f"/crawl/stream first lines: {lines}")


if __name__ == "__main__":
    main()

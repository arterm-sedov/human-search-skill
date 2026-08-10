#!/usr/bin/env python3
"""Extract a public HTML page as Markdown with lightweight block detection."""

from __future__ import annotations

import os
import re
import sys
from urllib.parse import urlparse

import requests
import tiktoken
from bs4 import BeautifulSoup
from markdownify import markdownify as md

DEFAULT_USER_AGENT = (
    "human-search-skill/1.0 "
    "(+https://github.com/arterm-sedov/human-search-skill)"
)
BLOCK_MARKERS = (
    "verify you are human",
    "access denied",
    "unusual traffic",
    "enable javascript and cookies",
)


def request_headers() -> dict[str, str]:
    return {
        "User-Agent": os.environ.get("HUMAN_SEARCH_USER_AGENT", DEFAULT_USER_AGENT),
        "Accept": "text/html,application/xhtml+xml",
    }


def scrape(url: str, timeout: int = 20) -> dict[str, object]:
    """Return page metadata and Markdown, or an error suitable for fallback."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return {"error": "URL must include an http:// or https:// scheme", "reason": "invalid-url"}
    try:
        response = requests.get(url, timeout=timeout, headers=request_headers())
        response.raise_for_status()
    except requests.RequestException as exc:
        return {"error": str(exc), "reason": "request-failed"}

    content_type = response.headers.get("Content-Type", "").lower()
    if "html" not in content_type:
        return {
            "error": f"Expected HTML but received {content_type or 'unknown content type'}",
            "reason": "non-html",
        }
    soup = BeautifulSoup(response.text, "lxml")
    visible_text = soup.get_text(" ", strip=True).lower()
    captcha_page = "captcha" in visible_text and len(visible_text.split()) < 100
    if captcha_page or any(marker in visible_text for marker in BLOCK_MARKERS):
        return {"error": "The page returned a block or CAPTCHA challenge", "reason": "blocked"}
    script_count = len(soup.find_all("script"))
    title = soup.title.get_text(" ", strip=True) if soup.title else url
    for tag in soup.find_all(("script", "nav", "footer", "aside", "iframe", "style", "meta", "noscript")):
        tag.decompose()
    for tag in soup.find_all(
        class_=lambda classes: classes
        and any(
            token in " ".join(classes if isinstance(classes, list) else [classes]).lower()
            for token in ("sticky", "modal", "popup", "sidebar", "cookie-banner")
        )
    ):
        tag.decompose()

    markdown = md(str(soup))
    markdown = re.sub(r"(\s*\n){3,}", "\n\n", markdown).strip()
    words = len(markdown.split())
    warning = ""
    if words < 15 or (words < 60 and script_count >= 5):
        warning = "Static extraction is unexpectedly thin; retry with a browser."
    tokens = len(tiktoken.get_encoding("cl100k_base").encode(markdown))
    return {
        "url": response.url,
        "title": title,
        "content": markdown,
        "tokens": tokens,
        "words": words,
        "warning": warning,
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("Usage: python quick_scrape.py <url>")
        return 2
    result = scrape(args[0])
    if "error" in result:
        print(f"Error ({result.get('reason', 'unknown')}): {result['error']}")
        return 1
    print(f"Title: {result['title']}")
    print(f"Tokens: {result['tokens']}")
    print(f"Words: {result['words']}")
    if result.get("warning"):
        print(f"Warning: {result['warning']}")
    print("\n--- Content Preview (first 1000 chars) ---")
    print(str(result["content"])[:1000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

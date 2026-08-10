#!/usr/bin/env python3
"""
Quick single-page scraper for human-search skill.
Usage: python quick_scrape.py <url>
"""
import sys
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import tiktoken
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

def scrape(url, timeout=20):
    """Scrape a single URL and return title, content, and token count."""
    try:
        resp = requests.get(url, timeout=timeout, headers=HEADERS)
        resp.raise_for_status()
    except Exception as e:
        return {'error': str(e)}
    
    soup = BeautifulSoup(resp.text, 'lxml')
    
    # Remove unwanted elements
    unwanted = ['script', 'nav', 'footer', 'aside', 'iframe', 'style', 'meta']
    for tag in soup.find_all(unwanted):
        tag.decompose()
    
    # Remove elements by class
    for tag in soup.find_all(class_=lambda c: c and any(x in str(c) for x in ['sticky', 'modal', 'popup', 'sidebar'])):
        tag.decompose()
    
    # Convert to markdown
    markdown = md(str(soup))
    markdown = re.sub(r'(\s*\n){3,}', '\n\n', markdown)
    markdown = re.sub(r'^\s*\n', '', markdown)
    
    # Count tokens
    enc = tiktoken.get_encoding('cl100k_base')
    tokens = len(enc.encode(markdown))
    words = len(markdown.split())
    
    return {
        'url': url,
        'title': soup.title.string.strip() if soup.title else url,
        'content': markdown,
        'tokens': tokens,
        'words': words
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python quick_scrape.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    result = scrape(url)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    print(f"Title: {result['title']}")
    print(f"Tokens: {result['tokens']}")
    print(f"Words: {result['words']}")
    print(f"\n--- Content Preview (first 1000 chars) ---")
    print(result['content'][:1000])
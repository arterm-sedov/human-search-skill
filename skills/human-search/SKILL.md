---
name: human-search
description: |
  Comprehensive human-like web search and scraping meta-skill. Mimics human behavior to bypass blocks/rate-limits. Auto-installs dependencies, auto-repairs failures, cascades through 5 tiers: (1) Browser CLI (agent-browser/playwright), (2) Scraping APIs (crawl4ai/jina.ai), (3) Python scraper (unlimited), (4) Quick extract (searxng/tavily), (5) Discovery search. Includes Yandex search. For Telegram login: telegram-scraper. Use for any "search", "scrape", "extract", "find articles" request.
compatibility: Auto-installs Python (crawl4ai, requests, bs4, lxml, markdownify, tiktoken), npm (agent-browser, playwright-cli), fixes Docker. Yandex via direct curl.
allowed-tools: Bash(pip *), Bash(npm *), Bash(docker *), Bash(curl *), Bash(python *), Read, Glob, Grep, Write, Edit
---

# Human Search

**Robust meta-skill for human-like web search/scraping.** Auto-fixes issues, bypasses blocks, cascades intelligently. **No API keys required** (free, unlimited).

## Philosophy
1. **Human-like** — Avoids bot detection
2. **Self-healing** — Auto-installs, restarts, fixes configs
3. **Token-efficient** — Max content per call
4. **Cascade** — Tier 1 → Tier 5 fallback
5. **Yandex** — RU-specific search included

## Tier Cascade

```
Tier 0: jina.ai/reader     → Free, instant markdown (no install)
Tier 1: Browser CLI        → agent-browser/playwright (JS, human-like)
Tier 2: Scraping APIs      → crawl4ai (Playwright + readability)
Tier 3: Python Scraper     → BS4 + markdownify (unlimited)
Tier 4: Quick Extract      → searxng/tavily (2500-4000 chars)
Tier 5: Discovery          → searxng-search/Yandex/websearch
```

## Auto-Setup (Run First)
```bash
# Test & auto-fix all deps
python references/test_deps.py
```

## Tier 0: jina.ai/reader (Instant, Free)
```bash
curl https://r.jina.ai/https://example.com | head -500
```
**When:** Simple articles, quickest test.

## Tier 1: Browser CLI (Human-like, JS)
**Auto-install:**
```bash
npm install -g agent-browser playwright-cli
```
**Test:**
```bash
agent-browser --version
npx playwright --version
```
**Usage:**
```bash
# agent-browser (fastest)
agent-browser open https://example.com && agent-browser snapshot -i && agent-browser get text body

# playwright-cli
npx playwright-cli open https://example.com && npx playwright-cli snapshot
```
**Fallback:** If blocked → Tier 2

## Tier 2: crawl4ai (Anti-bot, JS)
**Auto-install:**
```bash
pip install crawl4ai
```
**Test:**
```bash
python -c "from crawl4ai import AsyncWebCrawler; print('OK')"
```
**Usage:**
```python
from crawl4ai import AsyncWebCrawler
crawler = AsyncWebCrawler()
result = crawler.arun('https://example.com')
print(result.markdown)
```
**Fallback:** Heavy sites → Tier 3

## Tier 3: Python Scraper (Unlimited)
**Auto-install:**
```bash
pip install requests beautifulsoup4 lxml markdownify tiktoken
```
**Quick scrape:**
```bash
python references/quick_scrape.py https://example.com
```
**Batch (sitemap):**
```bash
python references/cmwlab_crawl4ai_ingest.py
```
**Fallback:** Rate-limited → Tier 4

## Tier 4: Quick Extract
**Docker check/fix:**
```bash
curl -s http://localhost:8000/health || (cd D:/Repo/searxng-docker-tavily-adapter && docker compose up -d)
docker restart searxng
```
**Usage:**
```bash
curl -s -X POST http://localhost:8000/search -H "Content-Type: application/json" -d '{"query": "site:example.com", "max_results": 1, "include_raw_content": true}'
```
**Fallback:** Empty → Tier 5

## Tier 5: Discovery Search (Yandex + Fallbacks)
**Yandex (RU-specific):**
```bash
curl "https://yandex.com/search/?text=QUERY&lr=213" | grep -o 'https://[^"]*'
```
**SearXNG:**
```bash
curl -s -X POST http://localhost:8000/search -d '{"query": "QUERY", "max_results": 5}'
```
**Websearch fallback:** Native tool.

## Auto-Repair Commands
**Docker Fix:**
```bash
docker restart searxng tavily-adapter
docker logs searxng --tail 20 | grep ERROR
```
**Config Fix (rate-limits):**
```bash
# Edit D:/Repo/searxng-docker-tavily-adapter/config.yaml engines to Bing/Qwant
docker restart searxng
```
**Python Fix:**
```bash
pip install requests beautifulsoup4 lxml markdownify tiktoken crawl4ai --upgrade
```
**Node Fix:**
```bash
npm install -g agent-browser playwright-cli
```
**Full Test:**
```bash
python references/test_deps.py
```

## Telegram Note
Public t.me: Use Tier 1-3. Private login: [telegram-scraper](../telegram-scraper/SKILL.md)

## See Also
- [telegram-scraper](../telegram-scraper/SKILL.md)
- [cmw-kb](../cmw-kb/SKILL.md)
- [deep-research](../deep-research/SKILL.md)
- [searxng-search](../searxng-search/SKILL.md)
- [playwright-cli](../playwright-cli/SKILL.md)
- [agent-browser](../agent-browser/SKILL.md)
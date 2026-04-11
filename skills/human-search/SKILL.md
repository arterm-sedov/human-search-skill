---
name: human-search
description: |
  Comprehensive human-like web search and scraping meta-skill. Auto-installs deps, auto-repairs failures, cascades intelligently. Priority: Native websearch → Python scraper → Browser CLI → crawl4ai → Yandex. No API keys required. Use for any "search", "scrape", "extract", "find articles" request.
compatibility: Auto-installs Python (requests, beautifulsoup4, lxml, markdownify, tiktoken, crawl4ai), npm (agent-browser, playwright-cli), Docker for searxng (optional). Yandex via curl.
allowed-tools: Bash(pip *), Bash(npm *), Bash(docker *), Bash(curl *), Bash(python *), Bash(websearch *), Read, Glob, Grep, Write, Edit
---

# Human Search

**Robust meta-skill for web search/scraping.** Auto-fixes, cascades, free/unlimited.

## Philosophy
1. **Reliability first** — Use working methods, skip broken ones
2. **Self-healing** — Auto-installs deps, restarts services
3. **Token-efficient** — Max content per call
4. **Cascade** — Tier 1 → Tier 5 fallback

## Tier Cascade (Tested Order)

```
Tier 1: Native websearch   → Always works, fastest (USE FIRST)
Tier 2: Python scraper     → Unlimited, reliable (BS4 + markdownify)
Tier 3: Browser CLI        → JS sites, human-like (agent-browser/playwright)
Tier 4: crawl4ai           → Anti-bot, Playwright-based
Tier 5: Yandex             → RU-specific search fallback
```

**Note:** jina.ai/reader blocked by region. searxng Docker often fails. These removed from primary cascade.

## Auto-Setup
```bash
python references/test_deps.py
```

## Tier 1: Native Websearch (PRIMARY - Always Works)
```bash
websearch "python programming tutorial 2026"
```
**Use first** for any search task. Fastest, most reliable.

## Tier 2: Python Scraper (Reliable, Unlimited)
**Install:**
```bash
pip install requests beautifulsoup4 lxml markdownify tiktoken
```
**Quick scrape:**
```bash
python references/quick_scrape.py https://example.com
```
**Batch crawl:**
```bash
python references/cmwlab_crawl4ai_ingest.py
```
**Output:** Full markdown, token count.

## Tier 3: Browser CLI (JS Sites)
**Install:**
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
# agent-browser (fastest, token-efficient)
agent-browser open https://example.com && agent-browser snapshot -i && agent-browser get text body

# playwright-cli
npx playwright-cli open https://example.com && npx playwright-cli snapshot
```

## Tier 4: crawl4ai (Anti-bot)
**Install:**
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
**Note:** Heavy deps (60MB+), slower than Tier 2/3.

## Tier 5: Yandex (RU-specific)
```bash
curl -s "https://yandex.com/search/?text=QUERY&num=5"
```
**When:** Need Russian results specifically.

## Auto-Repair

**Docker (optional for Tier below):**
```bash
docker restart searxng tavily-adapter
docker logs searxng --tail 10
```

**Python deps:**
```bash
pip install requests beautifulsoup4 lxml markdownify tiktoken crawl4ai --upgrade
```

**Node deps:**
```bash
npm install -g agent-browser playwright-cli
```

**Test all:**
```bash
python references/test_deps.py
```

## Telegram
- Public t.me: Use Tier 2-3
- Private/login: [telegram-scraper](../telegram-scraper/SKILL.md)

## See Also
- [telegram-scraper](../telegram-scraper/SKILL.md)
- [cmw-kb](../cmw-kb/SKILL.md)
- [deep-research](../deep-research/SKILL.md)
- [playwright-cli](../playwright-cli/SKILL.md)
- [agent-browser](../agent-browser/SKILL.md)
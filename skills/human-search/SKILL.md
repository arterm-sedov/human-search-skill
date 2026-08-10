---
name: human-search
description: |
  Comprehensive human-like web search and scraping meta-skill. Auto-installs deps, auto-repairs failures, cascades intelligently. Priority: Python scraper → Browser CLI → crawl4ai → Yandex → native websearch (if available). No API keys required. Use for any "search", "scrape", "extract", "find articles" request.
compatibility: Auto-installs Python (requests, beautifulsoup4, lxml, markdownify, tiktoken, crawl4ai), npm (agent-browser, playwright, @playwright/cli), Docker for searxng (optional). Yandex via curl.
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
Tier 1: Python scraper     → Always works, reliable (BS4 + markdownify)
Tier 2: Browser CLI        → JS sites, human-like (agent-browser/playwright)
Tier 3: crawl4ai           → Anti-bot, Playwright-based
Tier 4: Yandex             → RU-specific search fallback
Tier 5: Native websearch   → Only if the agent has a websearch tool (optional)
```

**Note:** jina.ai/reader blocked by region. searxng Docker often fails. These removed from primary cascade.
**Note:** opencode has no built-in `websearch` tool; the agent must have one available for Tier 5, otherwise skip.

## Auto-Setup
```bash
python references/test_deps.py --fix
```

## Tier 1: Python Scraper (Reliable, Unlimited)
**Install:**
```bash
pip install requests beautifulsoup4 lxml markdownify tiktoken
```
**Quick scrape:**
```bash
python references/quick_scrape.py https://example.com
```
**Batch crawl (site-specific example):**
```bash
python references/cmwlab_ingest.py
```
**Output:** Full markdown, token count.

## Tier 2: Browser CLI (JS Sites)
**Install:**
```bash
npm install -g agent-browser playwright @playwright/cli
```
**Test:**
```bash
agent-browser --version
playwright --version
playwright-cli --version
```
**Note:** `playwright-cli` npm package is deprecated and EMPTY (no binary). Use official `@playwright/cli` (provides `playwright-cli` command) or `playwright` CLI directly.
**Usage:**
```bash
# agent-browser (fastest, token-efficient)
agent-browser open https://example.com && agent-browser snapshot -i && agent-browser get text body

# playwright CLI (direct)
playwright open https://example.com
npx playwright open https://example.com

# playwright-cli (from @playwright/cli) - persistent session browser
playwright-cli open https://example.com && playwright-cli snapshot
playwright-cli snapshot --filename=page.yaml && playwright-cli screenshot
playwright-cli close-all   # stop all browser sessions
```

## Direct Playwright Alternatives
When you need to work with Playwright directly (not through the cascade):

1. **`playwright` CLI** (installed globally) — `playwright open|screenshot|pdf|codegen`, `npx playwright <cmd>`
2. **`@playwright/cli`** (installed globally) — `playwright-cli` command, persistent browser sessions with snapshots/screenshots/videos
3. **Python Playwright** — `pip install playwright && playwright install chromium`, then drive via `sync_playwright()` or `async_playwright()` in scripts
4. **`@playwright/mcp`** — MCP server (`npx @playwright/mcp@latest`) for agents that use MCP tools
5. **agent-browser** — human-like, token-efficient alternative browser CLI

## Tier 3: crawl4ai (Anti-bot)
**Install:**
```bash
pip install crawl4ai
```
**Test:**
```bash
python -c "from crawl4ai import AsyncWebCrawler; print('OK')"
```
**Usage (async):**
```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun('https://example.com')
        print(result.markdown)

asyncio.run(main())
```
**Note:** Heavy deps (60MB+), slower than Tier 1/2.

## Tier 4: Yandex (RU-specific)
```bash
curl -s "https://yandex.com/search/?text=QUERY&num=5"
```
**When:** Need Russian results specifically.

## Tier 5: Native Websearch (OPTIONAL)
```bash
websearch "python programming tutorial 2026"
```
**Only if** the agent has a `websearch` tool available. opencode does not include one by default.

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
npm install -g agent-browser playwright @playwright/cli
```

**Test all:**
```bash
python references/test_deps.py
```

## Telegram
- Public t.me: Use Tier 1-2
- Private/login: [telegram-scraper](../telegram-scraper/SKILL.md)

## See Also
- [telegram-scraper](../telegram-scraper/SKILL.md)
- [cmw-kb](../cmw-kb/SKILL.md)
- [deep-research](../deep-research/SKILL.md)
- [agent-browser](../agent-browser/SKILL.md)
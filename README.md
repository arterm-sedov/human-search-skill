# Human Search Skill

[![Status](https://img.shields.io/badge/status-ready-green.svg)](https://github.com/anomalyco/opencode/issues)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Why This Skill Exists

Web search and scraping in AI agents is **fragmented**:
- **searxng-search**: Free but rate-limited
- **agent-browser**: Human-like but browser-only
- **playwright-cli**: Powerful but token-heavy
- **tavily**: Paid API limits
- **Local scripts**: No integration

**human-search solves this** with:
1. **5-tier cascade** — Starts human-like, falls back gracefully
2. **Auto-repair** — Installs deps, restarts Docker, fixes configs
3. **Free/unlimited** — No API keys
4. **Token-efficient** — Max content per call
5. **Block-proof** — Bypasses anti-bot measures

**Result:** One skill handles 95% of search/scraping needs reliably.

## Quick Start

```bash
# Load skill
skill name:human-search

# Use it
\"scrape python.org full content with token count\"
```

## Tier Cascade (Intelligent Fallback)

| Tier | Tool | When | Content Limit | Speed |
|------|------|------|---------------|-------|
| 0 | jina.ai/reader | Articles | ~10K chars | Instant |
| 1 | agent-browser/playwright | JS sites | Unlimited | Fast |
| 2 | crawl4ai | Anti-bot | Unlimited | Medium |
| 3 | Python BS4 | KB/docs | Unlimited | Fast |
| 4 | searxng-extract | Quick | 2500 chars | Very fast |
| 5 | Yandex/searxng/websearch | Discovery | Snippets | Instant |

## Auto-Setup (One Command)
```bash
python references/test_deps.py  # Tests + auto-fixes
```

**Installs:** crawl4ai, playwright, agent-browser, fixes Docker.

## Features

- **Human-like browsing** — Avoids CAPTCHA/rate-limits
- **Full-page extraction** — No char limits
- **Token counting** — tiktoken cl100k_base
- **Batch crawling** — Sitemap + progress save
- **Yandex search** — RU-specific
- **Self-healing** — Restarts services, reinstalls deps

## Comparison

| Feature | human-search | searxng | Tavily | Browser CLI |
|---------|--------------|---------|--------|-------------|
| Free | ✅ | ✅ | ❌ | ✅ |
| JS Rendering | ✅ | ❌ | Partial | ✅ |
| Anti-bot | ✅ | ❌ | ✅ | ✅ |
| Auto-repair | ✅ | ❌ | ❌ | ❌ |
| Token count | ✅ | ❌ | ✅ | ❌ |
| Cascade | ✅ | ❌ | ❌ | ❌ |

## Usage Examples

```bash
# Simple scrape
human-search \"extract python.org full content\"

# Search + scrape
human-search \"find best NYC restaurants 2026, scrape top 3\"

# Telegram public
human-search \"scrape t.me/durov\"

# With repair
human-search \"scrape site with JS\"  # Auto-tries browser if static fails
```

## Reference Scripts

- `test_deps.py` — Dependency checker/fixer
- `quick_scrape.py` — Single URL scraper
- `cmwlab_crawl4ai_ingest.py` — Batch sitemap crawler

## Troubleshooting

See SKILL.md auto-repair section.

## Adjacent Skills

- [telegram-scraper-skill](https://github.com/arterm-sedov/telegram-scraper-skill) — Telegram extraction (public/private)
- [searxng-agent-skills](https://github.com/arterm-sedov/searxng-agent-skills) — Free search base
- [cmw-kb-skills](https://github.com/arterm-sedov/cmw-kb-skills) — CMW Platform docs
- [browser-switch-skill](https://github.com/arterm-sedov/browser-switch-skill) — Browser choice
- [doc-restructure-skill](https://github.com/arterm-sedov/doc-restructure-skill) — Markdown processing

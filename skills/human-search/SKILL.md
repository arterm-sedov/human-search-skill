---
name: human-search
description: Search the public web, discover current sources, extract known public URLs, and render interactive pages with automatic application-dependency repair. Use for requests to search, find articles, scrape or extract web content, or browse Google or Yandex without paid API keys.
license: MIT
metadata:
  compatibility: Portable Agent Skills host with Python 3.10+; optional native web tools, Node.js browser CLI, and local SearXNG are detected at runtime.
---

# Human search

Classify the request before selecting a capability. Verify output quality and escalate only when the current method is incomplete or blocked.

## Route the request

### Discover sources

Use this route when the request contains a query but no known URL.

1. Use a native `websearch` capability when available.
2. Otherwise search through an available browser:

    - For Cyrillic or explicitly Russian queries, use Yandex first and Google second.
    - For other queries, use Google first and Yandex second.
    - For broad coverage, query both engines and merge the organic results.

3. Normalize result URLs, remove tracking parameters, exclude ads and engine-internal links, and deduplicate.
4. Switch engines when one returns CAPTCHA, consent-only, or unusable results.
5. Use a headed browser for human completion when both engines require interaction.

Do not pass search text to a URL scraper. Do not treat raw Google or Yandex HTTP responses as reliable search results.

### Extract a known URL

1. Use a native `webfetch` capability when available.
2. Otherwise run:

```bash
python references/quick_scrape.py https://example.com
```

3. Escalate to a browser when the response is blocked, non-HTML, unexpectedly thin, or JavaScript-dependent.

Set `HUMAN_SEARCH_USER_AGENT` when the target requires a specific request identity.

### Browse an interactive page

Reuse a healthy browser capability when available. If none works, repair the browser component:

```bash
python references/test_deps.py --fix --component browser
```

Prefer `@playwright/cli` for persistent agent sessions. Inspect `playwright-cli --help` before choosing session-management commands because the command names vary by release.

## Repair dependencies

Check without changing the environment:

```bash
python references/test_deps.py
```

Repair all application components:

```bash
python references/test_deps.py --fix
```

Repair only the capability required by the current task:

```bash
python references/test_deps.py --fix --component core
python references/test_deps.py --fix --component browser
```

Repair Python and Node packages and browser binaries only. Do not install system runtimes, Docker, OS packages, or services. Attempt one repair, verify it, retry the task, and then fall back.

Prefer an already active virtual environment. If the system Python is externally managed and `uv` is already available, run `uv venv`, then prefix skill commands with `uv run`; this discovers the project-local `.venv` on Windows and Linux without embedding interpreter paths. Otherwise run `python -m venv .venv`, activate it using the current shell's standard mechanism, and continue with `python`. Do not install `uv`, bypass PEP 668, install a Python runtime, or modify system Python.

## Handle Google and Yandex results

Use browser-rendered result pages:

```text
https://www.google.com/search?q=QUERY
https://yandex.com/search/?text=QUERY
```

Preserve source-engine attribution when combining results. Rank URLs returned by both engines ahead of single-engine results.

## Telegram

- For public `t.me` pages, use known-URL extraction and escalate to a browser as needed.
- For private or authenticated channels, use the dedicated Telegram scraper capability.

# Human Search Skill

[![Status](https://img.shields.io/badge/status-ready-green.svg)](https://github.com/arterm-sedov/human-search-skill/issues)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

`human-search` routes public-web discovery, URL extraction, and interactive browsing to the cheapest suitable capability. It can repair missing application packages and browser binaries without installing system runtimes or services.

## Request routing

The skill selects a workflow by intent rather than applying one universal tool order.

| Request | Primary capability | Escalation |
| --- | --- | --- |
| Search or find sources | Native `websearch` | Google/Yandex through a browser |
| Extract a known URL | Native `webfetch` or Python scraper | Browser rendering |
| Interact with a page | Existing browser | Repair `@playwright/cli` and Chromium |

For Russian or Cyrillic queries, the browser workflow searches Yandex before Google. Other queries use Google before Yandex. Broad requests may query both and merge normalized, deduplicated organic links.

## Usage

Search runs through the host's native `websearch` or a browser session. Extraction and repair use these commands:

```bash
python references/quick_scrape.py https://example.com   # extract one URL
python references/test_deps.py                          # check dependencies
python references/test_deps.py --fix                    # repair all components
```

## Install the skill

Copy `skills/human-search/` into a supported Agent Skills directory. The host discovers the skill through `SKILL.md`; package installation occurs only when dependency repair is invoked.

Use an isolated environment when the system Python is externally managed. If `uv` is already installed, the same commands work across supported shells and operating systems:

```text
uv venv
uv run python references/test_deps.py --fix
```

Continue to prefix Python commands with `uv run`, which discovers the project-local `.venv`. The skill does not install or require `uv`.

Without `uv`, run `python -m venv .venv`, activate that environment with the current shell's standard activation command, and then use `python` normally. Do not pass `--break-system-packages`, install a Python runtime, or modify the operating system's Python environment.

## Check and repair dependencies

Run a side-effect-free check:

```bash
python references/test_deps.py
```

Repair all application components:

```bash
python references/test_deps.py --fix
```

Repair one component:

```bash
python references/test_deps.py --fix --component core
python references/test_deps.py --fix --component browser
```

The repair boundary includes allowlisted Python packages, `@playwright/cli`, and browser binaries. It excludes Python, Node.js, Docker, OS packages, and system services.

## Extract one URL

```bash
python references/quick_scrape.py https://example.com
```

The command validates the URL and content type, detects common block pages, converts HTML to Markdown, and reports when static content is too thin for reliable extraction. Override its identifiable default request identity with `HUMAN_SEARCH_USER_AGENT` when required.

## Reference files

- `test_deps.py`: capability check and application-level repair.
- `quick_scrape.py`: lightweight single-page extraction.

## Adjacent skills

- [telegram-scraper-skill](https://github.com/arterm-sedov/telegram-scraper-skill) - Telegram extraction
- [searxng-agent-skills](https://github.com/arterm-sedov/searxng-agent-skills) - free SearXNG search
- [cmw-kb-skills](https://github.com/arterm-sedov/cmw-kb-skills) - Comindware knowledge base
- [browser-switch-skill](https://github.com/arterm-sedov/browser-switch-skill) - browser choice
- [doc-restructure-skill](https://github.com/arterm-sedov/doc-restructure-skill) - Markdown restructuring

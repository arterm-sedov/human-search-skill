#!/usr/bin/env python3
"""
Dependency verification/repair script for human-search skill.
Tests all required packages and services; auto-installs missing Python deps.

Usage:
    python references/test_deps.py          # check only
    python references/test_deps.py --fix    # check + auto-install missing deps
"""
import sys
import shutil
import subprocess
import json

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def check_python_package(name, import_name=None):
    """Check if a Python package is installed."""
    if import_name is None:
        import_name = name.replace("-", "_")
    try:
        __import__(import_name)
        return True, None
    except ImportError as e:
        return False, str(e)


# Windows libuv assertion on exit is a Node-on-Windows bug, not a missing tool.
# Returned as unsigned (3221226505 = 0xC0000409) by subprocess on Windows.
WINDOWS_LIBUV_EXIT_CODES = {0xC0000409, 0xC0000409 - 2**32}


def check_command(cmd):
    """Check if a command is available and runnable."""
    exe = cmd.split()[0]
    if shutil.which(exe) is None:
        return False, f"'{exe}' not found on PATH"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return True, None
        # Windows: playwright-cli crashes with libuv assert AFTER printing version.
        if sys.platform == "win32" and result.returncode in WINDOWS_LIBUV_EXIT_CODES:
            return True, "note: libuv assert on exit (harmless Windows Node bug)"
        return False, f"exit code {result.returncode}"
    except Exception as e:
        return False, str(e)


def check_url(url):
    """Check if a URL is accessible."""
    try:
        import requests
        resp = requests.get(url, timeout=5)
        return resp.status_code == 200, None
    except Exception as e:
        return False, str(e)


def install_packages(packages):
    """Install Python packages via pip."""
    print(f"\n  Installing: {' '.join(packages)}")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", *packages],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"  Installation failed: {result.stderr[-500:]}")
            return False
        return True
    except Exception as e:
        print(f"  Installation failed: {e}")
        return False


def main():
    fix = "--fix" in sys.argv

    print("=" * 60)
    print("Human Search - Dependency Verification")
    print("=" * 60)

    results = {"passed": [], "failed": []}

    # Python packages
    print("\n[Python Packages]")
    packages = [
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("lxml", "lxml"),
        ("markdownify", "markdownify"),
        ("tiktoken", "tiktoken"),
        ("crawl4ai", "crawl4ai"),
    ]

    missing = []
    for name, import_name in packages:
        ok, error = check_python_package(name, import_name)
        status = "OK " if ok else "MISSING"
        print(f"  [{status}] {name}")
        if ok:
            results["passed"].append(f"Python: {name}")
        else:
            results["failed"].append(f"Python: {name} - {error}")
            missing.append(name)

    if missing and fix:
        print("\n  Auto-installing missing Python deps...")
        if install_packages(missing):
            for name in missing:
                import_name = name.replace("-", "_")
                ok, error = check_python_package(name, import_name)
                if ok:
                    results["passed"].append(f"Python: {name}")
                    results["failed"] = [
                        f for f in results["failed"]
                        if not f.startswith(f"Python: {name}")
                    ]
                else:
                    print(f"  Could not verify {name} after install: {error}")

    # Node packages
    print("\n[Node Packages]")
    node_checks = [
        ("agent-browser", "agent-browser --version"),
        ("playwright", "npx playwright --version"),
        ("playwright-cli", "playwright-cli --version"),
    ]

    for name, cmd in node_checks:
        ok, error = check_command(cmd)
        status = "OK " if ok else "MISSING"
        print(f"  [{status}] {name}")
        if ok:
            results["passed"].append(f"Node: {name}")
        else:
            results["failed"].append(f"Node: {name}")

    # Docker services (optional, informational only)
    print("\n[Docker Services]")
    service_checks = [
        ("SearXNG Adapter", "http://localhost:8000/health"),
        ("SearXNG UI", "http://localhost:8999"),
    ]

    for name, url in service_checks:
        ok, error = check_url(url)
        status = "OK " if ok else "SKIP"
        print(f"  [{status}] {name} (optional)")
        if ok:
            results["passed"].append(f"Docker: {name}")
        else:
            results["failed"].append(f"Docker: {name} - optional service not running")

    # Summary
    print("\n" + "=" * 60)
    print(f"Summary: {len(results['passed'])} passed, {len(results['failed'])} failed")
    print("=" * 60)

    if results["failed"]:
        print("\nNotes:")
        for f in results["failed"]:
            print(f"  - {f}")
        print("\nCommands to fix manually:")
        print("  Python: python -m pip install requests beautifulsoup4 lxml markdownify tiktoken crawl4ai")
        print("  Node:   npm install -g agent-browser playwright @playwright/cli")
        print("  Docker: optional - SearXNG services not required for the cascade")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

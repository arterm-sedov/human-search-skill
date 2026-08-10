#!/usr/bin/env python3
"""Check and repair application dependencies for the human-search skill."""

from __future__ import annotations

import argparse
import importlib
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass


STATUS_OK = "OK"
STATUS_MISSING = "MISSING"
STATUS_REPAIRED = "REPAIRED"
STATUS_FAILED = "FAILED"
STATUS_OPTIONAL = "OPTIONAL"
COMPONENTS = ("core", "browser", "all")


@dataclass(frozen=True)
class PackageSpec:
    distribution: str
    import_name: str


CORE_PACKAGES = (
    PackageSpec("requests", "requests"),
    PackageSpec("beautifulsoup4", "bs4"),
    PackageSpec("lxml", "lxml"),
    PackageSpec("markdownify", "markdownify"),
    PackageSpec("tiktoken", "tiktoken"),
)
BROWSER_COMMANDS = (
    ("agent-browser", "agent-browser", "--version"),
    ("playwright-cli", "playwright-cli", "--version"),
    ("playwright", "playwright", "--version"),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check human-search dependencies and optionally repair them."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Repair the selected component. Without --component, repair all components.",
    )
    parser.add_argument(
        "--component",
        choices=COMPONENTS,
        help="Limit checking or repair to one component (default: report all).",
    )
    return parser


def check_python_package(spec: PackageSpec) -> tuple[bool, str]:
    try:
        importlib.import_module(spec.import_name)
        return True, ""
    except (ImportError, OSError) as exc:
        return False, str(exc)


def resolve_command(name: str) -> str | None:
    executable = shutil.which(name)
    if executable and sys.platform == "win32":
        base = executable[:-4] if executable.lower().endswith(".ps1") else executable
        wrapper = base + ".cmd"
        if os.path.exists(wrapper):
            return wrapper
    return executable


def run_command(
    command: Sequence[str], timeout: int = 30, cwd: str | Path | None = None
) -> tuple[bool, str]:
    executable = resolve_command(command[0])
    if executable is None:
        return False, f"{command[0]} is not on PATH"
    try:
        result = subprocess.run(
            [executable, *command[1:]],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            cwd=cwd,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)
    detail = (result.stdout or result.stderr).strip()
    if result.returncode != 0:
        return False, detail or f"exit code {result.returncode}"
    return True, detail


def probe_browser(label: str, command: str) -> tuple[bool, str]:
    """Launch a disposable local page instead of trusting a version string."""
    if label == "playwright":
        with tempfile.TemporaryDirectory() as directory:
            screenshot = str(Path(directory) / "probe.png")
            return run_command((command, "screenshot", "about:blank", screenshot), timeout=60)

    with tempfile.TemporaryDirectory() as directory:
        ok, help_text = run_command((command, "--help"), cwd=directory)
        if not ok or "open" not in help_text:
            return False, help_text or "browser help does not advertise an open command"
        if "--session" not in help_text:
            return False, "browser cannot isolate a disposable health-check session"
        session = f"human-search-probe-{Path(directory).name}"
        if label == "playwright-cli":
            if "session-stop" not in help_text:
                return False, "browser help does not advertise session cleanup"
            open_command = (command, "--session", session, "open", "about:blank")
            close_command = (command, "session-stop", session)
        else:
            if "close" not in help_text:
                return False, "browser help does not advertise a close command"
            open_command = (command, "--session", session, "open", "about:blank")
            close_command = (command, "--session", session, "close")
        opened, detail = run_command(open_command, timeout=60, cwd=directory)
        if not opened:
            return False, detail
        closed, close_detail = run_command(close_command, timeout=60, cwd=directory)
        if not closed:
            return False, f"browser opened but cleanup failed: {close_detail}"
        return True, detail


def install_python_packages(specs: Iterable[PackageSpec]) -> tuple[bool, str]:
    packages = [spec.distribution for spec in specs]
    if not packages:
        return True, ""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", *packages],
        capture_output=True,
        text=True,
        check=False,
    )
    detail = (result.stderr or result.stdout).strip()
    return result.returncode == 0, detail


def install_browser() -> tuple[bool, str]:
    npm = resolve_command("npm")
    if npm is None:
        return False, "Node.js/npm is required but is not on PATH"
    install = subprocess.run(
        [npm, "install", "-g", "@playwright/cli@latest"],
        capture_output=True,
        text=True,
        check=False,
    )
    if install.returncode != 0:
        return False, (install.stderr or install.stdout).strip()
    ok, detail = run_command(("playwright-cli", "--version"))
    if not ok:
        return False, detail
    ok, detail = run_command(("playwright-cli", "install-browser"), timeout=300)
    if not ok:
        return False, detail
    return probe_browser("playwright-cli", "playwright-cli")


def print_status(status: str, name: str, detail: str = "") -> None:
    suffix = f": {detail}" if detail else ""
    print(f"  [{status}] {name}{suffix}")


def ensure_packages(
    name: str, specs: Sequence[PackageSpec], repair: bool
) -> bool:
    missing = []
    for spec in specs:
        ok, detail = check_python_package(spec)
        print_status(STATUS_OK if ok else STATUS_MISSING, spec.distribution, detail)
        if not ok:
            missing.append(spec)
    if not missing:
        return True
    if not repair:
        return False
    installed, detail = install_python_packages(missing)
    if not installed:
        print_status(STATUS_FAILED, name, detail[-500:])
        return False
    repaired = True
    for spec in missing:
        ok, check_detail = check_python_package(spec)
        print_status(STATUS_REPAIRED if ok else STATUS_FAILED, spec.distribution, check_detail)
        repaired = repaired and ok
    return repaired


def check_browser() -> tuple[bool, str]:
    failures = []
    for label, *command in BROWSER_COMMANDS:
        ok, detail = run_command(command)
        if ok:
            healthy, probe_detail = probe_browser(label, command[0])
            if healthy:
                return True, f"{label} {detail}".strip()
            detail = probe_detail
        failures.append(f"{label}: {detail}")
    return False, "; ".join(failures)


def ensure_browser(repair: bool) -> bool:
    ok, detail = check_browser()
    print_status(STATUS_OK if ok else STATUS_MISSING, "browser", detail)
    if ok or not repair:
        return ok
    installed, detail = install_browser()
    if not installed:
        print_status(STATUS_FAILED, "browser", detail[-500:])
        return False
    ok, detail = check_browser()
    print_status(STATUS_REPAIRED if ok else STATUS_FAILED, "browser", detail)
    return ok


def report_optional_services() -> None:
    print("\n[Optional services]")
    try:
        import requests
    except ImportError:
        print_status(STATUS_OPTIONAL, "SearXNG", "requests is unavailable")
        return
    for name, url in (
        ("SearXNG adapter", "http://localhost:8000/health"),
        ("SearXNG UI", "http://localhost:8999"),
    ):
        try:
            response = requests.get(url, timeout=2)
            if response.ok:
                print_status(STATUS_OK, name)
            else:
                print_status(STATUS_OPTIONAL, name, f"HTTP {response.status_code}")
        except requests.RequestException as exc:
            print_status(STATUS_OPTIONAL, name, str(exc))


def selected_components(args: argparse.Namespace) -> tuple[str, ...]:
    if args.component and args.component != "all":
        return (args.component,)
    return ("core", "browser")


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    selected = selected_components(args)
    results: dict[str, bool] = {}
    print("Human Search dependency status")

    if "core" in selected:
        print("\n[Core]")
        results["core"] = ensure_packages("core", CORE_PACKAGES, args.fix)
    if "browser" in selected:
        print("\n[Browser]")
        results["browser"] = ensure_browser(args.fix)

    if args.component in {None, "all"}:
        report_optional_services()

    if args.component or args.fix:
        required = selected
    else:
        required = ("core",)
    failed = [component for component in required if not results.get(component, False)]
    if failed:
        print(f"\n[FAILED] Required component(s): {', '.join(failed)}")
        return 1
    print("\n[OK] Requested dependencies are ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

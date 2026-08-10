from __future__ import annotations

import contextlib
import importlib
import io
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "skills" / "human-search" / "references"
sys.path.insert(0, str(REFERENCES))

quick_scrape = importlib.import_module("quick_scrape")
test_deps = importlib.import_module("test_deps")


class DependencyTests(unittest.TestCase):
    def test_beautifulsoup_repair_reuses_bs4_import_name(self):
        spec = test_deps.PackageSpec("beautifulsoup4", "bs4")
        checks = []

        def check(package):
            checks.append(package.import_name)
            return (len(checks) > 1, "missing" if len(checks) == 1 else "")

        with mock.patch.object(test_deps, "check_python_package", side_effect=check), mock.patch.object(
            test_deps, "install_python_packages", return_value=(True, "")
        ):
            self.assertTrue(test_deps.ensure_packages("core", (spec,), repair=True))
        self.assertEqual(checks, ["bs4", "bs4"])

    def test_default_check_uses_core_for_exit_status(self):
        with mock.patch.object(test_deps, "ensure_packages", return_value=True), mock.patch.object(
            test_deps, "ensure_browser", return_value=False
        ), mock.patch.object(test_deps, "report_optional_services"):
            self.assertEqual(test_deps.main([]), 0)

    def test_check_only_never_invokes_installers(self):
        with mock.patch.object(test_deps, "ensure_packages", return_value=True) as packages, mock.patch.object(
            test_deps, "ensure_browser", return_value=True
        ) as browser, mock.patch.object(test_deps, "report_optional_services"):
            self.assertEqual(test_deps.main([]), 0)
        self.assertTrue(all(call.args[-1] is False for call in packages.call_args_list))
        self.assertTrue(all(call.args[-1] is False for call in browser.call_args_list))

    def test_bare_fix_repairs_all_components(self):
        with mock.patch.object(test_deps, "ensure_packages", return_value=True) as packages, mock.patch.object(
            test_deps, "ensure_browser", return_value=True
        ) as browser, mock.patch.object(test_deps, "report_optional_services"):
            self.assertEqual(test_deps.main(["--fix"]), 0)
        self.assertEqual(packages.call_count, 1)
        self.assertTrue(all(call.args[-1] is True for call in packages.call_args_list))
        browser.assert_called_once_with(True)

    def test_browser_version_without_launch_is_unhealthy(self):
        with mock.patch.object(
            test_deps,
            "run_command",
            side_effect=[
                (True, "1.0"),
                (True, "open close"),
                (False, "browser executable missing"),
                (False, "missing"),
                (False, "missing"),
            ],
        ):
            ok, detail = test_deps.check_browser()
        self.assertFalse(ok)
        self.assertIn("browser executable missing", detail)

    def test_invalid_component_returns_argparse_exit_two(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            test_deps.main(["--component", "invalid"])
        self.assertEqual(raised.exception.code, 2)

    def test_nonzero_command_is_unhealthy(self):
        completed = mock.Mock(returncode=3221226505, stdout="0.0.1", stderr="")
        with mock.patch.object(test_deps.shutil, "which", return_value="tool"), mock.patch.object(
            test_deps.subprocess, "run", return_value=completed
        ):
            ok, _ = test_deps.run_command(("tool", "--version"))
        self.assertFalse(ok)

    def test_windows_command_resolution_prefers_cmd_wrapper(self):
        with mock.patch.object(test_deps.shutil, "which", return_value=r"C:\tools\playwright.ps1"), mock.patch.object(
            test_deps.os.path, "exists", return_value=True
        ), mock.patch.object(test_deps.sys, "platform", "win32"):
            self.assertEqual(
                test_deps.resolve_command("playwright"), r"C:\tools\playwright.cmd"
            )

    def test_windows_extensionless_node_shim_prefers_cmd_wrapper(self):
        with mock.patch.object(test_deps.shutil, "which", return_value=r"C:\tools\playwright"), mock.patch.object(
            test_deps.os.path, "exists", return_value=True
        ), mock.patch.object(test_deps.sys, "platform", "win32"):
            self.assertEqual(
                test_deps.resolve_command("playwright"), r"C:\tools\playwright.cmd"
            )

    def test_linux_command_resolution_keeps_executable(self):
        with mock.patch.object(test_deps.shutil, "which", return_value="/usr/bin/playwright"), mock.patch.object(
            test_deps.sys, "platform", "linux"
        ):
            self.assertEqual(test_deps.resolve_command("playwright"), "/usr/bin/playwright")


class QuickScrapeTests(unittest.TestCase):
    def test_rejects_search_text_as_url(self):
        result = quick_scrape.scrape("best Python tutorials")
        self.assertEqual(result["reason"], "invalid-url")

    def test_reports_non_html(self):
        response = mock.Mock()
        response.headers = {"Content-Type": "application/pdf"}
        response.raise_for_status.return_value = None
        with mock.patch.object(quick_scrape.requests, "get", return_value=response):
            result = quick_scrape.scrape("https://example.com/file.pdf")
        self.assertEqual(result["reason"], "non-html")

    def test_captcha_word_in_script_does_not_block_visible_content(self):
        response = mock.Mock()
        response.url = "https://example.com/"
        response.headers = {"Content-Type": "text/html"}
        response.text = "<html><title>Example</title><body>Useful article text<script>captcha</script></body></html>"
        response.raise_for_status.return_value = None
        with mock.patch.object(quick_scrape.requests, "get", return_value=response):
            result = quick_scrape.scrape("https://example.com/")
        self.assertNotIn("error", result)


if __name__ == "__main__":
    unittest.main()

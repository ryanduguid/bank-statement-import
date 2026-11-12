# Copyright 2026 Ryan Duguid
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Exercise the import hook through ordinary interpreter startup and imports."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ImportHookTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="oca-import-hook-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = self.root / "odoo"
        (self.package / "tests").mkdir(parents=True)
        (self.package / "__init__.py").write_text("")
        (self.package / "tests" / "__init__.py").write_text("")
        self.receipts = self.root / "receipts"

    def run_import(self, major, *, expected=None, configured=True, common="module"):
        (self.package / "release.py").write_text(f"version_info = ({major}, 0)\n")
        if common == "module":
            (self.package / "tests" / "common.py").write_text(
                "HOST = '127.0.0.1'\n"
                "ORDINARY_LOADER_RAN = True\n"
                "class ChromeBrowser:\n"
                "    def _websocket_request(self, method, *, params):\n"
                "        return {}\n"
            )
        elif common == "namespace":
            (self.package / "tests" / "common").mkdir()
        environment = {
            "PYTHONPATH": os.pathsep.join((str(Path(__file__).parent), str(self.root)))
        }
        if process_config := os.environ.get("COVERAGE_PROCESS_CONFIG"):
            environment["COVERAGE_PROCESS_CONFIG"] = process_config
        if os.name == "nt":
            environment["SystemRoot"] = os.environ["SystemRoot"]
        if configured:
            environment["OCA_JS_COVERAGE_DIR"] = str(self.receipts)
            environment["OCA_JS_COVERAGE_MAJOR"] = str(
                major if expected is None else expected
            )
        return subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                "from odoo.tests import common; assert common.ORDINARY_LOADER_RAN",
            ],
            cwd=Path(__file__).resolve().parents[2],
            env=environment,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )

    def test_supported_hosts_run_the_ordinary_loader_and_install_the_hook(self):
        for major in (18, 19):
            with self.subTest(major=major):
                result = self.run_import(major)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
                receipts = list(self.receipts.glob(f"installed-*-odoo{major}.txt"))
                self.assertEqual(len(receipts), 1)
                self.assertEqual(
                    receipts[0].read_text(),
                    f"Native Odoo {major} browser coverage hook installed\n",
                )

    def test_unconfigured_startup_leaves_ordinary_imports_alone(self):
        result = self.run_import(19, configured=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertFalse(self.receipts.exists())

    def test_a_different_host_major_is_refused_before_installation(self):
        result = self.run_import(19, expected=18)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Native Odoo major differs from requested lifecycle", result.stderr
        )
        self.assertFalse(self.receipts.exists())

    def test_an_unsupported_host_is_refused_before_installation(self):
        result = self.run_import(20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unsupported native Odoo browser lifecycle", result.stderr)
        self.assertFalse(self.receipts.exists())

    def test_a_missing_common_module_is_refused(self):
        result = self.run_import(19, common="missing")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Native Odoo common module unavailable", result.stderr)
        self.assertFalse(self.receipts.exists())

    def test_a_common_namespace_without_a_loader_is_refused(self):
        result = self.run_import(19, common="namespace")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Native Odoo common module unavailable", result.stderr)
        self.assertFalse(self.receipts.exists())

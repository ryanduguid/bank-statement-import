# Copyright 2026 Ryan Duguid
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""The native Python report must retain tracked code that no test imported."""

import runpy
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import coverage


class PythonReportTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="oca-python-report-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        addon = self.root / "fabricated_addon"
        addon.mkdir()
        (addon / "__manifest__.py").write_text("{'name': 'Fabricated addon'}\n")
        (addon / "__init__.py").write_text("")
        self.loaded = addon / "loaded.py"
        self.loaded.write_text("answer = 17\n")
        self.unloaded = addon / "unloaded.py"
        self.unloaded.write_text(
            "def choose(value):\n    if value:\n        return 11\n    return 13\n"
        )
        self.git("init", "--quiet")
        self.git("add", "--", ".")
        self.data_file = self.root / "native.coverage"
        self.output = self.root / "coverage.xml"
        collector = coverage.Coverage(
            data_file=str(self.data_file),
            config_file=False,
            branch=True,
            include=[str(self.root / "*")],
        )
        collector.start()
        try:
            runpy.run_path(str(self.loaded))
        finally:
            collector.stop()
            collector.save()

    def git(self, *arguments):
        subprocess.run(
            ["git", "-C", str(self.root), *arguments],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )

    def report(self):
        return subprocess.run(
            [
                sys.executable,
                str(Path(__file__).with_name("python_report.py")),
                str(self.root),
                str(self.data_file),
                str(self.output),
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )

    def test_unloaded_code_has_real_zero_lines_and_branches(self):
        result = self.report()
        self.assertEqual(result.returncode, 0, result.stderr)
        classes = {
            item.attrib["filename"].replace("\\", "/"): item
            for item in ET.parse(self.output).findall(".//class")
        }
        unloaded = next(
            item for name, item in classes.items() if name.endswith("/unloaded.py")
        )
        self.assertTrue(unloaded.findall(".//line"))
        self.assertTrue(
            all(line.attrib["hits"] == "0" for line in unloaded.findall(".//line"))
        )
        self.assertEqual(unloaded.attrib["branch-rate"], "0")
        branches = unloaded.findall(".//line[@branch='true']")
        self.assertTrue(branches)
        self.assertTrue(
            all(line.attrib["condition-coverage"] == "0% (0/2)" for line in branches)
        )
        self.assertFalse(any(name.endswith("/__manifest__.py") for name in classes))

    def test_a_new_python_source_outside_the_collected_groups_is_refused(self):
        (self.root / "maintenance.py").write_text("answer = 29\n")
        self.git("add", "--", "maintenance.py")
        result = self.report()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Uncollected Python source", result.stderr)

    def test_executable_metadata_is_refused(self):
        for content in (
            "dict(name='Not literal metadata')\n",
            "['Not a dictionary']\n",
        ):
            with self.subTest(content=content):
                (self.root / "fabricated_addon" / "__manifest__.py").write_text(content)
                result = self.report()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Manifest must be a literal dictionary", result.stderr)

    def test_a_link_to_external_source_is_refused(self):
        with tempfile.TemporaryDirectory(prefix="oca-external-source-") as outside:
            target = Path(outside) / "private.py"
            target.write_text("answer = 31\n")
            self.unloaded.unlink()
            try:
                self.unloaded.symlink_to(target)
            except OSError:
                self.skipTest("This host does not permit file symlinks")
            result = self.report()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Python source must be a regular owned file", result.stderr)
            self.assertFalse(self.output.exists())

    def test_an_empty_addon_inventory_is_refused(self):
        self.git("rm", "--cached", "--", "fabricated_addon/__manifest__.py")
        result = self.report()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No Odoo addon source inventory", result.stderr)

    def test_missing_native_data_cannot_be_replaced_by_a_zero_report(self):
        self.data_file.unlink()
        result = self.report()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Native Python coverage is missing", result.stderr)
        self.assertFalse(self.output.exists())

    def test_invalid_cli_arguments_fail_before_source_or_data_access(self):
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("python_report.py"))],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Usage: python_report.py", result.stderr)
        self.assertFalse(self.output.exists())

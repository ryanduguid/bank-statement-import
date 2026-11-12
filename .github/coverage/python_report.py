# Copyright 2026 Ryan Duguid
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Retain every tracked addon source, including code no test imported."""

import ast
import subprocess
import sys
from pathlib import Path

import coverage


def addon_sources(root):
    tracked = (
        subprocess.check_output(
            ["git", "-C", str(root), "ls-files", "-z", "--", "*.py"],
            timeout=15,
        )
        .decode("utf-8")
        .split("\0")
    )
    paths = [Path(name) for name in tracked if name]
    for relative in paths:
        path = root / relative
        if (
            path.is_symlink()
            or not path.resolve().is_relative_to(root)
            or not path.is_file()
        ):
            raise RuntimeError(
                f"Python source must be a regular owned file: {relative}"
            )
    manifests = {
        path
        for path in paths
        if len(path.parts) == 2 and path.name == "__manifest__.py"
    }
    if not manifests:
        raise RuntimeError("No Odoo addon source inventory")
    for manifest in manifests:
        try:
            metadata = ast.literal_eval((root / manifest).read_text(encoding="utf-8"))
        except (SyntaxError, ValueError) as error:
            raise RuntimeError("Manifest must be a literal dictionary") from error
        if not isinstance(metadata, dict):
            raise RuntimeError("Manifest must be a literal dictionary")
    addons = {manifest.parts[0] for manifest in manifests}
    sources = []
    for path in paths:
        if path in manifests or path.parts[:2] == (".github", "coverage"):
            continue
        if path.parts[0] not in addons:
            raise RuntimeError(f"Uncollected Python source: {path}")
        sources.append(str((root / path).resolve()))
    return sources


def write_report(root, data_file, output):
    sources = addon_sources(Path(root).resolve())
    collector = coverage.Coverage(data_file=data_file)
    collector.load()
    if not collector.get_data().measured_files():
        raise RuntimeError("Native Python coverage is missing")
    collector.get_data().touch_files(sources)
    collector.save()
    collector.xml_report(outfile=output)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("Usage: python_report.py source-root coverage-data output-xml")
    write_report(*sys.argv[1:])

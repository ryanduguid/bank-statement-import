# Copyright 2026 Ryan Duguid
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Enable the coverage-only hook for one explicitly configured native process."""

import importlib.abc
import importlib.machinery
import os
import sys

destination = os.environ.get("OCA_JS_COVERAGE_DIR")
if destination:

    class CoverageImport(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path, target=None):
            if fullname != "odoo.tests.common":
                return None
            spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
            if spec is None or spec.loader is None:
                raise ImportError("Native Odoo common module unavailable")
            loader = spec.loader

            class CoverageLoader(importlib.abc.Loader):
                def create_module(self, selected):
                    return loader.create_module(selected)

                def exec_module(self, module):
                    loader.exec_module(module)
                    from odoo_coverage import install

                    from odoo import release

                    major = release.version_info[0]
                    expected = int(os.environ["OCA_JS_COVERAGE_MAJOR"])
                    if major != expected:
                        raise RuntimeError(
                            "Native Odoo major differs from requested lifecycle"
                        )
                    install(module, destination, major)

            spec.loader = CoverageLoader()
            sys.meta_path.remove(self)
            return spec

    sys.meta_path.insert(0, CoverageImport())

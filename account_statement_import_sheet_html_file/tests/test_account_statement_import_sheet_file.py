# Copyright 2019 ForgeFlow, S.L.
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# Copyright 2025 Tecnativa - Pedro M. Baeza
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2025 Simone Rubino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date
from unittest.mock import patch

from odoo.tools import file_open

from .common import Common


class TestAccountStatementImportSheetFile(Common):
    def test_import_html_file(self):
        """Import an XLS[X] file that is actually an HTML file."""
        wizard = self._get_import_wizard("data/sample_statement_html.xlsx")
        wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertRecordValues(
            statement.line_ids,
            [
                {
                    "date": date(2025, month=1, day=15),
                    "payment_ref": "Line description",
                    "partner_name": "Azure Interior",
                    "amount": -200.20,
                },
            ],
        )

    def test_html_wrappers_preserve_nested_cell_text(self):
        self.sample_statement_map.file_encoding = False
        for opening in (
            "<html>",
            '<!DOCTYPE html><html lang="en">',
            '<html lang="en">',
        ):
            document = (
                opening + "<table><tr><th>Amount</th></tr>"
                "<tr><td><span>Café</span> 100.00</td></tr></table></html>"
            )
            with self.subTest(opening=opening):
                records = self.parser._parse_data_html(
                    self.sample_statement_map, document.encode()
                )
                self.assertEqual(list(records), [["Amount"], ["Café 100.00"]])
        self.assertIsNone(
            self.parser._parse_data_html(self.sample_statement_map, b"plain csv")
        )
        self.assertIsNone(
            self.parser._parse_data_html(self.sample_statement_map, b"<html></html>")
        )

    def test_html_respects_configured_and_detected_encodings(self):
        for configured, actual, label in (
            ("windows-1252", "windows-1252", "Café"),
            ("windows-1252", "utf-8", "Ё"),
        ):
            with self.subTest(actual=actual):
                self.sample_statement_map.file_encoding = configured
                html = (
                    f"<html><table><tr><th>Label</th></tr>"
                    f"<tr><td>{label}</td></tr></table></html>"
                ).encode(actual)
                with patch(
                    "odoo.addons.account_statement_import_sheet_file.models"
                    ".account_statement_import_sheet_parser.chardet.detect",
                    return_value={"encoding": actual},
                ) as detect:
                    records = self.parser._parse_data_html(
                        self.sample_statement_map, html
                    )
                self.assertEqual(list(records), [["Label"], [label]])
                self.assertEqual(detect.call_count, int(configured != actual))

    def test_html_decoder_does_not_prevent_legacy_xls_fallback(self):
        self.sample_statement_map.file_encoding = "utf-8"
        with file_open(
            "account_statement_import_sheet_file/tests/fixtures/sample_statement_en.xls",
            "rb",
        ) as file:
            data = file.read()
        with patch(
            "odoo.addons.account_statement_import_sheet_file.models"
            ".account_statement_import_sheet_parser.chardet.detect",
            return_value={"encoding": None},
        ) as detect:
            _book, sheet = self.parser._parse_data(self.sample_statement_map, data)
        detect.assert_called_once_with(data)
        self.assertEqual(sheet.row_values(0)[0], "Date")
        self.assertEqual(sheet.nrows, 3)

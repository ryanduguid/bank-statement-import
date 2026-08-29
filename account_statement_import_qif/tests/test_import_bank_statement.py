# Copyright 2015 Odoo S. A.
# Copyright 2015 Laurent Mignon <laurent.mignon@acsone.eu>
# Copyright 2015 Ronald Portier <rportier@therp.nl>
# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# Copyright 2024 Tecnativa - Víctor Martínez
# Copyright 2026 Ryan Duguid
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
from datetime import date

from odoo.tests.common import TransactionCase
from odoo.tools.misc import file_path


class TestQifFile(TransactionCase):
    """Tests for import bank statement qif file format
    (account.bank.statement.import)
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.statement_import_model = cls.env["account.statement.import"]
        cls.statement_line_model = cls.env["account.bank.statement.line"]
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Test bank journal",
                "code": "TEST",
                "type": "bank",
                "currency_id": cls.env.company.currency_id.id,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                # Different case for trying insensitive case search
                "name": "EPIC Technologies",
            }
        )

    def test_qif_file_import(self):
        qif_file_path = file_path("account_statement_import_qif/tests/test_qif.qif")
        qif_file = base64.b64encode(open(qif_file_path, "rb").read())
        wizard = self.statement_import_model.with_context(
            journal_id=self.journal.id
        ).create({"statement_file": qif_file, "statement_filename": "test_qif.qif"})
        wizard.import_file_button()
        statement = self.statement_line_model.search(
            [("payment_ref", "=", "YOUR LOCAL SUPERMARKET")],
            limit=1,
        ).statement_id
        self.assertAlmostEqual(statement.balance_end_real, -1896.09, 2)
        line = self.statement_line_model.search(
            [("payment_ref", "=", "Epic Technologies")],
            limit=1,
        )
        self.assertEqual(line.partner_id, self.partner)

    def _parse_qif_transactions(self, qif_bytes):
        wizard = self.statement_import_model.with_context(
            journal_id=self.journal.id
        ).create(
            {
                "statement_file": base64.b64encode(qif_bytes),
                "statement_filename": "test.qif",
            }
        )
        _currency, _account, stmts = wizard._parse_file(qif_bytes)
        return stmts[0]["transactions"]

    def test_qif_us_mdy_dates_from_unambiguous_day(self):
        """Keep US month-first dates when the file has a day > 12."""
        qif_file_path = file_path("account_statement_import_qif/tests/test_qif.qif")
        with open(qif_file_path, "rb") as qif_file:
            transactions = self._parse_qif_transactions(qif_file.read())
        self.assertEqual(transactions[0]["date"], date(2013, 8, 12))
        self.assertEqual(transactions[1]["date"], date(2013, 8, 15))

    def test_qif_australian_dmy_dates_from_unambiguous_day(self):
        """Respect dd/mm/yyyy when a day > 12 makes the order unambiguous.

        Regression for https://github.com/OCA/bank-statement-import/issues/982
        """
        qif = (
            b"!Type:Bank\n"
            b"D31/07/2026\n"
            b"T60.00\n"
            b"PTransaction 1\n"
            b"^\n"
            b"D08/07/2026\n"
            b"T360.00\n"
            b"PTransaction 2\n"
            b"^\n"
            b"D01/07/2026\n"
            b"T0.00\n"
            b"PTransaction 3\n"
            b"^\n"
        )
        self.env.company.country_id = self.env.ref("base.us")
        transactions = self._parse_qif_transactions(qif)
        self.assertEqual(
            [line["date"] for line in transactions],
            [date(2026, 7, 31), date(2026, 7, 8), date(2026, 7, 1)],
        )

    def test_qif_ambiguous_dates_follow_company_country(self):
        qif = (
            b"!Type:Bank\nD08/07/2026\nT10.00\nPOne\n^\nD01/06/2026\nT20.00\nPTwo\n^\n"
        )
        self.env.company.country_id = self.env.ref("base.us")
        us_dates = [line["date"] for line in self._parse_qif_transactions(qif)]
        self.assertEqual(us_dates, [date(2026, 8, 7), date(2026, 1, 6)])

        self.env.company.country_id = self.env.ref("base.au")
        au_dates = [line["date"] for line in self._parse_qif_transactions(qif)]
        self.assertEqual(au_dates, [date(2026, 7, 8), date(2026, 6, 1)])

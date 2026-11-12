import base64
import datetime

import odoo.tests.common as common
from odoo.exceptions import UserError
from odoo.tools import file_open


class TestOfxFile(common.TransactionCase):
    """Tests for import bank statement ofx file format
    (account.bank.statement.import)
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.asi_model = cls.env["account.statement.import"]
        cls.abs_model = cls.env["account.bank.statement"]
        cls.absl_model = cls.env["account.bank.statement.line"]
        cur = cls.env.ref("base.USD")
        bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "123456",
                "partner_id": cls.env.ref("base.main_partner").id,
                "company_id": cls.env.ref("base.main_company").id,
                "bank_id": cls.env.ref("base.res_bank_1").id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Bank Journal TEST OFX",
                "code": "BNK12",
                "type": "bank",
                "bank_account_id": bank.id,
                "currency_id": cur.id,
            }
        )
        bank_iban_ofx = cls.env["res.partner.bank"].create(
            {
                "acc_number": "FR7630001007941234567890185",
                "partner_id": cls.env.ref("base.main_partner").id,
                "company_id": cls.env.ref("base.main_company").id,
                "bank_id": cls.env.ref("base.res_bank_1").id,
            }
        )
        cls.env["account.journal"].create(
            {
                "name": "FR7630001007941234567890185",
                "code": "BNK13",
                "type": "bank",
                "bank_account_id": bank_iban_ofx.id,
                "currency_id": cur.id,
            }
        )

    def test_wrong_ofx_file_import(self):
        ofx_path = "account_statement_import_ofx/tests/test_ofx_file/test_ofx_wrong.ofx"
        with file_open(ofx_path, "rb") as ofx_file:
            ofx_bin_wrong = ofx_file.read()
            wizard = self.asi_model.create(
                {
                    "statement_file": base64.b64encode(ofx_bin_wrong),
                    "statement_filename": "test_ofx_wrong.ofx",
                }
            )
            self.assertFalse(wizard._check_ofx(data_file=ofx_bin_wrong))

    def test_ofx_file_import(self):
        ofx_path = "account_statement_import_ofx/tests/test_ofx_file/test_ofx.ofx"
        with file_open(ofx_path, "rb") as ofx_file:
            ofx_bin = ofx_file.read()
            wizard = self.asi_model.create(
                {
                    "statement_file": base64.b64encode(ofx_bin),
                    "statement_filename": "test_ofx.ofx",
                }
            )
            wizard.import_file_button()
            bank_st_record = self.abs_model.search([("name", "like", "123456")])[0]
            self.assertEqual(bank_st_record.balance_start, 2516.56)
            self.assertEqual(bank_st_record.balance_end_real, 2156.56)

            line = self.absl_model.search(
                [
                    ("payment_ref", "=", "Agrolait"),
                    ("statement_id", "=", bank_st_record.id),
                ]
            )[0]
            self.assertEqual(line.date, datetime.date(2013, 8, 24))

    def test_overlapping_uploads_keep_new_lines_balances_and_source_files(self):
        path = "account_statement_import_ofx/tests/test_ofx_file/test_ofx.ofx"
        with file_open(path, "rb") as source:
            original = source.read()
        start = original.index(b"<BANKTRANLIST>")
        first_end = original.index(b"</BANKTRANLIST>") + len(b"</BANKTRANLIST>")
        balance_start = original.index(b"<LEDGERBAL>")
        template = original[start:first_end]
        extra = template.replace(b"<TRNAMT>-80</TRNAMT>", b"<TRNAMT>-10</TRNAMT>")
        extra = extra.replace(b"<FITID>219378</FITID>", b"<FITID>fixture-E</FITID>")
        extra = extra.replace(b"<NAME>Agrolait</NAME>", b"<NAME>Fixture E</NAME>")
        final = extra.replace(b"<TRNAMT>-10</TRNAMT>", b"<TRNAMT>-5</TRNAMT>")
        final = final.replace(b"fixture-E", b"fixture-F").replace(
            b"Fixture E", b"Fixture F"
        )
        overlapping = original[:balance_start] + extra + original[balance_start:]
        overlapping = overlapping.replace(b"2156.56", b"2146.56", 1)
        rolling = original[:start] + extra + final + original[balance_start:]
        rolling = rolling.replace(b"2156.56", b"2141.56", 1)
        action = self.journal.import_account_statement()
        self.assertEqual(action["res_model"], "account.statement.import")
        self.assertEqual(action["context"], {"journal_id": self.journal.id})
        self.journal.bank_statements_source = "undefined"
        statements = self.abs_model.browse()
        for data, name, opening, closing, ids, warning in (
            (
                original,
                "original.ofx",
                2516.56,
                2156.56,
                ["219378", "219379", "219380", "219381"],
                None,
            ),
            (
                overlapping,
                "overlapping.ofx",
                2156.56,
                2146.56,
                ["fixture-E"],
                "4 transactions had already been imported and were ignored.",
            ),
            (
                rolling,
                "rolling.ofx",
                2146.56,
                2141.56,
                ["fixture-F"],
                "1 transaction had already been imported and was ignored.",
            ),
        ):
            wizard = self.asi_model.with_context(**action["context"]).create(
                {
                    "statement_file": base64.b64encode(data),
                    "statement_filename": name,
                }
            )
            result = wizard.import_file_button()
            statement = (
                self.abs_model.search([("journal_id", "=", self.journal.id)])
                - statements
            )
            self.assertEqual(len(statement), 1)
            statements |= statement
            self.assertAlmostEqual(statement.balance_start, opening, places=2)
            self.assertAlmostEqual(statement.balance_end_real, closing, places=2)
            prefix = f"123456-{self.journal.id}-"
            self.assertCountEqual(
                statement.line_ids.mapped("unique_import_id"),
                [prefix + identifier for identifier in ids],
            )
            if warning:
                self.assertEqual(result["type"], "ir.actions.client")
                self.assertEqual(result["tag"], "display_notification")
                self.assertEqual(result["params"]["type"], "warning")
                self.assertTrue(result["params"]["sticky"])
                self.assertEqual(result["params"]["message"], warning)
                result = result["params"]["next"]
            self.assertEqual(result["domain"], [("id", "in", statement.ids)])
            attachment = statement.attachment_ids
            self.assertEqual(len(attachment), 1)
            self.assertEqual(attachment.name, name)
            self.assertEqual(attachment.company_id, self.journal.company_id)
            self.assertEqual(attachment.res_model, "account.bank.statement")
            self.assertEqual(attachment.res_id, statement.id)
            self.assertEqual(base64.b64decode(attachment.datas), data)
        self.assertEqual(self.journal.bank_statements_source, "file_import_oca")
        self.assertEqual(len(statements.line_ids), 6)
        self.assertEqual(len(set(statements.line_ids.mapped("unique_import_id"))), 6)
        self.assertEqual(len(statements.attachment_ids), 3)
        for statement, (opening, closing) in zip(
            statements,
            [(2516.56, 2156.56), (2156.56, 2146.56), (2146.56, 2141.56)],
            strict=True,
        ):
            self.assertAlmostEqual(statement.balance_start, opening, places=2)
            self.assertAlmostEqual(statement.balance_end_real, closing, places=2)
        wizard = self.asi_model.with_context(**action["context"]).create(
            {
                "statement_file": base64.b64encode(rolling),
                "statement_filename": "repeat.ofx",
            }
        )
        attachment_count = self.env["ir.attachment"].search_count([])
        with (
            self.assertRaisesRegex(UserError, "already imported"),
            self.env.cr.savepoint(),
        ):
            wizard.import_file_button()
        self.assertCountEqual(
            self.abs_model.search([("journal_id", "=", self.journal.id)]).ids,
            statements.ids,
        )
        self.assertEqual(
            self.absl_model.search_count([("journal_id", "=", self.journal.id)]), 6
        )
        self.assertEqual(self.env["ir.attachment"].search_count([]), attachment_count)

    def no_test_check_journal_bank_account(self):
        ofx_path = "account_statement_import_ofx/tests/test_ofx_file/test_ofx_iban.ofx"
        with file_open(ofx_path, "rb") as ofx_file:
            ofx_bin = ofx_file.read()
            wizard = self.asi_model.create(
                {
                    "statement_file": base64.b64encode(ofx_bin),
                    "statement_filename": "test_ofx_iban.ofx",
                }
            )
            wizard.import_file_button()

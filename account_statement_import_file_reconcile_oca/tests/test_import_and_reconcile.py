# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).

from base64 import b64encode
from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestImportAndReconcile(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env["account.journal"].create(
            {"name": "Reconciliation import test", "code": "RCIMP", "type": "bank"}
        )
        import_action = cls.journal.import_account_statement()
        cls.wizard = (
            cls.env["account.statement.import"]
            .with_context(**import_action["context"])
            .create(
                {
                    "statement_file": b64encode(b"Synthetic bank statement"),
                    "statement_filename": "statement.txt",
                }
            )
        )

    def _import(self, *transaction_ids):
        statement = {
            "transactions": [
                {
                    "date": "2024-04-05",
                    "payment_ref": transaction_id,
                    "amount": 25,
                    "unique_import_id": transaction_id,
                }
                for transaction_id in transaction_ids
            ],
        }
        currency = self.journal.currency_id or self.journal.company_id.currency_id
        with patch.object(
            type(self.wizard),
            "_parse_file",
            return_value=(currency.name, None, [statement]),
        ):
            return self.wizard.import_file_and_reconcile_button()

    def _assert_reconciliation_action(self, action):
        expected = self.env["ir.actions.actions"]._for_xml_id(
            "account_reconcile_oca.action_bank_statement_line_reconcile"
        )
        self.assertEqual(action["id"], expected["id"])
        self.assertEqual(action["type"], expected["type"])
        self.assertEqual(action.get("tag"), expected.get("tag"))
        self.assertEqual(action["context"]["default_journal_id"], self.journal.id)
        self.assertEqual(action["context"]["active_ids"], self.journal.ids)
        self.assertTrue(action["context"]["search_default_not_reconciled"])

    def test_import_opens_journal_reconciliation(self):
        action = self._import("first")
        self._assert_reconciliation_action(action)
        transactions = self.env["account.bank.statement.line"].search(
            [("journal_id", "=", self.journal.id)]
        )
        self.assertEqual(transactions.mapped("payment_ref"), ["first"])

    def test_duplicate_warning_continues_to_reconciliation(self):
        self._import("first")
        action = self._import("first", "second")
        self.assertEqual(action["type"], "ir.actions.client")
        self.assertEqual(action["tag"], "display_notification")
        notification = action["params"]
        self.assertEqual(notification["type"], "warning")
        self.assertIn("1 transaction", notification["message"])
        self._assert_reconciliation_action(notification["next"])
        transactions = self.env["account.bank.statement.line"].search(
            [("journal_id", "=", self.journal.id)]
        )
        self.assertCountEqual(transactions.mapped("payment_ref"), ["first", "second"])

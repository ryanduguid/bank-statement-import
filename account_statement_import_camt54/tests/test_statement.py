# Copyright 2020 Camptocamp SA
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64

from lxml import etree

from odoo.tests.common import TransactionCase
from odoo.tools.misc import file_path


class TestGenerateBankStatement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        eur_currency = cls.env.ref("base.EUR")
        eur_currency.write({"active": True})
        bank = cls.env["res.partner.bank"].create(
            {
                "acc_number": "NL77ABNA0574908765",
                "partner_id": cls.env.ref("base.main_partner").id,
                "company_id": cls.env.ref("base.main_company").id,
                "bank_id": cls.env.ref("base.res_bank_1").id,
            }
        )
        cls.env["res.partner.bank"].create(
            {
                "acc_number": "NL46ABNA0499998748",
                "partner_id": cls.env.ref("base.main_partner").id,
                "company_id": cls.env.ref("base.main_company").id,
                "bank_id": cls.env.ref("base.res_bank_1").id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Bank Journal - (test camt)",
                "code": "TBNKCAMT",
                "type": "bank",
                "bank_account_id": bank.id,
                "currency_id": eur_currency.id,
            }
        )

    def _load_statement(self):
        testfile = file_path("account_statement_import_camt/tests/samples/test-camt054")
        with open(testfile, "rb") as datafile:
            camt_file = base64.b64encode(datafile.read())
            self.env["account.statement.import"].create(
                {
                    "statement_filename": "test import",
                    "statement_file": camt_file,
                }
            ).import_file_button()
            bank_st_record = self.env["account.bank.statement"].search(
                [
                    (
                        "name",
                        "in",
                        ["TBNKC Statement 2022-01-26", "20220120000000000000000"],
                    )
                ],
                limit=1,
            )
            statement_lines = bank_st_record.line_ids
            return statement_lines

    def test_statement_import(self):
        self.journal.transfer_line = True
        lines = self._load_statement()
        self.assertEqual(len(lines), 2)
        self.assertAlmostEqual(sum(lines.mapped("amount")), 0)
        self.journal.transfer_line = False
        lines = self._load_statement()
        self.assertEqual(len(lines), 1)
        self.assertAlmostEqual(sum(lines.mapped("amount")), 5.0)

    def _camt54_document(self):
        path = file_path("account_statement_import_camt/tests/samples/test-camt054")
        with open(path, "rb") as datafile:
            return etree.parse(datafile)

    def _parse_camt54_transaction(self, document):
        currency, account, statements = self.env[
            "account.statement.import.camt.parser"
        ].parse(etree.tostring(document))
        self.assertEqual(currency, "EUR")
        self.assertEqual(account, "NL77ABNA0574908765")
        self.assertEqual(len(statements), 1)
        self.assertEqual(len(statements[0]["transactions"]), 1)
        transaction = statements[0]["transactions"][0]
        self.assertEqual(transaction["amount"], 5.0)
        return transaction

    def test_unstructured_remittance_keeps_the_bank_reconciliation_reference(self):
        document = self._camt54_document()
        remittance = document.find(".//{*}TxDtls/{*}RmtInf")
        self.assertIsNotNone(remittance)
        for child in list(remittance):
            remittance.remove(child)
        namespace = etree.QName(remittance).namespace
        etree.SubElement(remittance, f"{{{namespace}}}Ustrd").text = "Invoice 42"
        transaction = self._parse_camt54_transaction(document)
        self.assertEqual(transaction["payment_ref"], "Invoice 42 (98888208N8)")
        self.assertEqual(transaction["ref"], "98888208N8")

    def test_qr_remittance_extracts_the_configured_partner_reference(self):
        self.env["ir.config_parameter"].set_param("qrr_partner_ref", "27,1")
        transaction = self._parse_camt54_transaction(self._camt54_document())
        self.assertEqual(transaction["payment_ref"], "000000000000000000000000003")
        self.assertEqual(transaction["partner_ref"], "3")
        self.assertEqual(transaction["ref"], "98888208N8")

# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountBankStatementImportMoveLine(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner 2"})
        cls.journal_bank = cls.company_data["default_journal_bank"]
        cls.invoice = cls.init_invoice(
            "out_invoice", partner=cls.partner, amounts=[100]
        )
        cls.statement = cls.env["account.bank.statement"].create(
            {"name": "Test account bank statement import move line"}
        )
        cls.statement.journal_id = cls.journal_bank.id

    def test_global(self):
        self.invoice.action_post()
        self.assertTrue(self.invoice.id)
        wizard_o = self.env["account.statement.line.create"]
        context = wizard_o._context.copy()
        context.update(
            {"active_model": "account.bank.statement", "active_id": self.statement.id}
        )
        wizard = wizard_o.with_context(**context).create(
            {
                "statement_id": self.statement.id,
                "partner_id": self.partner.id,
                "date_type": "move",
                "move_date": fields.Date.today(),
                "invoice": False,
            }
        )
        wizard.populate()
        self.assertEqual(len(wizard.move_line_ids), 1)
        line = wizard.move_line_ids
        self.assertEqual(line.debit, self.invoice.amount_total)
        wizard.create_statement_lines()
        line = self.statement.line_ids[0]
        self.assertEqual(line.amount, self.invoice.amount_total)

    def _assert_payment_lines_are_excluded(self, reset_to_draft):
        self.invoice.action_post()
        payment = self.env["account.payment"].create(
            {
                "journal_id": self.journal_bank.id,
                "payment_method_line_id": self.inbound_payment_method_line.id,
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner.id,
                "amount": 40,
                "date": self.invoice.date,
            }
        )
        payment.action_post()
        self.assertIn(payment.state, ("in_process", "paid"))
        if reset_to_draft:
            payment.action_draft()
            self.assertEqual(payment.state, "draft")
        payment_line = payment.move_id.line_ids.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        self.assertEqual(len(payment_line), 1)
        self.assertFalse(payment_line.reconciled)
        self.assertEqual(payment_line.partner_id, self.partner)
        invoice_line = self.invoice.line_ids.filtered(
            lambda line: line.account_id.account_type == "asset_receivable"
        )
        self.assertEqual(len(invoice_line), 1)
        self.assertFalse(invoice_line.reconciled)
        wizard = self.env["account.statement.line.create"].create(
            {
                "statement_id": self.statement.id,
                "partner_id": self.partner.id,
                "target_move": "all" if reset_to_draft else "posted",
                "date_type": "move",
                "move_date": max(self.invoice.date, payment.date),
                "invoice": False,
            }
        )
        wizard.populate()
        self.assertEqual(wizard.move_line_ids, invoice_line)
        self.assertFalse(wizard.move_line_ids & payment.move_id.line_ids)

    def test_draft_payment_lines_are_not_offered_as_new_statement_entries(self):
        self._assert_payment_lines_are_excluded(reset_to_draft=True)

    def test_confirmed_payment_lines_are_not_offered_as_new_statement_entries(self):
        self._assert_payment_lines_are_excluded(reset_to_draft=False)

    def _vendor_bill(self, amount, due, partner=None, journal=None, posted=True):
        bill = self.init_invoice(
            "in_invoice",
            partner=partner or self.partner,
            invoice_date=fields.Date.today(),
            amounts=[amount],
            taxes=[],
            journal=journal,
        )
        bill.write({"invoice_payment_term_id": False, "invoice_date_due": due})
        if posted:
            bill.action_post()
        return bill

    def test_journal_import_filters_due_bills_and_keeps_the_credit_sign(self):
        cutoff = fields.Date.today()
        bill = self._vendor_bill(40, cutoff)
        purchase = bill.journal_id
        other_journal = purchase.copy(
            {"name": "Fabricated other purchase journal", "code": "FOP"}
        )
        other_partner = self.env["res.partner"].create(
            {"name": "Fabricated other supplier"}
        )
        self._vendor_bill(50, cutoff + timedelta(days=1))
        self._vendor_bill(60, cutoff, partner=other_partner)
        self._vendor_bill(70, cutoff, journal=other_journal)
        self._vendor_bill(80, cutoff, posted=False)
        payable = bill.line_ids.filtered(
            lambda line: line.account_id.account_type == "liability_payable"
        )
        self.assertEqual(len(payable), 1)
        self.assertEqual((payable.debit, payable.credit), (0, 40))
        wizard = (
            self.env["account.statement.line.create"]
            .with_context(
                active_model="account.journal", active_id=self.journal_bank.id
            )
            .create(
                {
                    "journal_ids": [(6, 0, purchase.ids)],
                    "partner_id": self.partner.id,
                    "due_date": cutoff,
                }
            )
        )
        wizard.populate()
        self.assertEqual(wizard.move_line_ids, payable)
        domain = wizard.move_line_filters_change()["domain"]["move_line_ids"]
        self.assertEqual(self.env["account.move.line"].search(domain), payable)
        before = self.env["account.bank.statement"].search([])
        action = wizard.create_statement_lines()
        created = self.env["account.bank.statement"].search([]) - before
        self.assertEqual(created, wizard.statement_id)
        self.assertEqual(len(created), 1)
        self.assertEqual(created.journal_id, self.journal_bank)
        self.assertEqual(len(created.line_ids), 1)
        line = created.line_ids
        self.assertEqual(
            (line.amount, line.partner_id, line.date), (-40, self.partner, cutoff)
        )
        self.assertEqual(
            action,
            {
                "type": "ir.actions.act_window",
                "res_model": "account.bank.statement",
                "view_mode": "form",
                "res_id": created.id,
                "target": "current",
            },
        )

    def test_journal_import_without_selected_lines_creates_nothing(self):
        wizard = (
            self.env["account.statement.line.create"]
            .with_context(
                active_model="account.journal", active_id=self.journal_bank.id
            )
            .create({})
        )
        before = self.env["account.bank.statement"].search([])
        self.assertIs(wizard.create_statement_lines(), True)
        self.assertFalse(wizard.statement_id)
        self.assertEqual(self.env["account.bank.statement"].search([]), before)

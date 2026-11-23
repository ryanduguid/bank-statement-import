# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AccountStatementImport(models.TransientModel):
    """Add process_camt method to account.bank.statement.import."""

    _inherit = "account.statement.import"

    def _create_bank_statement(self, statement_values, creation_context):
        """Balance CAMT.054 notifications on their configured journal."""
        statement = super()._create_bank_statement(statement_values, creation_context)
        if not creation_context.get("camt54_notification"):
            return statement

        amount = sum(statement.line_ids.mapped("amount"))
        if statement.journal_id.transfer_line:
            statement.line_ids.create(
                {
                    "amount": -amount,
                    "statement_id": statement.id,
                    "date": statement.date,
                    "payment_ref": statement.name,
                }
            )
            statement.balance_end_real = statement.balance_start
        else:
            statement.balance_end_real = statement.balance_start + amount
        return statement

    def _complete_stmts_vals(self, stmts_vals, journal, account_number):
        """Search partner from partner reference"""
        stmts_vals = super()._complete_stmts_vals(stmts_vals, journal, account_number)
        line_refs = [
            (line, line.pop("partner_ref"))
            for statement in stmts_vals
            for line in statement["transactions"]
            if "partner_ref" in line
        ]
        references = {reference for _, reference in line_refs if reference}
        if references:
            partner_ids = {}
            for partner in self.env["res.partner"].search_fetch(
                [("ref", "in", list(references))], ["ref"]
            ):
                partner_ids.setdefault(partner.ref, partner.id)
            for line, reference in line_refs:
                if reference in partner_ids:
                    line["partner_id"] = partner_ids[reference]
        return stmts_vals

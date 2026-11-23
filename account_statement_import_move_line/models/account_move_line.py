# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_statement_line_vals(self, statement):
        self.ensure_one()
        currency = statement.currency_id or self.company_currency_id
        if currency == self.company_currency_id:
            amount = self.balance
        elif currency == self.currency_id:
            amount = self.amount_currency
        else:
            amount = self.company_currency_id._convert(
                self.balance, currency, self.company_id, self.date
            )
        vals = {
            "name": self.name or "?",
            "amount": amount,
            "partner_id": self.partner_id.id,
            "statement_id": statement.id,
            "payment_ref": self.ref or self.name,
            "date": self.date_maturity or self.date,
        }
        if currency != self.currency_id:
            vals.update(
                {
                    "foreign_currency_id": self.currency_id.id,
                    "amount_currency": self.amount_currency,
                }
            )
        return vals

    def create_statement_line_from_move_line(self, statement):
        abslo = self.env["account.bank.statement.line"]
        for mline in self:
            abslo.create(mline._prepare_statement_line_vals(statement))
        return

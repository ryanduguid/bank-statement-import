# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountStatementImport(models.TransientModel):
    _inherit = "account.statement.import"

    def _get_default_mapping_id(self):
        return (
            self.env["account.journal"]
            .browse(self.env.context.get("journal_id"))
            .default_sheet_mapping_id
        )

    sheet_mapping_id = fields.Many2one(
        string="Sheet mapping",
        comodel_name="account.statement.import.sheet.mapping",
        default=_get_default_mapping_id,
    )

    def _parse_file(self, data_file):
        self.ensure_one()
        if self.sheet_mapping_id:
            try:
                Parser = self.env["account.statement.import.sheet.parser"]
                return Parser.parse(
                    data_file, self.sheet_mapping_id, self.statement_filename
                )
            except BaseException as exc:
                if self.env.context.get("account_statement_import_sheet_file_test"):
                    raise
                _logger.warning("Sheet parser error", exc_info=True)
                raise UserError(self.env._("Bad file/mapping: ") + str(exc)) from exc
        return super()._parse_file(data_file)

    def _create_bank_statement(self, statement_values, creation_context):
        """Calculate the closing balance when the file leaves it unspecified."""
        reported_balance = statement_values.get("balance_end_real")
        statement = super()._create_bank_statement(statement_values, creation_context)
        has_reported_balance = (
            self.sheet_mapping_id
            and reported_balance is not None
            and reported_balance is not False
        )
        if not has_reported_balance and not statement.balance_end_real:
            amount = sum(statement.line_ids.mapped("amount"))
            statement.balance_end_real = statement.balance_start + amount
        return statement

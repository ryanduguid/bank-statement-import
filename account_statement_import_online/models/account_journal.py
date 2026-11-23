# Copyright 2019-2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2019-2020 Dataplug (https://dataplug.io)
# Copyright 2023 Therp BV (https://therp.nl)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.model
    def _selection_service(self):
        OnlineBankStatementProvider = self.env["online.bank.statement.provider"]
        return OnlineBankStatementProvider._selection_service()

    # Keep provider fields for compatibility with other modules.
    online_bank_statement_provider = fields.Selection(
        selection=lambda self: self._selection_service(),
    )
    online_bank_statement_provider_id = fields.Many2one(
        string="Statement Provider",
        comodel_name="online.bank.statement.provider",
        copy=False,
    )

    def __get_bank_statements_available_sources(self):
        result = super().__get_bank_statements_available_sources()
        result.append(("online", _("Online (OCA)")))
        return result

    def _update_providers(self):
        """Automatically create service.

        This method exists for compatibility reasons. The preferred method
        to create an online provider is directly through the menu,
        """
        OnlineBankStatementProvider = self.env["online.bank.statement.provider"]
        for journal in self.filtered("online_bank_statement_provider"):
            service = journal.online_bank_statement_provider
            if service == journal._get_linked_online_provider().service:
                # Provider already exists.
                continue
            # Use existing or create new provider for service.
            provider = OnlineBankStatementProvider.with_context(
                active_test=False
            ).search(
                [
                    ("journal_id", "=", journal.id),
                    ("service", "=", service),
                ],
                limit=1,
            ) or OnlineBankStatementProvider.create(
                {
                    "journal_id": journal.id,
                    "service": service,
                }
            )
            journal.online_bank_statement_provider_id = provider
            _logger.info("Journal %s now linked to service %s", journal.name, service)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._update_vals(vals)
        journals = super().create(vals_list)
        journals._update_providers()
        return journals

    def write(self, vals):
        self._update_vals(vals)
        res = super().write(vals)
        if vals.get("online_bank_statement_provider"):
            self._update_providers()
        return res

    def _update_vals(self, vals):
        """Ensure consistent values."""
        if (
            "bank_statements_source" in vals
            and vals.get("bank_statements_source") != "online"
        ):
            vals["online_bank_statement_provider"] = False
            vals["online_bank_statement_provider_id"] = False

    def _get_linked_online_provider(self):
        self.ensure_one()
        return self.online_bank_statement_provider_id.filtered(
            lambda provider: provider.journal_id == self
        )

    def _clear_online_provider_link(self):
        online_journals = self.filtered(lambda j: j.bank_statements_source == "online")
        if online_journals:
            online_journals.write({"bank_statements_source": "undefined"})
        other_journals = self - online_journals
        if other_journals:
            other_journals.write(
                {
                    "online_bank_statement_provider": False,
                    "online_bank_statement_provider_id": False,
                }
            )

    def _get_online_provider_for_pull(self):
        provider = self._get_linked_online_provider()
        if not provider:
            raise UserError(
                _("Configure an online statement provider for this journal.")
            )
        return provider

    def action_online_bank_statements_pull_wizard(self):
        """Keep the journal entry point for compatibility."""
        provider = self._get_online_provider_for_pull()
        return provider.action_online_bank_statements_pull_wizard()

    def action_open_online_bank_statement_provider(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Statement Provider",
            "view_mode": "form",
            "res_model": "online.bank.statement.provider",
            "res_id": self._get_linked_online_provider().id,
            "target": "current",
        }

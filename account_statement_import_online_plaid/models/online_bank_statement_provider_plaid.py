# Copyright 2024 Binhex - Adasat Torres de León.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

AVAILABLE_LANGS = [
    "da",
    "nl",
    "en",
    "et",
    "fr",
    "de",
    "hi",
    "it",
    "lv",
    "lt",
    "no",
    "pl",
    "pt",
    "ro",
    "es",
    "sv",
    "vi",
]


class OnlineBankStatementProvider(models.Model):
    _inherit = "online.bank.statement.provider"
    plaid_access_token = fields.Char()
    plaid_account_id = fields.Char(
        readonly=True,
        copy=False,
        help="The single Plaid account selected for this journal. Relink to change it.",
    )
    plaid_host = fields.Selection(
        [
            ("sandbox", "Sandbox"),
            ("production", "Production"),
        ],
        default="sandbox",
    )

    def _obtain_statement_data(self, date_since, date_until):
        self.ensure_one()
        if self.service != "plaid":
            return super()._obtain_statement_data(date_since, date_until)
        return self._plaid_retrieve_data(date_since, date_until), {}

    @api.model
    def _get_available_services(self):
        return super()._get_available_services() + [
            ("plaid", "Plaid.com"),
        ]

    def _country_code(self):
        if self.journal_id.bank_id and self.journal_id.bank_id.country:
            return self.journal_id.bank_id.country.code
        if self.journal_id.company_id.country_id:
            return self.journal_id.company_id.country_id.code
        raise UserError(_("Country code not found for the bank or the company..."))

    def _verify_lang(self, lang):
        if lang not in AVAILABLE_LANGS:
            return "en"
        return lang

    def action_sync_with_plaid(self):
        self.ensure_one()
        plaid_interface = self.env["plaid.interface"]
        args = [self.username, self.password, self.plaid_host]
        client = plaid_interface._client(*args)
        lang = (
            self.env["res.lang"]._lang_get(self.env.lang or self.env.user.lang).iso_code
        )
        company_name = self.env.company.name

        link_token = plaid_interface._link(
            client=client,
            language=self._verify_lang(lang),
            country_code=self._country_code(),
            company_name=company_name,
            products=["transactions"],
        )
        return {
            "type": "ir.actions.client",
            "tag": "plaid_login",
            "params": {
                "call_model": "online.bank.statement.provider",
                "call_method": "plaid_create_access_token",
                "token": link_token,
                "object_id": self.id,
            },
            "target": "new",
        }

    def _plaid_retrieve_data(self, date_since, date_until):
        if not self.plaid_access_token or not self.plaid_account_id:
            raise UserError(
                _(
                    "Please link exactly one Plaid account for this journal by "
                    "clicking on 'Sync with Plaid'."
                )
            )
        plaid_interface = self.env["plaid.interface"]
        args = [self.username, self.password, self.plaid_host]
        client = plaid_interface._client(*args)
        transactions = plaid_interface._get_transactions(
            client,
            self.plaid_access_token,
            date_since,
            date_until,
            self.plaid_account_id,
        )
        return self._prepare_vals_for_statement(transactions)

    @api.model
    def plaid_create_access_token(self, public_token, active_id, accounts=None):
        provider = self.browse(active_id)
        provider.ensure_one()
        if not accounts or len(accounts) != 1 or not accounts[0].get("id"):
            raise UserError(_("Select exactly one Plaid account for this journal."))
        plaid_interface = self.env["plaid.interface"]
        client = plaid_interface._client(
            provider.username, provider.password, provider.plaid_host
        )
        args = [client, public_token]
        access_token = plaid_interface._login(*args)
        if not access_token:
            return False
        provider.write(
            {
                "plaid_access_token": access_token,
                "plaid_account_id": accounts[0]["id"],
            }
        )
        return True

    def _prepare_vals_for_statement(self, transactions):
        self.ensure_one()
        currency = self.journal_id.currency_id or self.journal_id.company_id.currency_id
        if not self.plaid_account_id:
            raise UserError(_("Relink Plaid and select one account for this journal."))
        transactions = [
            transaction
            for transaction in transactions
            if not transaction.get("pending", False)
        ]
        for transaction in transactions:
            if transaction.get("account_id") != self.plaid_account_id:
                raise UserError(_("Plaid returned a transaction for another account."))
            if transaction.get("iso_currency_code") != currency.name:
                raise UserError(
                    _("Plaid transaction currency differs from the journal currency.")
                )
        return [
            {
                "date": transaction["date"],
                "ref": transaction["name"],
                "payment_ref": transaction["name"],
                "unique_import_id": transaction["transaction_id"],
                "amount": float(transaction["amount"]) * -1.00,
                "raw_data": transaction,
            }
            for transaction in transactions
        ]

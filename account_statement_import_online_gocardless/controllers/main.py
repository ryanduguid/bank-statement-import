# Copyright 2022 ForgeFlow S.L.
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import werkzeug
from werkzeug.urls import url_encode

from odoo import http
from odoo.http import request


class GocardlessController(http.Controller):
    @http.route("/gocardless/response", type="http", auth="public", csrf=False)
    def gocardless_response(self, **post):
        Provider = request.env["online.bank.statement.provider"].sudo()
        current_providers = Provider.search(
            [("gocardless_requisition_ref", "=", post["ref"])]
        )
        params = {
            "action": request.env.ref(
                "account_statement_import_online.online_bank_statement_provider_action"
            ).id,
            "model": "online.bank.statement.provider",
        }
        for provider in current_providers:
            provider._gocardless_finish_requisition()
        if len(current_providers) == 1:
            params.update(
                {
                    "view_type": "form",
                    "id": current_providers.id,
                }
            )
        else:
            params["view_type"] = "list"
        return werkzeug.utils.redirect("/web#" + url_encode(params), 303)

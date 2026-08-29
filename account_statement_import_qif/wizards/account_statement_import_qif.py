# Copyright 2015 Odoo S. A.
# Copyright 2015 Laurent Mignon <laurent.mignon@acsone.eu>
# Copyright 2015 Ronald Portier <rportier@therp.nl>
# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# Copyright 2026 Ryan Duguid
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import re

import dateutil.parser

from odoo import api, models
from odoo.exceptions import UserError

# Numeric QIF dates in these countries use day/month/year.
_QIF_DMY_COUNTRY_CODES = frozenset({"AU", "NZ", "GB", "IE", "ZA", "IN"})


class AccountStatementImport(models.TransientModel):
    _inherit = "account.statement.import"

    @api.model
    def _check_qif(self, data_file):
        return data_file.strip().startswith(b"!Type:")

    def _qif_detect_dayfirst_from_dates(self, date_strings):
        """Return True/False when dates in the file have an unambiguous order.

        QIF does not declare locale. ``08/07/2026`` is 8 July in Australia and
        7 August in the US. A day or month number above 12 tells us which.
        Year-first ISO values (first part > 31) are skipped; dateutil already
        parses those independently of ``dayfirst``.
        """
        saw_dmy = False
        saw_mdy = False
        for raw in date_strings:
            parts = [int(part) for part in re.findall(r"\d+", raw)]
            if len(parts) < 2:
                continue
            first, second = parts[0], parts[1]
            if first > 31:
                continue
            if first > 12:
                saw_dmy = True
            if 12 < second <= 31:
                saw_mdy = True
        if saw_dmy and not saw_mdy:
            return True
        if saw_mdy and not saw_dmy:
            return False
        return None

    def _qif_lang_dayfirst(self):
        lang_code = self.env.user.lang or self.env.company.partner_id.lang
        if not lang_code:
            return False
        lang = self.env["res.lang"].search([("code", "=", lang_code)], limit=1)
        date_format = lang.date_format or ""
        day_pos = date_format.find("%d")
        month_pos = date_format.find("%m")
        return day_pos != -1 and month_pos != -1 and day_pos < month_pos

    def _qif_dayfirst(self, date_strings):
        detected = self._qif_detect_dayfirst_from_dates(date_strings)
        if detected is not None:
            return detected
        if self._qif_lang_dayfirst():
            return True
        return self.env.company.country_id.code in _QIF_DMY_COUNTRY_CODES

    def _parse_file(self, data_file):
        if not self._check_qif(data_file):
            return super()._parse_file(data_file)
        try:
            file_data = data_file.decode()
            if "\r" in file_data:
                data_list = file_data.split("\r")
            else:
                data_list = file_data.split("\n")
            header = data_list[0].strip()
            header = header.split(":")[1]
        except Exception as e:
            raise UserError(self.env._("Could not decipher the QIF file.")) from e
        transactions = []
        vals_line = {}
        total = 0
        if header in ("Bank", "CCard"):
            vals_bank_statement = {}
            date_strings = [
                line.strip()[1:] for line in data_list if line.strip()[:1] == "D"
            ]
            dayfirst = self._qif_dayfirst(date_strings)
            for line in data_list:
                line = line.strip()
                if not line:
                    continue
                if line[0] == "D":  # date of transaction
                    vals_line["date"] = dateutil.parser.parse(
                        line[1:], fuzzy=True, dayfirst=dayfirst
                    ).date()
                elif line[0] == "T":  # Total amount
                    total += float(line[1:].replace(",", ""))
                    vals_line["amount"] = float(line[1:].replace(",", ""))
                elif line[0] == "N":  # Check number
                    vals_line["ref"] = line[1:]
                elif line[0] == "P":  # Payee
                    vals_line["payment_ref"] = (
                        "name" in vals_line
                        and line[1:] + ": " + vals_line["name"]
                        or line[1:]
                    )
                elif line[0] == "M":  # Memo
                    vals_line["payment_ref"] = (
                        "name" in vals_line
                        and vals_line["name"] + ": " + line[1:]
                        or line[1:]
                    )
                elif line[0] == "^" and vals_line:  # end of item
                    transactions.append(vals_line)
                    vals_line = {}
                elif line[0] == "\n":
                    transactions = []
                else:
                    pass
        else:
            raise UserError(
                self.env._(
                    "This file is either not a bank statement or is "
                    "not correctly formed."
                )
            )
        vals_bank_statement.update(
            {"balance_end_real": total, "transactions": transactions}
        )
        journal = self.env["account.journal"].browse(self.env.context.get("journal_id"))
        return journal.currency_id.name, None, [vals_bank_statement]

    def _complete_stmts_vals(self, stmt_vals, journal_id, account_number):
        """Match partner_id if hasn't been deducted yet."""
        res = super()._complete_stmts_vals(stmt_vals, journal_id, account_number)
        # Since QIF doesn't provide account numbers (normal behaviour is to
        # provide 'account_number', which the generic module uses to find
        # the partner), we have to find res.partner through the name
        if not self.statement_file or not self._check_qif(
            base64.b64decode(self.statement_file)
        ):
            return res
        partner_obj = self.env["res.partner"]
        for statement in res:
            for line_vals in statement["transactions"]:
                if not line_vals.get("partner_id") and line_vals.get("payment_ref"):
                    partner = partner_obj.search(
                        [("name", "ilike", line_vals["payment_ref"])],
                        limit=1,
                    )
                    line_vals["partner_id"] = partner.id
        return res

# Copyright 2013-2016 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
import zipfile
from io import BytesIO

from odoo import models

_logger = logging.getLogger(__name__)


class AccountStatementImport(models.TransientModel):
    _inherit = "account.statement.import"

    def _parse_file(self, data_file):
        """Parse a CAMT053 XML file."""
        try:
            parser = self.env["account.statement.import.camt.parser"]
            _logger.debug("Try parsing with camt.")
            return parser.parse(data_file)
        except ValueError:
            try:
                with zipfile.ZipFile(BytesIO(data_file)) as data:
                    grouped = {}
                    for member in data.namelist():
                        parsed = self._parse_file(data.open(member).read())
                        triplets = parsed if isinstance(parsed, list) else [parsed]
                        for currency, account_number, statements in triplets:
                            # Keep each member's own account and currency; only
                            # members that share both are filed together.
                            grouped.setdefault((currency, account_number), []).extend(
                                statements
                            )
                return parser.group_statements(grouped)
            # pylint: disable=except-pass
            except (zipfile.BadZipFile, ValueError):
                _logger.exception("BadZipfile exception")
            # Not a camt file, returning super will call next candidate:
            _logger.debug("Statement file was not a camt file.", exc_info=True)
        return super()._parse_file(data_file)

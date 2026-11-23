import io
import logging
from importlib import import_module

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountStatementImport(models.TransientModel):
    _inherit = "account.statement.import"

    @api.model
    def _check_ofx(self, data_file):
        try:
            ofxparse = import_module("ofxparse")
        except ImportError:
            _logger.debug("ofxparse not found.")
            return False
        try:
            ofx = ofxparse.OfxParser.parse(io.BytesIO(data_file))
        except Exception as e:
            _logger.debug(e)
            return False
        return ofx

    @api.model
    def _prepare_ofx_transaction_line(self, transaction):
        # Since ofxparse doesn't provide account numbers,
        # we cannot provide the key 'account_number'
        # If you read the code of the module account_statement_import_base
        # it's the only key we can provide to match a partner.
        reference = " ".join(filter(None, (transaction.payee, transaction.checknum)))
        payment_ref = " : ".join(filter(None, (reference, transaction.memo)))
        vals = {
            "date": transaction.date,
            "payment_ref": payment_ref,
            "amount": float(transaction.amount),
            "unique_import_id": transaction.id,
        }
        return vals

    def _parse_file(self, data_file):
        ofx = self._check_ofx(data_file)
        if not ofx:
            return super()._parse_file(data_file)

        result = []
        try:
            for account in ofx.accounts:
                transactions = []
                total_amt = 0.00

                if not account.statement.transactions:
                    continue

                for transaction in account.statement.transactions:
                    vals = self._prepare_ofx_transaction_line(transaction)
                    if vals:
                        transactions.append(vals)
                        total_amt += vals["amount"]
                balance = float(account.statement.balance)
                vals_bank_statement = {
                    "name": account.number,
                    "transactions": transactions,
                    "balance_start": balance - total_amt,
                    "balance_end_real": balance,
                }
                result.append(
                    (account.statement.currency, account.number, [vals_bank_statement])
                )
        except Exception as e:
            raise UserError(
                _(
                    "The following problem occurred during import. "
                    "The file might not be valid.\n\n %s"
                )
                % str(e)
            ) from e
        return result

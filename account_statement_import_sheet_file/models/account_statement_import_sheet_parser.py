# Copyright 2019 ForgeFlow, S.L.
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2025 Simone Rubino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import itertools
import logging
import math
import re
from csv import reader
from datetime import datetime
from decimal import Decimal
from importlib import import_module
from io import BytesIO, StringIO
from os import path
from zipfile import BadZipFile

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl.worksheet.worksheet import Worksheet

from odoo import api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountStatementImportSheetParser(models.TransientModel):
    _name = "account.statement.import.sheet.parser"
    _description = "Bank Statement Import Sheet Parser"

    @api.model
    def parse_header(self, csv_or_xlsx, mapping):
        if mapping.no_header:
            return []
        header_line = mapping.header_lines_skip_count
        # prevent negative indexes
        if header_line > 0:
            header_line -= 1
        if isinstance(csv_or_xlsx, Worksheet):
            header = [
                str(cell.value).strip() if cell.value is not None else ""
                for cell in csv_or_xlsx[header_line + 1]
            ]
        elif isinstance(csv_or_xlsx, tuple):
            header = [
                str(value).strip() for value in csv_or_xlsx[1].row_values(header_line)
            ]
        else:
            [next(csv_or_xlsx) for _i in range(header_line)]
            header = [value.strip() for value in next(csv_or_xlsx)]
        if mapping.offset_column:
            header = header[mapping.offset_column :]
        return header

    @api.model
    def parse(self, data_file, mapping, filename):
        journal = self.env["account.journal"].browse(self.env.context.get("journal_id"))
        currency_code = (journal.currency_id or journal.company_id.currency_id).name
        account_number = journal.bank_account_id.acc_number

        lines = self._parse_lines(mapping, data_file, currency_code)
        if not lines:
            return currency_code, account_number, [{"transactions": []}]

        lines = sorted(lines, key=lambda line: line["timestamp"])
        first_line = lines[0]
        last_line = lines[-1]
        data = {
            "date": first_line["timestamp"].date(),
            "name": self.env._(
                "%(code)s: %(filename)s",
                code=journal.code,
                filename=path.basename(filename),
            ),
        }

        if mapping.balance_column:
            if (balance := first_line.get("balance")) is not None:
                data["balance_start"] = balance - first_line["amount"]
            if (balance := last_line.get("balance")) is not None:
                data["balance_end_real"] = balance
        transactions = list(
            itertools.chain.from_iterable(
                map(lambda line: self._convert_line_to_transactions(line), lines)
            )
        )
        data.update({"transactions": transactions})

        return currency_code, account_number, [data]

    def _get_column_indexes(self, header, column_name, mapping):
        configured_columns = mapping[column_name]
        if not configured_columns:
            return []
        column_indexes = []
        for column_name_or_index in configured_columns.split(","):
            column_name_or_index = column_name_or_index.strip()
            if not column_name_or_index:
                continue
            if mapping.no_header:
                try:
                    column_indexes.append(int(column_name_or_index))
                except ValueError:
                    continue
            else:
                column_indexes.append(header.index(column_name_or_index))
        return column_indexes

    def _get_column_names(self):
        return [
            "timestamp_column",
            "currency_column",
            "amount_column",
            "amount_debit_column",
            "amount_credit_column",
            "balance_column",
            "original_currency_column",
            "original_amount_column",
            "debit_credit_column",
            "transaction_id_column",
            "description_column",
            "notes_column",
            "reference_column",
            "partner_name_column",
            "bank_name_column",
            "bank_account_column",
        ]

    def _get_csv_options(self, mapping):
        csv_options = {}
        csv_delimiter = mapping._get_column_delimiter_character()
        if csv_delimiter:
            csv_options["delimiter"] = csv_delimiter
        if mapping.quotechar:
            csv_options["quotechar"] = mapping.quotechar
        return csv_options

    def _get_data_parsers(self):
        """List of callables that can parse a file.

        They accept `mapping` and `data_file` arguments and return the parsed file.
        """
        return [
            self._parse_data_openpyxl,
            self._parse_data_xlrd,
            self._parse_data_csv,
        ]

    def _parse_data_openpyxl(self, mapping, data_file):
        try:
            with BytesIO(data_file) as stream:
                workbook = load_workbook(stream, data_only=True)
                sheet = workbook.worksheets[0]
                workbook.close()
                return sheet
        except (BadZipFile, InvalidFileException):
            _logger.debug("Failed decoding with openpyxl", exc_info=True)
            return None

    def _parse_data_xlrd(self, mapping, data_file):
        try:
            xlrd = import_module("xlrd")
        except (ImportError, OSError):
            return None
        try:
            workbook = xlrd.open_workbook(
                file_contents=data_file,
                encoding_override=(
                    mapping.file_encoding if mapping.file_encoding else None
                ),
            )
            csv_or_xlsx = (
                workbook,
                workbook.sheet_by_index(0),
            )
        except xlrd.XLRDError:
            _logger.debug("Failed decoding with xlrd", exc_info=True)
            csv_or_xlsx = None
        return csv_or_xlsx

    def _decode_data_file(self, data_file, encoding="utf-8"):
        """Decode `data_file` with `encoding`."""
        try:
            return data_file.decode(encoding or "utf-8")
        except UnicodeDecodeError as error:
            # Try auto guessing the format
            try:
                chardet = import_module("chardet")
            except (ImportError, OSError):
                raise error from None
            detected_encoding = chardet.detect(data_file).get("encoding", False)
            if not detected_encoding:
                _logger.debug("Failed decoding detection")
                raise
            return data_file.decode(detected_encoding)

    def _parse_data_csv(self, mapping, data_file):
        decoded_file = self._decode_data_file(data_file, encoding=mapping.file_encoding)
        return self._parse_csv_text(mapping, decoded_file)

    def _parse_csv_text(self, mapping, decoded_file):
        content_end = len(decoded_file.rstrip())
        if not content_end:
            return None
        trailing_break = re.search(r"[\r\n]", decoded_file[content_end:])
        if trailing_break:
            decoded_file = decoded_file[: content_end + trailing_break.start()]
        return reader(
            StringIO(decoded_file, newline=""), **self._get_csv_options(mapping)
        )

    def _parse_data(self, mapping, data_file):
        """Try the available parsers for `data_file`.

        The available parsers are returned by `_get_data_parsers`.
        """

        for parser in self._get_data_parsers():
            if parsed_data := parser(mapping, data_file):
                break
        else:
            raise UserError(self.env._("Failed to parse file"))
        return parsed_data

    def _parse_lines(self, mapping, data_file, currency_code):
        parsed_data = self._parse_data(mapping, data_file)
        columns = dict()
        header = self.parse_header(parsed_data, mapping)

        # NOTE no seria necesario debit_column y credit_column ya que tenemos los
        # respectivos campos related
        for column_name in self._get_column_names():
            columns[column_name] = self._get_column_indexes(
                header, column_name, mapping
            )
        data = parsed_data, data_file
        return self._parse_rows(mapping, currency_code, data, columns)

    def _get_values_from_column(self, values, columns, column_name):
        indexes = columns[column_name]
        content_l = []
        column_count = len(values)
        for index in indexes:
            if isinstance(index, int):
                if -column_count <= index < column_count:
                    content_l.append(values[index])
            else:
                if index in values:
                    content_l.append(values[index])
        if not content_l:
            return None
        if all(isinstance(content, str) for content in content_l):
            return " ".join(content_l)
        return content_l[0]

    def _parse_rows(self, mapping, currency_code, data, columns):  # noqa: C901
        csv_or_xlsx, _data_file = data
        label_line = mapping.header_lines_skip_count
        footer_count = mapping.footer_lines_skip_count
        if isinstance(csv_or_xlsx, Worksheet):
            rows = range(label_line, csv_or_xlsx.max_row - footer_count)
        elif isinstance(csv_or_xlsx, tuple):
            xlrd = import_module("xlrd")
            book, sheet = csv_or_xlsx[:2]
            rows = range(label_line, sheet.nrows - footer_count)
        elif footer_count > 0:
            # Look ahead by the footer size in CSV records, buffering only that tail.
            records, lookahead = itertools.tee(csv_or_xlsx)
            tail = itertools.islice(lookahead, footer_count, None)
            rows = (row for row, _ in zip(records, tail, strict=False))
        else:
            rows = csv_or_xlsx

        lines = []
        for row in rows:
            if isinstance(csv_or_xlsx, Worksheet):
                values = [
                    cell.value if cell.value is not None else ""
                    for cell in csv_or_xlsx[row + 1][mapping.offset_column :]
                ]
            elif isinstance(csv_or_xlsx, tuple):
                values = []
                for col_index in range(mapping.offset_column, sheet.row_len(row)):
                    cell_type = sheet.cell_type(row, col_index)
                    cell_value = sheet.cell_value(row, col_index)
                    if cell_type == xlrd.XL_CELL_DATE:
                        cell_value = xlrd.xldate_as_datetime(cell_value, book.datemode)
                    values.append(cell_value)
            else:
                values = list(row)
            if mapping.skip_empty_lines and not any(values):
                continue

            timestamp = self._get_values_from_column(
                values, columns, "timestamp_column"
            )
            currency = (
                self._get_values_from_column(values, columns, "currency_column")
                if mapping.currency_column
                else currency_code
            )

            def _decimal(value):
                if value is not None:
                    return self._parse_decimal(value, mapping)

            amount_column, debit_column, credit_column = (
                self._get_values_from_column(values, columns, column)
                if columns[column]
                else None
                for column in (
                    "amount_column",
                    "amount_debit_column",
                    "amount_credit_column",
                )
            )
            amount = _decimal(amount_column)
            if not amount:
                amount = abs(_decimal(debit_column) or 0)
            if not amount:
                amount = -abs(_decimal(credit_column) or 0)

            balance = (
                self._get_values_from_column(values, columns, "balance_column")
                if columns["balance_column"]
                else None
            )
            original_currency = (
                self._get_values_from_column(
                    values, columns, "original_currency_column"
                )
                if columns["original_currency_column"]
                else None
            )
            original_amount = (
                self._get_values_from_column(values, columns, "original_amount_column")
                if columns["original_amount_column"]
                else None
            )
            debit_credit = (
                self._get_values_from_column(values, columns, "debit_credit_column")
                if columns["debit_credit_column"]
                else None
            )
            transaction_id = (
                self._get_values_from_column(values, columns, "transaction_id_column")
                if columns["transaction_id_column"]
                else None
            )
            description = (
                self._get_values_from_column(values, columns, "description_column")
                if columns["description_column"]
                else None
            )
            notes = (
                self._get_values_from_column(values, columns, "notes_column")
                if columns["notes_column"]
                else None
            )
            reference = (
                self._get_values_from_column(values, columns, "reference_column")
                if columns["reference_column"]
                else None
            )
            partner_name = (
                self._get_values_from_column(values, columns, "partner_name_column")
                if columns["partner_name_column"]
                else None
            )
            bank_name = (
                self._get_values_from_column(values, columns, "bank_name_column")
                if columns["bank_name_column"]
                else None
            )
            bank_account = (
                self._get_values_from_column(values, columns, "bank_account_column")
                if columns["bank_account_column"]
                else None
            )

            if mapping.currency_column and not str(currency or "").strip():
                raise UserError(
                    self.env._(
                        "The mapped currency column is missing from a statement row."
                    )
                )
            if currency != currency_code:
                continue

            if (
                timestamp is None
                or isinstance(timestamp, str)
                and not timestamp.strip()
            ):
                raise UserError(
                    self.env._(
                        "The mapped date column is missing from a statement row."
                    )
                )
            if isinstance(timestamp, str):
                timestamp = datetime.strptime(timestamp, mapping.timestamp_format)
                if timestamp.year == 1900:
                    # No year indicated, so put the current or previous one depending
                    # on the current month (i.e. in January, importing December)
                    now = datetime.now()
                    year = now.year
                    if timestamp.month > now.month:
                        year -= 1
                    timestamp = timestamp.replace(year=year)

            balance = (
                self._parse_decimal(balance, mapping)
                if balance is not None and str(balance).strip()
                else None
            )
            has_debit_credit = debit_credit is not None and bool(
                str(debit_credit).strip()
            )

            if has_debit_credit:
                amount = abs(amount)
                if debit_credit == mapping.debit_value:
                    amount = -amount

            if debit_column and credit_column:
                debit_amount = self._parse_decimal(debit_column, mapping)
                debit_amount = abs(debit_amount)
                credit_amount = self._parse_decimal(credit_column, mapping)
                credit_amount = abs(credit_amount)
                amount = -(credit_amount - debit_amount)

            if original_amount:
                original_amount = self._parse_decimal(original_amount, mapping)
                if (
                    original_amount
                    and not amount
                    and original_currency == currency
                    and not any(
                        re.search(r"\d", str(value))
                        for value in (amount_column, debit_column, credit_column)
                    )
                ):
                    amount = original_amount
                    if has_debit_credit:
                        amount = (
                            -abs(amount)
                            if debit_credit == mapping.debit_value
                            else abs(amount)
                        )
                original_amount = math.copysign(original_amount, amount)
            else:
                original_amount = 0.0
            if (
                amount == 0
                and amount_column is None
                and debit_column is None
                and credit_column is None
                and (
                    mapping.amount_column
                    or mapping.amount_debit_column
                    or mapping.amount_credit_column
                )
            ):
                raise UserError(
                    self.env._(
                        "The mapped amount column is missing from a statement row."
                    )
                )
            if (
                amount
                and mapping.amount_type == "absolute_value"
                and not has_debit_credit
            ):
                raise UserError(
                    self.env._(
                        "Missing mapped debit or credit indicator in statement row."
                    )
                )
            if mapping.amount_inverse_sign:
                amount = -amount
                original_amount = -original_amount
                balance = -balance if balance is not None else balance
            line = {
                "timestamp": timestamp,
                "amount": amount,
                "currency": currency,
                "original_amount": original_amount,
                "original_currency": original_currency,
            }
            if balance is not None:
                line["balance"] = balance
            if transaction_id is not None:
                line["transaction_id"] = transaction_id
            if description is not None:
                line["description"] = description
            if notes is not None:
                line["notes"] = notes
            if reference is not None:
                line["reference"] = reference
            if partner_name is not None:
                line["partner_name"] = partner_name
            if bank_name is not None:
                line["bank_name"] = bank_name
            if bank_account is not None:
                line["bank_account"] = bank_account

            lines.append(line)
        return lines

    @api.model
    def _convert_line_to_transactions(self, line):  # noqa: C901
        """Hook for extension"""
        timestamp = line["timestamp"]
        amount = line["amount"]
        currency = line["currency"]
        original_amount = line["original_amount"]
        original_currency = line["original_currency"]
        transaction_id = line.get("transaction_id")
        description = line.get("description")
        notes = line.get("notes")
        reference = line.get("reference")
        partner_name = line.get("partner_name")
        bank_name = line.get("bank_name")
        bank_account = line.get("bank_account")

        if original_currency == currency:
            original_currency = None

        transaction = {
            "date": timestamp,
            "amount": str(amount),
        }

        if original_currency:
            original_currency = self.env["res.currency"].search(
                [("name", "=", original_currency)],
                limit=1,
            )
            if original_currency:
                transaction["foreign_currency_id"] = original_currency.id
            if original_amount:
                transaction["amount_currency"] = str(original_amount)

        if currency:
            currency = self.env["res.currency"].search(
                [("name", "=", currency)],
                limit=1,
            )
            if currency:
                transaction["currency_id"] = currency.id

        if transaction_id:
            transaction["unique_import_id"] = (
                f"{transaction_id}-{int(timestamp.timestamp())}"
            )

        transaction["payment_ref"] = description or self.env._("N/A")
        if reference:
            transaction["ref"] = reference

        note = ""
        if bank_name:
            note += self.env._("Bank: %s; ") % (bank_name,)
        if bank_account:
            note += self.env._("Account: %s; ") % (bank_account,)
        if transaction_id:
            note += self.env._("Transaction ID: %s; ") % (transaction_id,)
        if note and notes:
            note = f"{notes}\n{note.strip()}"
        elif note:
            note = note.strip()
        elif notes:
            note = notes
        if note:
            transaction["narration"] = note

        if partner_name:
            transaction["partner_name"] = partner_name
        if bank_account:
            transaction["account_number"] = bank_account

        return [transaction]

    @api.model
    def _parse_decimal(self, value, mapping):
        if isinstance(value, Decimal) or isinstance(value, int | float):
            return float(value)
        thousands, decimal = mapping._get_float_separators()
        # No digits and at most one sign, such as "-" or "$ -", is an empty
        # amount in some bank exports. Test before dropping the separators the
        # mapping does not use, so "-," stays malformed for float() to reject.
        if re.sub(r"[^\d\-+.,']+", "", value) in ("", "-", "+"):
            return 0.0
        # Remove all characters except digits, thousands separator,
        # decimal separator, and signs
        value = re.sub(
            r"[^\d\-+" + re.escape(thousands) + re.escape(decimal) + "]+", "", value
        )
        value = value.replace(thousands, "")
        if decimal:
            return float(value.replace(decimal, "."))

        journal = self.env["account.journal"].browse(self.env.context.get("journal_id"))
        currency = journal.currency_id or journal.company_id.currency_id
        decimal_places = currency.decimal_places if currency else 2
        return float(f"{value}e-{decimal_places}")

# Copyright 2019 ForgeFlow, S.L.
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# Copyright 2025 Tecnativa - Pedro M. Baeza
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

from openpyxl import Workbook

from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form
from odoo.tools import float_round, mute_logger

from .common import Common


class TestAccountStatementImportSheetFile(Common):
    def test_xlsx_dates_numbers_empty_cells_and_offsets(self):
        self.sample_statement_map.write(
            {
                "header_lines_skip_count": 2,
                "offset_column": 1,
                "footer_lines_skip_count": 1,
                "skip_empty_lines": True,
                "original_currency_column": False,
                "original_amount_column": False,
                "partner_name_column": False,
                "bank_account_column": False,
            }
        )
        workbook = Workbook()
        for row in [
            ["Title"],
            ["Unused", "Date", "Amount", "Label"],
            ["x", datetime(2026, 9, 1), 100, None],
            [None, None, None, None],
            ["x", datetime(2026, 9, 2), -12.5, "Fee"],
            ["Footer"],
        ]:
            workbook.active.append(row)
        with BytesIO() as stream:
            workbook.save(stream)
            lines = self.parser._parse_lines(
                self.sample_statement_map, stream.getvalue(), "USD"
            )
        workbook.close()
        self.assertEqual([line["amount"] for line in lines], [100, -12.5])
        self.assertEqual(
            [line["timestamp"] for line in lines],
            [datetime(2026, 9, 1), datetime(2026, 9, 2)],
        )
        self.assertEqual([line["description"] for line in lines], ["", "Fee"])

    def test_import_csv_file(self):
        wizard = self._get_import_wizard("fixtures/sample_statement_en.csv")
        wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 2)

    def test_csv_preserves_transaction_audit_details(self):
        self.sample_statement_map.write(
            {
                "balance_column": "Balance",
                "transaction_id_column": "Transaction ID",
                "bank_name_column": "Bank",
                "bank_account_column": "Account",
                "reference_column": "Reference",
                "notes_column": "Notes",
                "original_currency_column": False,
                "original_amount_column": False,
                "partner_name_column": False,
            }
        )
        csv_data = (
            b"Date,Label,Amount,Balance,Transaction ID,Bank,Account,Reference,Notes\n"
            b"09/02/2026,Fee,-25.00,1100.00,,,,,Service charge\n"
            b"09/01/2026,Deposit,125.00,1125.00,TX-001,Fixture Bank,"
            b"FIXTURE-001,DEP-001,Counter deposit\n"
        )
        currency, _account, statements = self.parser.with_context(
            journal_id=self.journal.id
        ).parse(csv_data, self.sample_statement_map, "audit.csv")
        self.assertEqual(currency, "USD")
        self.assertEqual(len(statements), 1)
        statement = statements[0]
        self.assertEqual(statement["date"], datetime(2026, 9, 1).date())
        # Opening 1000 + deposit 125 - fee 25 = closing 1100.
        self.assertEqual(statement["balance_start"], 1000)
        self.assertEqual(statement["balance_end_real"], 1100)
        transactions = statement["transactions"]
        self.assertEqual(len(transactions), 2)
        deposit, fee = transactions
        self.assertEqual(
            [line["payment_ref"] for line in transactions], ["Deposit", "Fee"]
        )
        self.assertEqual(
            [line["date"] for line in transactions],
            [datetime(2026, 9, 1), datetime(2026, 9, 2)],
        )
        self.assertEqual([line["amount"] for line in transactions], ["125.0", "-25.0"])
        self.assertEqual(deposit["ref"], "DEP-001")
        self.assertEqual(deposit["account_number"], "FIXTURE-001")
        self.assertEqual(
            deposit["unique_import_id"],
            f"TX-001-{int(datetime(2026, 9, 1).timestamp())}",
        )
        self.assertEqual(
            deposit["narration"],
            "Counter deposit\nBank: Fixture Bank; Account: FIXTURE-001; "
            "Transaction ID: TX-001;",
        )
        self.assertEqual(fee["narration"], "Service charge")
        for name in ("unique_import_id", "ref", "account_number"):
            self.assertNotIn(name, fee)
        for line in transactions:
            self.assertEqual(line["currency_id"], self.currency_usd.id)
            self.assertNotIn("foreign_currency_id", line)
            self.assertNotIn("amount_currency", line)

    def test_yearless_csv_dates_use_the_current_or_previous_year(self):
        self.sample_statement_map.write(
            {
                "timestamp_format": "%m/%d",
                "balance_column": "Balance",
                "original_currency_column": False,
                "original_amount_column": False,
                "partner_name_column": False,
                "bank_account_column": False,
            }
        )
        cases = [
            (
                b"01/15,Deposit,125.00,1125.00\n",
                "Deposit",
                "125.0",
                1125,
                datetime(2026, 1, 15),
            ),
            (b"12/15,Fee,-25.00,975.00\n", "Fee", "-25.0", 975, datetime(2025, 12, 15)),
        ]
        with patch(
            "odoo.addons.account_statement_import_sheet_file.models."
            "account_statement_import_sheet_parser.datetime",
            wraps=datetime,
        ) as clock:
            clock.now.return_value = datetime(2026, 6, 30, 12)
            for row, label, amount, closing, expected_date in cases:
                with self.subTest(label=label):
                    currency, _account, statements = self.parser.with_context(
                        journal_id=self.journal.id
                    ).parse(
                        b"Date,Label,Amount,Balance\n" + row,
                        self.sample_statement_map,
                        "yearless.csv",
                    )
                    self.assertEqual(currency, "USD")
                    self.assertEqual(len(statements), 1)
                    statement = statements[0]
                    self.assertEqual(statement["date"], expected_date.date())
                    # Closing less the signed transaction independently gives 1000.
                    self.assertEqual(statement["balance_start"], 1000)
                    self.assertEqual(statement["balance_end_real"], closing)
                    self.assertEqual(len(statement["transactions"]), 1)
                    transaction = statement["transactions"][0]
                    self.assertEqual(transaction["date"], expected_date)
                    self.assertEqual(transaction["payment_ref"], label)
                    self.assertEqual(transaction["amount"], amount)
                    self.assertEqual(transaction["currency_id"], self.currency_usd.id)
                    self.assertNotIn("foreign_currency_id", transaction)
                    self.assertNotIn("amount_currency", transaction)

    def test_import_empty_csv_file(self):
        wizard = self._get_import_wizard("fixtures/empty_statement_en.csv")
        with self.assertRaises(UserError):
            wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 0)

    def test_import_xlsx_file(self):
        wizard = self._get_import_wizard("fixtures/sample_statement_en.xlsx")
        wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 2)

    def test_import_empty_xlsx_file(self):
        wizard = self._get_import_wizard("fixtures/empty_statement_en.xlsx")
        with self.assertRaises(UserError):
            wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 0)

    def test_original_currency(self):
        wizard = self._get_import_wizard("fixtures/original_currency.csv")
        wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 1)
        line = statement.line_ids
        self.assertEqual(line.currency_id, self.currency_usd)
        self.assertEqual(line.amount, 1525.0)
        self.assertEqual(line.foreign_currency_id, self.currency_eur)
        line_amount_currency = float_round(line.amount_currency, precision_digits=1)
        self.assertEqual(line_amount_currency, 1000.0)

    def test_original_currency_no_header(self):
        no_header_statement_map = self.AccountStatementImportSheetMapping.create(
            {
                "name": "Sample Statement",
                "float_thousands_sep": "comma",
                "float_decimal_sep": "dot",
                "header_lines_skip_count": 0,
                "delimiter": "comma",
                "quotechar": '"',
                "timestamp_format": "%m/%d/%Y",
                "no_header": True,
                "timestamp_column": "0",
                "amount_column": "3",
                "original_currency_column": "2",
                "original_amount_column": "4",
                "description_column": "1,7",
                "partner_name_column": "5",
                "bank_account_column": "6",
            }
        )
        wizard = self._get_import_wizard("fixtures/original_currency_no_header.csv")
        wizard.sheet_mapping_id = no_header_statement_map.id
        wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 1)
        line = statement.line_ids
        self.assertEqual(line.currency_id, self.currency_usd)
        self.assertEqual(line.foreign_currency_id, self.currency_eur)
        self.assertEqual(line.amount_currency, 1000.0)
        self.assertEqual(line.payment_ref, "Your payment INV0001")

    def test_original_currency_empty(self):
        wizard = self._get_import_wizard("fixtures/original_currency_empty.csv")
        wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 1)
        line = statement.line_ids
        self.assertFalse(line.foreign_currency_id)
        self.assertEqual(line.amount_currency, 0.0)

    def test_multi_currency(self):
        self.sample_statement_map.write(
            {
                "currency_column": "Currency",
                "original_currency_column": None,
                "original_amount_column": None,
            }
        )
        wizard = self._get_import_wizard("fixtures/multi_currency.csv")
        wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 1)
        line = statement.line_ids
        self.assertFalse(line.foreign_currency_id)
        self.assertEqual(line.amount, -33.5)

    def test_balance(self):
        self.sample_statement_map.write(
            {
                "balance_column": "Balance",
                "original_currency_column": None,
                "original_amount_column": None,
            }
        )
        wizard = self._get_import_wizard("fixtures/balance.csv")
        wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 2)
        self.assertEqual(statement.balance_start, 10.0)
        self.assertEqual(statement.balance_end_real, 1510.0)
        self.assertEqual(statement.balance_end, 1510.0)

    def test_debit_credit(self):
        self.sample_statement_map.write(
            {
                "balance_column": "Balance",
                "original_currency_column": None,
                "original_amount_column": None,
                "debit_credit_column": "D/C",
                "debit_value": "D",
                "credit_value": "C",
            }
        )
        wizard = self._get_import_wizard("fixtures/debit_credit.csv")
        wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 2)
        self.assertEqual(statement.balance_start, 10.0)
        self.assertEqual(statement.balance_end_real, 1510.0)
        self.assertEqual(statement.balance_end, 1510.0)

    def test_debit_credit_amount(self):
        self.sample_statement_map.write(
            {
                "amount_type": "distinct_credit_debit",
                "amount_debit_column": "Debit",
                "amount_credit_column": "Credit",
                "balance_column": "Balance",
                "amount_column": None,
                "original_currency_column": None,
                "original_amount_column": None,
            }
        )
        wizard = self._get_import_wizard("fixtures/debit_credit_amount.csv")
        wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 4)
        self.assertEqual(statement.balance_start, 10.0)
        self.assertEqual(statement.balance_end_real, 1510.0)
        self.assertEqual(statement.balance_end, 1510.0)

    def test_metadata_separated_debit_credit_csv(self):
        self.sample_statement_map.write(
            {
                "footer_lines_skip_count": 1,
                "header_lines_skip_count": 5,
                "amount_column": None,
                "partner_name_column": None,
                "bank_account_column": None,
                "float_thousands_sep": "none",
                "float_decimal_sep": "comma",
                "timestamp_format": "%m/%d/%y",
                "original_currency_column": None,
                "original_amount_column": None,
                "amount_type": "distinct_credit_debit",
                "amount_debit_column": "Debit",
                "amount_credit_column": "Credit",
            }
        )
        wizard = self._get_import_wizard(
            "fixtures/meta_data_separated_credit_debit.csv"
        )
        wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 4)
        line1 = statement.line_ids.filtered(lambda x: x.payment_ref == "LABEL 1")
        line4 = statement.line_ids.filtered(lambda x: x.payment_ref == "LABEL 4")
        self.assertEqual(line1.amount, 50)
        self.assertEqual(line4.amount, -1300)

    def test_metadata_separated_debit_credit_xlsx(self):
        self.sample_statement_map.write(
            {
                "footer_lines_skip_count": 1,
                "header_lines_skip_count": 5,
                "amount_column": None,
                "partner_name_column": None,
                "bank_account_column": None,
                "float_thousands_sep": "none",
                "float_decimal_sep": "comma",
                "timestamp_format": "%m/%d/%y",
                "original_currency_column": None,
                "original_amount_column": None,
                "amount_type": "distinct_credit_debit",
                "amount_debit_column": "Debit",
                "amount_credit_column": "Credit",
            }
        )
        wizard = self._get_import_wizard(
            "fixtures/meta_data_separated_credit_debit.xlsx"
        )
        wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 4)
        line1 = statement.line_ids.filtered(lambda x: x.payment_ref == "LABEL 1")
        line4 = statement.line_ids.filtered(lambda x: x.payment_ref == "LABEL 4")
        self.assertEqual(line1.amount, 50)
        self.assertEqual(line4.amount, -1300)

    def test_amount_inverse_sign(self):
        self.sample_statement_map.amount_inverse_sign = True
        wizard = self._get_import_wizard(
            "fixtures/sample_statement_credit_card_inverse_sign_en.csv"
        )
        wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 2)
        line1 = statement.line_ids.filtered(lambda x: x.payment_ref == "LABEL 1")
        self.assertEqual(line1.amount, -33.50)
        line2 = statement.line_ids.filtered(lambda x: x.payment_ref == "LABEL 2")
        self.assertEqual(line2.amount, 1525.00)
        self.assertEqual(line2.amount_currency, 1000.00)

    def test_import_xlsx_empty_values(self):
        sample_statement_map_empty_values = (
            self.AccountStatementImportSheetMapping.create(
                {
                    "name": "Sample Statement with empty values",
                    "amount_type": "distinct_credit_debit",
                    "float_decimal_sep": "comma",
                    "delimiter": "n/a",
                    "no_header": 0,
                    "footer_lines_skip_count": 1,
                    "amount_inverse_sign": 0,
                    "header_lines_skip_count": 1,
                    "quotechar": '"',
                    "float_thousands_sep": "dot",
                    "reference_column": "REF",
                    "description_column": "DESCRIPTION",
                    "amount_credit_column": "DEBIT",
                    "amount_debit_column": "CREDIT",
                    "balance_column": "BALANCE",
                    "timestamp_format": "%d/%m/%Y",
                    "timestamp_column": "DATE",
                }
            )
        )
        wizard = self._get_import_wizard(
            "fixtures/sample_statement_en_empty_values.xlsx"
        )
        wizard.sheet_mapping_id = sample_statement_map_empty_values.id
        wizard.import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 3)

    def test_mapping_separator_onchanges_preserve_import_amounts(self):
        cases = (
            (
                "comma",
                "dot",
                "float_thousands_sep",
                "dot",
                "dot",
                "comma",
                "1.234,56",
                "-25,00",
            ),
            (
                "dot",
                "comma",
                "float_thousands_sep",
                "comma",
                "comma",
                "dot",
                "1,234.56",
                "-25.00",
            ),
            (
                "dot",
                "comma",
                "float_decimal_sep",
                "dot",
                "comma",
                "dot",
                "1,234.56",
                "-25.00",
            ),
            (
                "comma",
                "dot",
                "float_decimal_sep",
                "comma",
                "dot",
                "comma",
                "1.234,56",
                "-25,00",
            ),
            (
                "comma",
                "dot",
                "float_thousands_sep",
                "quote",
                "quote",
                "dot",
                "1'234.56",
                "-25.00",
            ),
            (
                "comma",
                "dot",
                "float_decimal_sep",
                "none",
                "comma",
                "none",
                "123456",
                "-2500",
            ),
        )
        for (
            thousands,
            decimal,
            changed,
            value,
            expected_thousands,
            expected_decimal,
            deposit,
            fee,
        ) in cases:
            with self.subTest(field=changed, value=value, initial=(thousands, decimal)):
                mapping = self.sample_statement_map.copy(
                    {
                        "name": "Separator import fixture",
                        "float_thousands_sep": thousands,
                        "float_decimal_sep": decimal,
                        "delimiter": "semicolon",
                        "timestamp_format": "%m/%d/%Y",
                        "amount_type": "simple_value",
                        "amount_column": "Amount",
                        "balance_column": False,
                        "currency_column": False,
                        "original_currency_column": False,
                        "original_amount_column": False,
                        "partner_name_column": False,
                        "bank_name_column": False,
                        "bank_account_column": False,
                        "transaction_id_column": False,
                        "reference_column": False,
                        "notes_column": False,
                    }
                )
                with Form(
                    mapping,
                    view="account_statement_import_sheet_file.account_statement_import_sheet_mapping_tree",
                ) as mapping_form:
                    setattr(mapping_form, changed, value)
                self.assertEqual(mapping.float_thousands_sep, expected_thousands)
                self.assertEqual(mapping.float_decimal_sep, expected_decimal)
                csv_data = (
                    "Date;Label;Amount\n"
                    f"09/01/2026;Deposit;{deposit}\n"
                    f"09/02/2026;Fee;{fee}\n"
                ).encode()
                currency, _account, statements = self.parser.with_context(
                    journal_id=self.journal.id
                ).parse(csv_data, mapping, "separators.csv")
                self.assertEqual(currency, "USD")
                self.assertEqual(len(statements), 1)
                transactions = statements[0]["transactions"]
                self.assertEqual(len(transactions), 2)
                self.assertEqual(
                    [line["date"] for line in transactions],
                    [datetime(2026, 9, 1), datetime(2026, 9, 2)],
                )
                self.assertEqual(
                    [line["payment_ref"] for line in transactions], ["Deposit", "Fee"]
                )
                self.assertEqual(
                    [line["amount"] for line in transactions], ["1234.56", "-25.0"]
                )
                self.assertEqual(
                    sum(Decimal(line["amount"]) for line in transactions),
                    Decimal("1209.56"),
                )
                for line in transactions:
                    self.assertEqual(line["currency_id"], self.currency_usd.id)
                    self.assertNotIn("foreign_currency_id", line)
                    self.assertNotIn("amount_currency", line)

    def test_mapping_rejects_incomplete_amount_configuration(self):
        cases = (
            (
                {"amount_type": "simple_value", "amount_column": False},
                "Use amount_column",
            ),
            (
                {"amount_type": "absolute_value", "debit_credit_column": False},
                "Use debit_credit_column",
            ),
            (
                {
                    "amount_type": "distinct_credit_debit",
                    "amount_debit_column": False,
                    "amount_credit_column": "Credit",
                },
                "Use amount_debit_column and amount_credit_column",
            ),
            (
                {
                    "amount_type": "distinct_credit_debit",
                    "amount_debit_column": "Debit",
                    "amount_credit_column": False,
                },
                "Use amount_debit_column and amount_credit_column",
            ),
            ({"offset_column": -1}, "Offsets cannot be negative"),
        )
        mapping = self.sample_statement_map.copy({"name": "Invalid mapping fixture"})
        for values, message in cases:
            with self.subTest(values=values):
                original = {field: mapping[field] for field in values}
                with (
                    self.assertRaisesRegex(ValidationError, message),
                    self.env.cr.savepoint(),
                ):
                    mapping.with_context(lang="en_US").write(values)
                self.assertEqual({field: mapping[field] for field in values}, original)

    def test_parse_decimal(self):
        # Define a series of test cases
        test_cases = [
            (
                "1,234.56",
                1234.56,
                self.mock_mapping_comma_dot,
            ),  # standard case with thousands separator
            (
                "1,234,567.89",
                1234567.89,
                self.mock_mapping_comma_dot,
            ),  # multiple thousands separators
            (
                "-1,234.56",
                -1234.56,
                self.mock_mapping_comma_dot,
            ),  # negative value
            (
                "$1,234.56",
                1234.56,
                self.mock_mapping_comma_dot,
            ),  # prefixed with currency symbol
            (
                "1,234.56 USD",
                1234.56,
                self.mock_mapping_comma_dot,
            ),  # suffixed with currency code
            (
                "   1,234.56   ",
                1234.56,
                self.mock_mapping_comma_dot,
            ),  # leading and trailing spaces
            (
                "not a number",
                0,
                self.mock_mapping_comma_dot,
            ),  # non-numeric input
            (" ", 0, self.mock_mapping_comma_dot),  # empty string
            ("", 0, self.mock_mapping_comma_dot),  # empty space
            ("USD", 0, self.mock_mapping_comma_dot),  # empty dolar
            (
                "12,34.56",
                1234.56,
                self.mock_mapping_comma_dot,
            ),  # unusual thousand separator placement
            (
                "1234,567.89",
                1234567.89,
                self.mock_mapping_comma_dot,
            ),  # missing one separator
            (
                "1234.567,89",
                1234567.89,
                self.mock_mapping_dot_comma,
            ),  # inverted separators
            (
                "123456",
                1234.56,
                self.mock_mapping_none_none,
            ),  # no separator
        ]

        for value, expected, mock_mapping in test_cases:
            with self.subTest(value=value):
                result = self.parser._parse_decimal(value, mock_mapping)
                self.assertEqual(result, expected, f"Failed for value: {value}")

    def test_decimal_and_float_inputs(self):
        # Test direct Decimal and float inputs
        self.assertEqual(
            self.parser._parse_decimal(-1234.56, self.mock_mapping_comma_dot),
            -1234.56,
        )
        self.assertEqual(
            self.parser._parse_decimal(1234.56, self.mock_mapping_comma_dot),
            1234.56,
        )
        self.assertEqual(
            self.parser._parse_decimal(
                Decimal("-1234.56"), self.mock_mapping_comma_dot
            ),
            -1234.56,
        )
        self.assertEqual(
            self.parser._parse_decimal(Decimal("1234.56"), self.mock_mapping_comma_dot),
            1234.56,
        )

    @mute_logger(
        "odoo.addons.account_statement_import_sheet_file.models."
        "account_statement_import"
    )
    def test_offsets(self):
        journal = self.journal
        file_name = "fixtures/sample_statement_offsets.xlsx"
        data = self._data_file(file_name)
        wizard = self.AccountStatementImport.with_context(journal_id=journal.id).create(
            {
                "statement_filename": file_name,
                "statement_file": data,
                "sheet_mapping_id": self.sample_statement_map.id,
            }
        )
        # First try with incorrect values
        with self.assertRaises(UserError):
            wizard.with_context(
                account_statement_import_txt_xlsx_test=True
            ).import_file_button()
        self.sample_statement_map.write(
            {"offset_column": 1, "header_lines_skip_count": 3}
        )
        wizard.with_context(
            account_statement_import_txt_xlsx_test=True
        ).import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 2)
        self.assertEqual(statement.balance_start, 0.0)
        self.assertEqual(statement.balance_end_real, 1491.5)
        self.assertEqual(statement.balance_end, 1491.5)

    @mute_logger(
        "odoo.addons.account_statement_import_sheet_file.models."
        "account_statement_import"
    )
    def test_skip_empty_lines(self):
        journal = self.journal
        file_name = "fixtures/empty_lines_statement.csv"
        data = self._data_file(file_name, "utf-8")
        self.sample_statement_map.skip_empty_lines = False
        wizard = self.AccountStatementImport.with_context(journal_id=journal.id).create(
            {
                "statement_filename": file_name,
                "statement_file": data,
                "sheet_mapping_id": self.sample_statement_map.id,
            }
        )
        with self.assertRaises(UserError):
            wizard.with_context(
                account_statement_import_txt_xlsx_test=True
            ).import_file_button()
        self.sample_statement_map.skip_empty_lines = True
        wizard.with_context(
            account_statement_import_txt_xlsx_test=True
        ).import_file_button()
        statement = self.AccountBankStatement.search(self.statement_domain)
        self.assertEqual(len(statement), 1)
        self.assertEqual(len(statement.line_ids), 3)
        self.assertEqual(statement.balance_start, 0.0)
        self.assertEqual(statement.balance_end_real, 2291.5)
        self.assertEqual(statement.balance_end, 2291.5)

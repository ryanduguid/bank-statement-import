# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2021-2022 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest import mock
from urllib.error import HTTPError

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common

_module_ns = "odoo.addons.account_statement_import_online_paypal"
_provider_class = (
    _module_ns
    + ".models.online_bank_statement_provider_paypal"
    + ".OnlineBankStatementProviderPayPal"
)


class FakeHTTPError(HTTPError):
    def __init__(self, content):
        self.content = content

    # pylint: disable=method-required-super
    def read(self):
        return self.content.encode("utf-8")


class UrlopenRetValMock:
    def __init__(self, content, throw=False):
        self.content = content
        self.throw = throw

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    # pylint: disable=method-required-super
    def read(self):
        if self.throw:
            raise FakeHTTPError(self.content)
        return self.content.encode("utf-8")


class TestAccountBankAccountStatementImportOnlinePayPal(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.now = fields.Datetime.now()
        self.now_isoformat = self.now.isoformat() + "+0000"
        self.today = datetime(self.now.year, self.now.month, self.now.day)
        self.today_isoformat = self.today.isoformat() + "+0000"
        self.today_timestamp = str(int(self.today.timestamp()))
        self.yesterday = self.today - relativedelta(days=1)
        self.yesterday_isoformat = self.yesterday.isoformat() + "+0000"
        self.yesterday_timestamp = str(int(self.yesterday.timestamp()))
        self.currency_eur = self.env.ref("base.EUR")
        self.currency_usd = self.env.ref("base.USD")
        self.AccountJournal = self.env["account.journal"]
        self.OnlineBankStatementProvider = self.env["online.bank.statement.provider"]
        self.AccountBankStatement = self.env["account.bank.statement"]
        self.AccountBankStatementLine = self.env["account.bank.statement.line"]

        Provider = self.OnlineBankStatementProvider
        self.paypal_parse_transaction = lambda payload: (
            Provider._paypal_transaction_to_lines(
                Provider._paypal_preparse_transaction(
                    json.loads(
                        payload,
                        parse_float=Decimal,
                    )
                )
            )
        )
        self.mock_token = lambda: mock.patch(
            _provider_class + "._paypal_get_token",
            return_value="--TOKEN--",
        )

    def test_request_authentication_preserves_the_body_and_destination(self):
        url = "https://example.com/paypal-fixture"
        body = b"grant_type=client_credentials"
        for auth, expected in (
            (
                ("fixture-client", "fixture-secret"),
                "Basic Zml4dHVyZS1jbGllbnQ6Zml4dHVyZS1zZWNyZXQ=",
            ),
            ("fixture-access-token", "Bearer fixture-access-token"),
        ):
            with self.subTest(auth=expected.split()[0]):
                response = object()
                with mock.patch(
                    "urllib.request.urlopen", return_value=response
                ) as urlopen:
                    result = self.OnlineBankStatementProvider._paypal_urlopen(
                        url, auth, data=body
                    )
                self.assertIs(result, response)
                urlopen.assert_called_once()
                request = urlopen.call_args.args[0]
                self.assertEqual(request.full_url, url)
                self.assertEqual(request.get_method(), "POST")
                self.assertEqual(request.get_header("Authorization"), expected)
                self.assertEqual(request.data, body)

    def test_invalid_authentication_is_refused_before_opening_a_connection(self):
        for auth, message in (
            (None, "No authentication specified"),
            ("", "No authentication specified"),
            (42, "Unknown authentication specified"),
        ):
            with self.subTest(auth=auth):
                with mock.patch("urllib.request.urlopen") as urlopen:
                    with self.assertRaisesRegex(UserError, message):
                        self.OnlineBankStatementProvider._paypal_urlopen(
                            "https://example.com/paypal-fixture", auth
                        )
                urlopen.assert_not_called()

    def test_good_token(self):
        journal = self.AccountJournal.create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BANK",
                "currency_id": self.currency_eur.id,
                "bank_statements_source": "online",
                "online_bank_statement_provider": "paypal",
            }
        )

        provider = journal.online_bank_statement_provider_id
        mocked_response = json.loads(
            """{
    "scope": "https://uri.paypal.com/services/reporting/search/read",
    "access_token": "---TOKEN---",
    "token_type": "Bearer",
    "app_id": "APP-1234567890",
    "expires_in": 32400,
    "nonce": "---NONCE---"
}""",
            parse_float=Decimal,
        )
        with mock.patch(
            _provider_class + "._paypal_retrieve",
            return_value=mocked_response,
        ):
            token = provider._paypal_get_token()
        self.assertEqual(token, "---TOKEN---")

    def test_bad_token_scope(self):
        journal = self.AccountJournal.create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BANK",
                "currency_id": self.currency_eur.id,
                "bank_statements_source": "online",
                "online_bank_statement_provider": "paypal",
            }
        )

        provider = journal.online_bank_statement_provider_id
        mocked_response = json.loads(
            """{
    "scope": "openid https://uri.paypal.com/services/applications/webhooks",
    "access_token": "---TOKEN---",
    "token_type": "Bearer",
    "app_id": "APP-1234567890",
    "expires_in": 32400,
    "nonce": "---NONCE---"
}""",
            parse_float=Decimal,
        )
        with mock.patch(
            _provider_class + "._paypal_retrieve",
            return_value=mocked_response,
        ):
            with self.assertRaisesRegex(
                UserError, "PayPal App features are configured incorrectly!"
            ):
                provider._paypal_get_token()

    def test_bad_token_type(self):
        journal = self.AccountJournal.create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BANK",
                "currency_id": self.currency_eur.id,
                "bank_statements_source": "online",
                "online_bank_statement_provider": "paypal",
            }
        )

        provider = journal.online_bank_statement_provider_id
        mocked_response = json.loads(
            """{
    "scope": "https://uri.paypal.com/services/reporting/search/read",
    "access_token": "---TOKEN---",
    "token_type": "NotBearer",
    "app_id": "APP-1234567890",
    "expires_in": 32400,
    "nonce": "---NONCE---"
}""",
            parse_float=Decimal,
        )
        with mock.patch(
            _provider_class + "._paypal_retrieve",
            return_value=mocked_response,
        ):
            with self.assertRaisesRegex(UserError, "Invalid token type!"):
                provider._paypal_get_token()

    def test_no_token(self):
        journal = self.AccountJournal.create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BANK",
                "currency_id": self.currency_eur.id,
                "bank_statements_source": "online",
                "online_bank_statement_provider": "paypal",
            }
        )

        provider = journal.online_bank_statement_provider_id
        mocked_response = json.loads(
            """{
        "scope": "https://uri.paypal.com/services/reporting/search/read",
        "token_type": "Bearer",
        "app_id": "APP-1234567890",
        "expires_in": 32400,
        "nonce": "---NONCE---"
    }""",
            parse_float=Decimal,
        )
        with mock.patch(
            _provider_class + "._paypal_retrieve",
            return_value=mocked_response,
        ):
            with self.assertRaisesRegex(
                UserError, "Failed to acquire token using Client ID and Secret!"
            ):
                provider._paypal_get_token()

    def test_no_data_on_monday(self):
        journal = self.AccountJournal.create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BANK",
                "currency_id": self.currency_eur.id,
                "bank_statements_source": "online",
                "online_bank_statement_provider": "paypal",
            }
        )

        provider = journal.online_bank_statement_provider_id
        mocked_response_1 = UrlopenRetValMock(
            """{
    "debug_id": "eec890ebd5798",
    "details": "xxxxxx",
    "links": "xxxxxx",
    "message": "Data for the given start date is not available.",
    "name": "INVALID_REQUEST"
}""",
            throw=True,
        )
        mocked_response_2 = UrlopenRetValMock(
            f"""{{
    "balances": [
        {{
            "currency": "EUR",
            "primary": true,
            "total_balance": {{
                "currency_code": "EUR",
                "value": "0.75"
            }},
            "available_balance": {{
                "currency_code": "EUR",
                "value": "0.75"
            }},
            "withheld_balance": {{
                "currency_code": "EUR",
                "value": "0.00"
            }}
        }}
    ],
    "account_id": "1234567890",
    "as_of_time": "{self.now_isoformat}",
    "last_refresh_time": "{self.now_isoformat}"
}}"""
        )
        with (
            mock.patch(
                _provider_class + "._paypal_urlopen",
                side_effect=[mocked_response_1, mocked_response_2],
            ),
            self.mock_token(),
        ):
            data = provider.with_context(
                test_account_statement_import_online_paypal_monday=True,
            )._obtain_statement_data(
                self.now - relativedelta(hours=1),
                self.now,
            )

        self.assertEqual(data, ([], {"balance_start": 0.75, "balance_end_real": 0.75}))

    def test_error_handling_1(self):
        journal = self.AccountJournal.create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BANK",
                "currency_id": self.currency_eur.id,
                "bank_statements_source": "online",
                "online_bank_statement_provider": "paypal",
            }
        )

        provider = journal.online_bank_statement_provider_id
        mocked_response = UrlopenRetValMock(
            """{
    "message": "MESSAGE",
    "name": "ERROR"
}""",
            throw=True,
        )
        with mock.patch(
            _provider_class + "._paypal_urlopen",
            return_value=mocked_response,
        ):
            with self.assertRaises(UserError):
                provider._paypal_retrieve("https://url", "")

    def test_error_handling_2(self):
        journal = self.AccountJournal.create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BANK",
                "currency_id": self.currency_eur.id,
                "bank_statements_source": "online",
                "online_bank_statement_provider": "paypal",
            }
        )

        provider = journal.online_bank_statement_provider_id
        mocked_response = UrlopenRetValMock(
            """{
    "error_description": "ERROR DESCRIPTION",
    "error": "ERROR"
}""",
            throw=True,
        )
        with mock.patch(
            _provider_class + "._paypal_urlopen",
            return_value=mocked_response,
        ):
            with self.assertRaises(UserError):
                provider._paypal_retrieve("https://url", "")

    def test_create_empty_paypal_statements(self):
        """Test creating empty PayPal statements
        ('Allow empty statements' field is checked).
        """
        journal = self.AccountJournal.create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BANK",
                "currency_id": self.currency_eur.id,
                "bank_statements_source": "online",
                "online_bank_statement_provider": "paypal",
            }
        )

        provider = journal.online_bank_statement_provider_id
        mocked_response_1 = json.loads(f"""{{
    "transaction_details": [],
    "account_number": "1234567890",
    "start_date": "{self.now_isoformat}",
    "end_date": "{self.now_isoformat}",
    "last_refreshed_datetime": "{self.now_isoformat}",
    "page": 1,
    "total_items": 0,
    "total_pages": 0
}}""")
        mocked_response_2 = json.loads(f"""{{
    "balances": [
        {{
            "currency": "EUR",
            "primary": true,
            "total_balance": {{
                "currency_code": "EUR",
                "value": "0.75"
            }},
            "available_balance": {{
                "currency_code": "EUR",
                "value": "0.75"
            }},
            "withheld_balance": {{
                "currency_code": "EUR",
                "value": "0.00"
            }}
        }}
    ],
    "account_id": "1234567890",
    "as_of_time": "{self.now_isoformat}",
    "last_refresh_time": "{self.now_isoformat}"
}}""")
        with (
            mock.patch(
                _provider_class + "._paypal_retrieve",
                side_effect=[mocked_response_1, mocked_response_2],
            ),
            self.mock_token(),
        ):
            data = provider._obtain_statement_data(
                self.now - relativedelta(hours=1),
                self.now,
            )

        self.assertEqual(data, ([], {"balance_start": 0.75, "balance_end_real": 0.75}))

    def test_ancient_pull(self):
        journal = self.AccountJournal.create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BANK",
                "currency_id": self.currency_eur.id,
                "bank_statements_source": "online",
                "online_bank_statement_provider": "paypal",
            }
        )

        provider = journal.online_bank_statement_provider_id
        mocked_response = json.loads(f"""{{
    "transaction_details": [],
    "account_number": "1234567890",
    "start_date": "{self.now_isoformat}",
    "end_date": "{self.now_isoformat}",
    "last_refreshed_datetime": "{self.now_isoformat}",
    "page": 1,
    "total_items": 0,
    "total_pages": 0
}}""")
        with (
            mock.patch(
                _provider_class + "._paypal_retrieve",
                return_value=mocked_response,
            ),
            self.mock_token(),
        ):
            with self.assertRaisesRegex(
                UserError,
                "PayPal allows retrieving transactions only up to 3 years in "
                "the past. Please import older transactions manually.",
            ):
                provider._obtain_statement_data(
                    self.now - relativedelta(years=5),
                    self.now,
                )

    def test_pull(self):
        journal = self.AccountJournal.create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BANK",
                "currency_id": self.currency_eur.id,
                "bank_statements_source": "online",
                "online_bank_statement_provider": "paypal",
            }
        )

        provider = journal.online_bank_statement_provider_id
        mocked_response = json.loads(f"""{{
    "transaction_details": [{{
        "transaction_info": {{
            "paypal_account_id": "1234567890",
            "transaction_id": "1234567890",
            "transaction_event_code": "T1234",
            "transaction_initiation_date": "{self.yesterday_isoformat}",
            "transaction_updated_date": "{self.yesterday_isoformat}",
            "transaction_amount": {{
                "currency_code": "USD",
                "value": "1000.00"
            }},
            "fee_amount": {{
                "currency_code": "USD",
                "value": "-100.00"
            }},
            "transaction_status": "S",
            "transaction_subject": "Payment for Invoice(s) 1",
            "ending_balance": {{
                "currency_code": "USD",
                "value": "900.00"
            }},
            "available_balance": {{
                "currency_code": "USD",
                "value": "900.00"
            }},
            "invoice_id": "1"
        }},
        "payer_info": {{
            "account_id": "1234567890",
            "email_address": "partner@example.com",
            "address_status": "Y",
            "payer_status": "N",
            "payer_name": {{
                "alternate_full_name": "Acme, Inc."
            }},
            "country_code": "US"
        }},
        "shipping_info": {{}},
        "cart_info": {{}},
        "store_info": {{}},
        "auction_info": {{}},
        "incentive_info": {{}}
    }}, {{
        "transaction_info": {{
            "paypal_account_id": "1234567890",
            "transaction_id": "1234567891",
            "transaction_event_code": "T1234",
            "transaction_initiation_date": "{self.today_isoformat}",
            "transaction_updated_date": "{self.today_isoformat}",
            "transaction_amount": {{
                "currency_code": "USD",
                "value": "1000.00"
            }},
            "fee_amount": {{
                "currency_code": "USD",
                "value": "-100.00"
            }},
            "transaction_status": "S",
            "transaction_subject": "Payment for Invoice(s) 1",
            "ending_balance": {{
                "currency_code": "USD",
                "value": "900.00"
            }},
            "available_balance": {{
                "currency_code": "USD",
                "value": "900.00"
            }},
            "invoice_id": "1"
        }},
        "payer_info": {{
            "account_id": "1234567890",
            "email_address": "partner@example.com",
            "address_status": "Y",
            "payer_status": "N",
            "payer_name": {{
                "alternate_full_name": "Acme, Inc."
            }},
            "country_code": "US"
        }},
        "shipping_info": {{}},
        "cart_info": {{}},
        "store_info": {{}},
        "auction_info": {{}},
        "incentive_info": {{}}
    }}],
    "account_number": "1234567890",
    "start_date": "{self.yesterday_isoformat}",
    "end_date": "{self.today_isoformat}",
    "last_refreshed_datetime": "{self.now_isoformat}",
    "page": 1,
    "total_items": 1,
    "total_pages": 1
}}""")
        with (
            mock.patch(
                _provider_class + "._paypal_retrieve",
                return_value=mocked_response,
            ),
            self.mock_token(),
        ):
            data = provider._obtain_statement_data(
                self.yesterday,
                self.today,
            )

        self.assertEqual(len(data[0]), 2)
        del data[0][0]["raw_data"]
        self.assertEqual(
            data[0][0],
            {
                "date": self.yesterday,
                "amount": "1000.00",
                "ref": "Invoice 1",
                "payment_ref": "1234567890: Payment for Invoice(s) 1",
                "partner_name": "Acme, Inc.",
                "unique_import_id": f"1234567890-{self.yesterday_timestamp}",
            },
        )
        self.assertEqual(
            data[0][1],
            {
                "date": self.yesterday,
                "amount": "-100.00",
                "ref": "Fee for Invoice 1",
                "payment_ref": "Transaction fee for 1234567890: Payment for Invoice(s)"
                " 1",
                "partner_name": "PayPal",
                "unique_import_id": f"1234567890-{self.yesterday_timestamp}-FEE",
            },
        )
        self.assertEqual(data[1], {"balance_start": 0.0, "balance_end_real": 900.0})

    def test_transaction_parse_1(self):
        lines = self.paypal_parse_transaction(f"""{{
    "transaction_info": {{
        "paypal_account_id": "1234567890",
        "transaction_id": "1234567890",
        "transaction_event_code": "T1234",
        "transaction_initiation_date": "{self.today_isoformat}",
        "transaction_updated_date": "{self.today_isoformat}",
        "transaction_amount": {{
            "currency_code": "USD",
            "value": "1000.00"
        }},
        "fee_amount": {{
            "currency_code": "USD",
            "value": "0.00"
        }},
        "transaction_status": "S",
        "transaction_subject": "Payment for Invoice(s) 1",
        "ending_balance": {{
            "currency_code": "USD",
            "value": "1000.00"
        }},
        "available_balance": {{
            "currency_code": "USD",
            "value": "1000.00"
        }},
        "invoice_id": "1"
    }},
    "payer_info": {{
        "account_id": "1234567890",
        "email_address": "partner@example.com",
        "address_status": "Y",
        "payer_status": "N",
        "payer_name": {{
            "alternate_full_name": "Acme, Inc."
        }},
        "country_code": "US"
    }},
    "shipping_info": {{}},
    "cart_info": {{}},
    "store_info": {{}},
    "auction_info": {{}},
    "incentive_info": {{}}
}}""")
        self.assertEqual(len(lines), 1)
        del lines[0]["raw_data"]
        self.assertEqual(
            lines[0],
            {
                "date": self.today,
                "amount": "1000.00",
                "ref": "Invoice 1",
                "payment_ref": "1234567890: Payment for Invoice(s) 1",
                "partner_name": "Acme, Inc.",
                "unique_import_id": f"1234567890-{self.today_timestamp}",
            },
        )

    def test_transaction_parse_2(self):
        lines = self.paypal_parse_transaction(f"""{{
    "transaction_info": {{
        "paypal_account_id": "1234567890",
        "transaction_id": "1234567890",
        "transaction_event_code": "T1234",
        "transaction_initiation_date": "{self.today_isoformat}",
        "transaction_updated_date": "{self.today_isoformat}",
        "transaction_amount": {{
            "currency_code": "USD",
            "value": "1000.00"
        }},
        "fee_amount": {{
            "currency_code": "USD",
            "value": "0.00"
        }},
        "transaction_status": "S",
        "transaction_subject": "Payment for Invoice(s) 1",
        "ending_balance": {{
            "currency_code": "USD",
            "value": "1000.00"
        }},
        "available_balance": {{
            "currency_code": "USD",
            "value": "1000.00"
        }},
        "invoice_id": "1"
    }},
    "payer_info": {{
        "account_id": "1234567890",
        "email_address": "partner@example.com",
        "address_status": "Y",
        "payer_status": "N",
        "payer_name": {{
            "alternate_full_name": "Acme, Inc."
        }},
        "country_code": "US"
    }},
    "shipping_info": {{}},
    "cart_info": {{}},
    "store_info": {{}},
    "auction_info": {{}},
    "incentive_info": {{}}
}}""")

        self.assertEqual(len(lines), 1)
        del lines[0]["raw_data"]
        self.assertEqual(
            lines[0],
            {
                "date": self.today,
                "amount": "1000.00",
                "ref": "Invoice 1",
                "payment_ref": "1234567890: Payment for Invoice(s) 1",
                "partner_name": "Acme, Inc.",
                "unique_import_id": f"1234567890-{self.today_timestamp}",
            },
        )

    def test_transaction_parse_3(self):
        lines = self.paypal_parse_transaction(f"""{{
    "transaction_info": {{
        "paypal_account_id": "1234567890",
        "transaction_id": "1234567890",
        "transaction_event_code": "T1234",
        "transaction_initiation_date": "{self.today_isoformat}",
        "transaction_updated_date": "{self.today_isoformat}",
        "transaction_amount": {{
            "currency_code": "USD",
            "value": "1000.00"
        }},
        "fee_amount": {{
            "currency_code": "USD",
            "value": "-100.00"
        }},
        "transaction_status": "S",
        "transaction_subject": "Payment for Invoice(s) 1",
        "ending_balance": {{
            "currency_code": "USD",
            "value": "900.00"
        }},
        "available_balance": {{
            "currency_code": "USD",
            "value": "900.00"
        }},
        "invoice_id": "1"
    }},
    "payer_info": {{
        "account_id": "1234567890",
        "email_address": "partner@example.com",
        "address_status": "Y",
        "payer_status": "N",
        "payer_name": {{
            "alternate_full_name": "Acme, Inc."
        }},
        "country_code": "US"
    }},
    "shipping_info": {{}},
    "cart_info": {{}},
    "store_info": {{}},
    "auction_info": {{}},
    "incentive_info": {{}}
}}""")
        self.assertEqual(len(lines), 2)
        del lines[0]["raw_data"]
        self.assertEqual(
            lines[0],
            {
                "date": self.today,
                "amount": "1000.00",
                "ref": "Invoice 1",
                "payment_ref": "1234567890: Payment for Invoice(s) 1",
                "partner_name": "Acme, Inc.",
                "unique_import_id": f"1234567890-{self.today_timestamp}",
            },
        )
        self.assertEqual(
            lines[1],
            {
                "date": self.today,
                "amount": "-100.00",
                "ref": "Fee for Invoice 1",
                "payment_ref": "Transaction fee for 1234567890: Payment for Invoice(s)"
                " 1",
                "partner_name": "PayPal",
                "unique_import_id": f"1234567890-{self.today_timestamp}-FEE",
            },
        )

    def test_transaction_parse_4(self):
        lines = self.paypal_parse_transaction(f"""{{
    "transaction_info": {{
        "paypal_account_id": "1234567890",
        "transaction_id": "1234567890",
        "transaction_event_code": "T1234",
        "transaction_initiation_date": "{self.today_isoformat}",
        "transaction_updated_date": "{self.today_isoformat}",
        "transaction_amount": {{
            "currency_code": "USD",
            "value": "1000.00"
        }},
        "transaction_status": "S",
        "transaction_subject": "Payment for Invoice(s) 1",
        "ending_balance": {{
            "currency_code": "USD",
            "value": "1000.00"
        }},
        "available_balance": {{
            "currency_code": "USD",
            "value": "1000.00"
        }},
        "invoice_id": "1"
    }},
    "payer_info": {{
        "account_id": "1234567890",
        "email_address": "partner@example.com",
        "address_status": "Y",
        "payer_status": "N",
        "payer_name": {{
            "alternate_full_name": "Acme, Inc."
        }},
        "country_code": "US"
    }},
    "shipping_info": {{}},
    "cart_info": {{}},
    "store_info": {{}},
    "auction_info": {{}},
    "incentive_info": {{}}
}}""")
        self.assertEqual(len(lines), 1)
        del lines[0]["raw_data"]
        self.assertEqual(
            lines[0],
            {
                "date": self.today,
                "amount": "1000.00",
                "ref": "Invoice 1",
                "payment_ref": "1234567890: Payment for Invoice(s) 1",
                "partner_name": "Acme, Inc.",
                "unique_import_id": f"1234567890-{self.today_timestamp}",
            },
        )

    def test_retrieve_invalid_json_response(self):
        """Cover new logic: if PayPal returns non-JSON body, raise UserError."""
        journal = self.AccountJournal.create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BANK",
                "currency_id": self.currency_eur.id,
                "bank_statements_source": "online",
                "online_bank_statement_provider": "paypal",
            }
        )
        provider = journal.online_bank_statement_provider_id
        mocked_response = UrlopenRetValMock("<html>not a json</html>", throw=False)
        with mock.patch(
            _provider_class + "._paypal_urlopen",
            return_value=mocked_response,
        ):
            with self.assertRaisesRegex(
                UserError, "Invalid JSON response from PayPal API"
            ):
                provider._paypal_retrieve("https://url", "--TOKEN--")

    def test_get_transactions_missing_transaction_details(self):
        """
        Response without `transaction_details` must
        not crash and should return empty list.
        """
        journal = self.AccountJournal.create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BANK",
                "currency_id": self.currency_eur.id,
                "bank_statements_source": "online",
                "online_bank_statement_provider": "paypal",
            }
        )
        provider = journal.online_bank_statement_provider_id
        # PayPal-like error payload without `transaction_details`
        mocked_payload = {
            "name": "INVALID_REQUEST",
            "message": "Request is not well-formed, syntactically "
            "incorrect, or violates schema.",
            # so that the page cycle ends correctly
            "total_pages": 0,
        }
        since = self.now - relativedelta(hours=1)
        until = self.now
        with mock.patch(
            _provider_class + "._paypal_retrieve",
            return_value=mocked_payload,
        ):
            tx = provider._paypal_get_transactions("--TOKEN--", "EUR", since, until)
        self.assertEqual(tx, [])

    def test_paypal_format_datetime(self):
        """
        Ensure PayPal datetime formatter drops
        microseconds and uses UTC Z format.
        """
        journal = self.AccountJournal.create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BANK",
                "currency_id": self.currency_eur.id,
                "bank_statements_source": "online",
                "online_bank_statement_provider": "paypal",
            }
        )
        provider = journal.online_bank_statement_provider_id
        # None -> None
        self.assertIsNone(provider._paypal_format_datetime(None))
        # Drops microseconds + Z format
        dt = datetime(2026, 1, 15, 11, 28, 27, 749445)  # naive UTC
        self.assertEqual(
            provider._paypal_format_datetime(dt),
            "2026-01-15T11:28:27Z",
        )

    def test_balance_transaction_lookup_follows_pages(self):
        from urllib.parse import parse_qs, urlsplit

        provider = self.OnlineBankStatementProvider.new({"service": "paypal"})
        wanted = {"transaction_info": {"transaction_id": "wanted"}}
        replies = [
            {
                "transaction_details": [
                    {"transaction_info": {"transaction_id": "other"}}
                ],
                "total_pages": 2,
            },
            {"transaction_details": [wanted], "total_pages": 2},
        ]
        with mock.patch(
            _provider_class + "._paypal_retrieve", side_effect=replies
        ) as retrieve:
            self.assertEqual(
                provider._paypal_get_transaction("synthetic", "wanted", self.today),
                wanted,
            )
        queries = [
            parse_qs(urlsplit(call.args[0]).query) for call in retrieve.call_args_list
        ]
        self.assertEqual([query["page"] for query in queries], [["1"], ["2"]])
        self.assertTrue(all(query["transaction_id"] == ["wanted"] for query in queries))
        self.assertTrue(
            all(query["balance_affecting_records_only"] == ["Y"] for query in queries)
        )
        for reply in ({"transaction_details": []}, {"total_pages": None}):
            with (
                self.subTest(reply=reply),
                mock.patch(
                    _provider_class + "._paypal_retrieve", return_value=reply
                ) as retrieve,
            ):
                self.assertIsNone(
                    provider._paypal_get_transaction("synthetic", "missing", self.today)
                )
                retrieve.assert_called_once()

    def test_balance_lookups_use_single_or_distinct_transactions(self):
        journal = self.AccountJournal.create(
            {"name": "Synthetic PayPal", "code": "PST", "type": "bank"}
        )
        provider = self.OnlineBankStatementProvider.new(
            {"service": "paypal", "journal_id": journal.id}
        )
        date = self.today
        transaction_id = "fabricated-transaction"
        first_transaction = {
            "transaction_info": {
                "transaction_id": transaction_id,
                "transaction_updated_date": date,
                "transaction_amount": {"value": "7.50"},
                "fee_amount": {"value": "-0.25"},
                "available_balance": {"value": "120.00"},
            }
        }
        last_date = date + timedelta(hours=1)
        last_transaction = {
            "transaction_info": {
                "transaction_id": "fabricated-last",
                "transaction_updated_date": last_date,
                "transaction_amount": {"value": "20.00"},
                "available_balance": {"value": "140.00"},
            },
        }
        offset = timedelta(hours=10)
        since = date.replace(tzinfo=timezone(offset))
        until = since + timedelta(days=1)
        with (
            mock.patch(
                _provider_class + "._paypal_get_token", return_value="synthetic"
            ),
            mock.patch(
                _provider_class + "._paypal_get_transactions",
                return_value=[first_transaction],
            ) as transactions,
            mock.patch(
                _provider_class + "._paypal_get_transaction",
                return_value=first_transaction,
            ) as lookup,
        ):
            lines, balances = provider._obtain_statement_data(since, until)
            transactions.assert_called_once_with(
                "synthetic",
                self.env.company.currency_id.name,
                date - offset,
                date + timedelta(days=1) - offset,
            )
            lookup.assert_called_once_with("synthetic", transaction_id, date)

            transactions.return_value = [last_transaction, first_transaction]
            lookup.reset_mock()
            lookup.side_effect = [first_transaction, last_transaction]
            multiple_lines, multiple_balances = provider._obtain_statement_data(
                since, until
            )
            self.assertEqual(
                lookup.call_args_list,
                [
                    mock.call("synthetic", transaction_id, date),
                    mock.call("synthetic", "fabricated-last", last_date),
                ],
            )
        self.assertEqual(
            balances,
            {
                "balance_start": Decimal("112.75"),
                "balance_end_real": Decimal("120.00"),
            },
        )
        self.assertEqual([line["amount"] for line in lines], ["7.50", "-0.25"])
        self.assertEqual(lines[0]["payment_ref"], transaction_id)
        self.assertNotIn("partner_name", lines[0])
        self.assertEqual(
            [line["amount"] for line in multiple_lines], ["7.50", "-0.25", "20.00"]
        )
        self.assertEqual(
            multiple_balances,
            {
                "balance_start": Decimal("112.75"),
                "balance_end_real": Decimal("140.00"),
            },
        )

    def test_optional_payer_name_preserves_payment_reference_format(self):
        provider = self.OnlineBankStatementProvider.new({"service": "paypal"})
        email = "billing@example.invalid"
        transaction_id = "fabricated-transaction"
        transaction = {
            "transaction_info": {
                "transaction_id": transaction_id,
                "transaction_updated_date": self.today,
                "transaction_amount": {"value": "1.00"},
            },
            "payer_info": {"email_address": email, "payer_name": None},
        }
        line = provider._paypal_transaction_to_lines(transaction)[0]
        self.assertEqual(line["payment_ref"], transaction_id)
        self.assertNotIn("partner_name", line)

        transaction["payer_info"] = {"payer_name": {"email_address": email}}
        line = provider._paypal_transaction_to_lines(transaction)[0]
        self.assertEqual(line["payment_ref"], f"{transaction_id} ({email})")

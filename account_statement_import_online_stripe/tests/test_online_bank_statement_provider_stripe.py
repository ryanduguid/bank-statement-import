import io
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, call, patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse

from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon

from ..models.online_bank_statement_provider_stripe import safe_format


class TestOnlineBankStatementProviderStripe(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Bank",
                "type": "bank",
                "code": "BANK",
                "bank_statements_source": "online",
            }
        )
        cls.provider = cls.env["online.bank.statement.provider"].create(
            {
                "name": "Test Stripe Provider",
                "service": "stripe",
                "password": "test_api_key",
                "journal_id": cls.journal.id,
                "currency_id": cls.env.ref("base.USD").id,
                "stripe_note": "Custom Note {source.object}",
                "stripe_fee_note": "Fee Note {source.object}",
            }
        )

    def test_obtain_statement_data_success(self):
        mock_stripe_data = {
            "data": [
                {
                    "id": "txn_123",
                    "amount": 10000,
                    "currency": "usd",
                    "created": 1678886400,
                    "object": "balance_transaction",
                    "fee": 100,
                    "type": "transfer",
                    "source": {
                        "id": "ch_123",
                        "object": "charge",
                        "metadata": {"invoice_number": "INV-001"},
                        "payment_method_details": {"type": "card"},
                    },
                },
                {
                    "id": "txn_456",
                    "amount": 20000,
                    "currency": "usd",
                    "created": 1678972800,
                    "object": "balance_transaction",
                    "fee": 200,
                    "type": "transfer",
                    "source": {
                        "id": "ch_456",
                        "object": "charge",
                        "metadata": {"invoice_number": "INV-002"},
                        "payment_method_details": {"type": "card"},
                    },
                },
            ],
            "has_more": False,
        }
        with patch(
            "odoo.addons.account_statement_import_online_stripe.models.online_bank_statement_provider_stripe.OnlineBankStatementProviderStripe._stripe_api_get_all",
            return_value=mock_stripe_data["data"],
        ) as mock_get_all:
            date_since = datetime(2023, 3, 15)
            date_until = datetime(2023, 3, 17)
            statement_data, _ = self.provider._obtain_statement_data(
                date_since, date_until
            )
            mock_get_all.assert_called_once()
            self.assertEqual(len(statement_data), 4)
            self.assertEqual(statement_data[0]["amount"], 100.0)
            self.assertEqual(statement_data[0]["unique_import_id"], "txn_123")
            self.assertEqual(statement_data[0]["ref"], "INV-001")
            self.assertEqual(
                statement_data[0]["payment_ref"], "stripe INV-001 charge ch_123 card"
            )
            self.assertEqual(statement_data[0]["narration"], "Custom Note charge")
            self.assertEqual(statement_data[1]["amount"], -1.0)
            self.assertEqual(statement_data[1]["unique_import_id"], "txn_123_fee")
            self.assertEqual(statement_data[1]["ref"], "")
            self.assertEqual(
                statement_data[1]["payment_ref"],
                "stripe fee INV-001 charge ch_123 card",
            )
            self.assertEqual(statement_data[1]["narration"], "Fee Note charge")
            self.assertEqual(statement_data[2]["amount"], 200.0)
            self.assertEqual(statement_data[2]["unique_import_id"], "txn_456")
            self.assertEqual(statement_data[2]["ref"], "INV-002")
            self.assertEqual(
                statement_data[2]["payment_ref"], "stripe INV-002 charge ch_456 card"
            )
            self.assertEqual(statement_data[2]["narration"], "Custom Note charge")
            self.assertEqual(statement_data[3]["amount"], -2.0)
            self.assertEqual(statement_data[3]["unique_import_id"], "txn_456_fee")
            self.assertEqual(statement_data[3]["ref"], "")
            self.assertEqual(
                statement_data[3]["payment_ref"],
                "stripe fee INV-002 charge ch_456 card",
            )
            self.assertEqual(statement_data[3]["narration"], "Fee Note charge")

    def test_pagination_preserves_parameters_and_uses_the_last_result_cursor(self):
        pages = [
            {"data": [{"id": "txn_first"}, {"id": "txn_second"}], "has_more": True},
            {"data": [{"id": "txn_last"}], "has_more": False},
        ]
        for parameters in (None, [("expand[]", "data.source")]):
            with (
                self.subTest(parameters=parameters),
                patch.object(
                    type(self.provider), "_stripe_api_get", side_effect=pages
                ) as request,
            ):
                original = list(parameters or [])
                rows = list(
                    self.provider._stripe_api_get_all(
                        "/balance_transactions", parameters
                    )
                )
                self.assertEqual(
                    [row["id"] for row in rows], ["txn_first", "txn_second", "txn_last"]
                )
                self.assertEqual(
                    request.call_args_list,
                    [
                        call("/balance_transactions", params=original),
                        call(
                            "/balance_transactions",
                            params=[*original, ("starting_after", "txn_second")],
                        ),
                    ],
                )
                self.assertEqual(parameters, None if parameters is None else original)

    def test_transport_encodes_query_authentication_and_response(self):
        document = {
            "data": [{"id": "fabricated", "label": "caf\u00e9"}],
            "has_more": False,
        }
        response = Mock()
        response.read.return_value = json.dumps(document).encode("utf-8")
        for api_base, parameters, data in (
            (False, None, None),
            (
                "https://stripe.invalid/v1",
                [("expand[]", "data.source"), ("limit", "2")],
                b"fixture",
            ),
        ):
            self.provider.api_base = api_base
            with (
                self.subTest(api_base=api_base),
                patch(
                    "odoo.addons.account_statement_import_online_stripe.models.online_bank_statement_provider_stripe.urllib.request.urlopen",
                    return_value=response,
                ) as open_url,
            ):
                self.assertEqual(
                    self.provider._stripe_api_get(
                        "/balance_transactions", parameters, data
                    ),
                    document,
                )
            request = open_url.call_args.args[0]
            parsed = urlparse(request.full_url)
            self.assertEqual(parsed.scheme, "https")
            self.assertEqual(
                parsed.netloc, "stripe.invalid" if api_base else "api.stripe.com"
            )
            self.assertEqual(parsed.path, "/v1/balance_transactions")
            self.assertEqual(
                parse_qs(parsed.query),
                {"expand[]": ["data.source"], "limit": ["2"]} if parameters else {},
            )
            self.assertEqual(request.get_header("Authorization"), "Bearer test_api_key")
            self.assertEqual(request.data, data)

    def test_http_failure_is_a_user_error_with_the_original_cause(self):
        error = HTTPError(
            "https://stripe.invalid/v1/balance_transactions",
            401,
            "fixture refusal",
            {},
            io.BytesIO(b'{"error":{"message":"fabricated request denied"}}'),
        )
        with (
            patch(
                "odoo.addons.account_statement_import_online_stripe.models.online_bank_statement_provider_stripe.urllib.request.urlopen",
                side_effect=error,
            ),
            self.assertRaises(UserError) as raised,
        ):
            self.provider._stripe_api_get("/balance_transactions")
        self.assertIs(raised.exception.__cause__, error)
        self.assertIn("fabricated request denied", str(raised.exception))
        self.assertIn("/balance_transactions", str(raised.exception))

    def test_aware_dates_empty_expansions_and_foreign_currency(self):
        self.provider.stripe_expand = ",data.source,  ,data.source.customer,"
        zone = timezone(timedelta(hours=11))
        since, until = (datetime(2023, 1, day, tzinfo=zone) for day in (1, 2))
        transactions = [
            {
                "id": "txn_own",
                "currency": "usd",
                "amount": 123,
                "created": 1672491600,
                "fee": 0,
            },
            {
                "id": "txn_foreign",
                "currency": "eur",
                "amount": 999,
                "created": 1672491600,
                "fee": 0,
            },
        ]
        with patch.object(
            type(self.provider), "_stripe_api_get_all", return_value=transactions
        ) as request:
            lines, metadata = self.provider._obtain_statement_data(since, until)
        request.assert_called_once_with(
            "/balance_transactions",
            [
                ("created[gte]", int(since.timestamp())),
                ("created[lt]", int(until.timestamp())),
                ("expand[]", "data.source"),
                ("expand[]", "data.source.customer"),
            ],
        )
        self.assertEqual(metadata, {})
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["unique_import_id"], "txn_own")
        self.assertAlmostEqual(lines[0]["amount"], 1.23)

    def test_missing_nested_fields_preserve_the_surrounding_label(self):
        for source in ({}, {"metadata": {}}, "a scalar instead of an object"):
            with self.subTest(source=source):
                self.assertEqual(
                    safe_format(
                        "before {source.metadata.invoice_number} after",
                        {"source": source},
                    ),
                    "before  after",
                )

# Copyright 2022 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
from unittest.mock import MagicMock, patch

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common

from .test_account_statement_import_online_ponto import FOUR_TRANSACTIONS


class TestPontoInterface(common.TransactionCase):
    post_install = True

    @patch("requests.get")
    def test_request_sends_authorization_without_logging_it(self, requests_get):
        interface = self.env["ponto.interface"]
        marker = "synthetic-request-marker"
        access = {
            "access_token": marker,
            "token_expiration": fields.Datetime.now() + relativedelta(minutes=5),
        }
        url = "https://example.invalid/transactions"
        params = {"limit": 25}
        requests_get.return_value = MagicMock(status_code=200, text='{"data": []}')
        with self.assertLogs(
            "odoo.addons.account_statement_import_online_ponto.models.ponto_interface",
            level="DEBUG",
        ) as logs:
            self.assertEqual(interface._get_request(access, url, params), {"data": []})
        requests_get.assert_called_once_with(
            url,
            params=params,
            headers={"Accept": "application/json", "Authorization": f"Bearer {marker}"},
            timeout=(60, 300),
        )
        output = "\n".join(logs.output)
        self.assertIn(url, output)
        self.assertIn(str(params), output)
        self.assertNotIn(marker, output)

    @patch("requests.post")
    def test_login(self, requests_post):
        """Check Ponto API login."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(
            {
                "access_token": "live_the_token",
                "expires_in": 1799,
                "scope": "ai",
                "token_type": "bearer",
            }
        )
        requests_post.return_value = mock_response
        interface_model = self.env["ponto.interface"]
        access_data = interface_model._login("uncle_john", "secret")
        self.assertEqual(access_data["access_token"], "live_the_token")
        self.assertIn("token_expiration", access_data)

    @patch("requests.post")
    def test_login_rejects_missing_credentials_or_token(self, requests_post):
        interface = self.env["ponto.interface"]
        with self.assertRaisesRegex(UserError, "Please fill login and key"):
            interface._login("fixture", "")
        requests_post.assert_not_called()
        requests_post.return_value = MagicMock(status_code=201, text="{}")
        with self.assertRaisesRegex(UserError, "no token"):
            interface._login("fixture", "fixture-key")

    @patch("requests.post")
    def test_expired_access_refreshes_headers_and_cached_token(self, requests_post):
        access = self._get_access_dict()
        access["token_expiration"] = fields.Datetime.now() - relativedelta(seconds=1)
        requests_post.return_value = MagicMock(
            status_code=201,
            text=json.dumps({"access_token": "renewed-fixture", "expires_in": 120}),
        )
        headers = self.env["ponto.interface"]._get_request_headers(access)
        self.assertEqual(headers["Authorization"], "Bearer renewed-fixture")
        self.assertEqual(access["access_token"], "renewed-fixture")
        self.assertGreater(access["token_expiration"], fields.Datetime.now())
        requests_post.assert_called_once()

    @patch("requests.get")
    def test_set_access_account(self, requests_get):
        """Test getting account data for Ponto access."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps(
            {
                "data": [
                    {
                        "id": "wrong_id",
                        "attributes": {
                            "reference": "NL66ABNA123456789",
                        },
                    },
                    {
                        "id": "2ad3df83-be01-47cf-a6be-cf0de5cb4c99",
                        "attributes": {
                            "reference": "NL66RABO123456789",
                        },
                    },
                ],
            }
        )
        requests_get.return_value = mock_response
        # Start of actual test.
        access_data = self._get_access_dict(include_account=False)
        interface_model = self.env["ponto.interface"]
        interface_model._set_access_account(access_data, "NL66RABO123456789")
        self.assertIn("ponto_account", access_data)
        self.assertEqual(
            access_data["ponto_account"], "2ad3df83-be01-47cf-a6be-cf0de5cb4c99"
        )

    @patch("requests.get")
    def test_set_access_account_distinguishes_empty_and_unmatched_accounts(
        self, requests_get
    ):
        interface = self.env["ponto.interface"]
        access = self._get_access_dict(include_account=False)
        for accounts, message in (
            ([], "No accounts found"),
            ([{"attributes": {"reference": "NL66ABNA123456789"}}], "not found"),
        ):
            with self.subTest(accounts=accounts):
                requests_get.return_value = MagicMock(
                    status_code=200, text=json.dumps({"data": accounts})
                )
                with self.assertRaisesRegex(UserError, message):
                    interface._set_access_account(access, "NL66RABO123456789")
                self.assertNotIn("ponto_account", access)

    @patch("requests.get")
    def test_get_transactions(self, requests_get):
        """Test getting transactions from Ponto."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Key "data" will contain a list of transactions.
        mock_response.text = json.dumps({"data": FOUR_TRANSACTIONS})
        requests_get.return_value = mock_response
        # Start of actual test.
        access_data = self._get_access_dict()
        interface_model = self.env["ponto.interface"]
        transactions = interface_model._get_transactions(access_data, False)
        self.assertEqual(len(transactions), 4)
        self.assertEqual(transactions[3]["id"], "b21a6c65-1c52-4ba6-8cbc-127d2b2d85ff")
        self.assertEqual(
            transactions[3]["attributes"]["counterpartReference"], "BE10325927501996"
        )

    @patch("requests.get")
    def test_get_transactions_uses_cursor_and_distinguishes_http_failure(
        self, requests_get
    ):
        interface = self.env["ponto.interface"]
        access = self._get_access_dict()
        requests_get.return_value = MagicMock(status_code=200, text='{"data": []}')
        self.assertEqual(interface._get_transactions(access, "cursor-fixture"), [])
        self.assertEqual(
            requests_get.call_args.kwargs["params"],
            {"limit": 100, "after": "cursor-fixture"},
        )
        requests_get.return_value = MagicMock(status_code=429, text="try again later")
        with self.assertRaisesRegex(UserError, "429: try again later"):
            interface._get_transactions(access, "cursor-fixture")

    def _get_access_dict(self, include_account=True):
        """Get access dict that caches login/account information."""
        token_expiration = fields.Datetime.now() + relativedelta(seconds=1800)
        access_data = {
            "username": "uncle_john",
            "password": "secret",
            "access_token": "live_the_token",
            "token_expiration": token_expiration,
        }
        if include_account:
            access_data["ponto_account"] = "2ad3df83-be01-47cf-a6be-cf0de5cb4c99"
        return access_data

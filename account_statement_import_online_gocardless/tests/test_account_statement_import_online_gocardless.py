# Copyright 2023 Tecnativa - Pedro M.Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
from unittest import mock

import requests
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common
from odoo.tools import mute_logger

_module_ns = "odoo.addons.account_statement_import_online_gocardless"
_provider_class = (
    _module_ns + ".models.online_bank_statement_provider.OnlineBankStatementProvider"
)


class TestAccountBankAccountStatementImportOnlineGocardless(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.now = fields.Datetime.now()
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.currency_eur.write({"active": True})
        bank_account = cls.env["res.partner.bank"].create(
            {
                "acc_number": "NL77ABNA0574908765",
                "partner_id": cls.env.ref("base.main_partner").id,
                "company_id": cls.env.ref("base.main_company").id,
                "bank_id": cls.env.ref("base.res_bank_1").id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "GoCardless Bank Test",
                "type": "bank",
                "code": "GCB",
                "currency_id": cls.currency_eur.id,
                "bank_statements_source": "online",
                "online_bank_statement_provider": "gocardless",
                "bank_account_id": bank_account.id,
            }
        )
        cls.provider = cls.journal.online_bank_statement_provider_id
        cls.provider.write(
            {
                "statement_creation_mode": "monthly",
                "gocardless_account_id": "SANDBOXFINANCE_SFIN0000",
                "gocardless_requisition_expiration": cls.now + relativedelta(days=30),
            }
        )
        cls.return_value = {  # GoCardless sample return
            "transactions": {
                "booked": [
                    {
                        "transactionId": "2020103000624289-1",
                        "debtorName": "MON MOTHMA",
                        "debtorAccount": {"iban": "GL53SAFI055151515"},
                        "transactionAmount": {"currency": "EUR", "amount": "45.00"},
                        "bookingDate": "2020-10-30",
                        "valueDate": "2020-10-30",
                        "remittanceInformationUnstructured": (
                            "For the support of Restoration of the Republic foundation"
                        ),
                    },
                    {
                        "transactionId": "2020111101899195-1",
                        "transactionAmount": {"currency": "EUR", "amount": "-15.00"},
                        "bankTransactionCode": "PMNT",
                        "bookingDate": "2020-11-11",
                        "valueDate": "2020-11-11",
                        "remittanceInformationUnstructured": "PAYMENT Alderaan Coffe",
                    },
                ],
                "pending": [
                    {
                        "transactionAmount": {"currency": "EUR", "amount": "-10.00"},
                        "valueDate": "2020-11-03",
                        "remittanceInformationUnstructured": (
                            "Reserved PAYMENT Emperor's Burgers"
                        ),
                    }
                ],
            }
        }
        cls.mock_transaction = lambda cls: mock.patch(
            _provider_class + "._gocardless_request_transactions",
            return_value=cls.return_value,
        )
        cls.request_requisition_value = {
            "accounts": ["ACCOUNT-ID-1"],
            "agreement": "TEST-AGREEMENT-ID",
        }
        cls.mock_requisition = lambda cls: mock.patch(
            _provider_class + "._gocardless_request_requisition",
            return_value=cls.request_requisition_value,
        )
        cls.request_account_value = {
            "id": "ACCOUNT-ID-1",
            "iban": "nl77abna0574908765",
        }
        cls.mock_account = lambda cls: mock.patch(
            _provider_class + "._gocardless_request_account",
            return_value=cls.request_account_value,
        )
        cls.request_agreement_value = {
            "id": "TEST-AGREEMENT-ID",
            "accepted": cls.now.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "access_valid_for_days": 30,
        }
        cls.mock_agreement = lambda cls: mock.patch(
            _provider_class + "._gocardless_request_agreement",
            return_value=cls.request_agreement_value,
        )

    def test_mocked_gocardless(self):
        vals = {
            "date_since": "2020-10-30",
            "date_until": "2020-11-11",
        }
        wizard = (
            self.env["online.bank.statement.pull.wizard"]
            .with_context(
                active_model="account.journal",
                active_id=self.journal.id,
            )
            .create(vals)
        )
        with self.mock_transaction():
            wizard.action_pull()
        statements = self.env["account.bank.statement"].search(
            [("journal_id", "=", self.journal.id)]
        )
        self.assertEqual(len(statements), 2)
        lines = statements.line_ids.sorted(lambda x: x.date)
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines.mapped("amount"), [45.0, -15.0])

    def test_manual_pull_normalises_references_accounts_and_duplicate_ids(self):
        self.provider.tz = "UTC"
        own_account = self.journal.bank_account_id.sanitized_acc_number
        supplier_account = "NL91ABNA0417164300"

        def booked(identifier, amount, **details):
            return {
                "transactionId": identifier,
                "bookingDate": "2020-10-30",
                "valueDate": "2020-10-30",
                "transactionAmount": {"currency": "EUR", "amount": amount},
                **details,
            }

        payload = {
            "transactions": {
                "booked": [
                    booked(
                        "fixture-array",
                        "25.00",
                        debtorName="Fixture Customer",
                        debtorAccount={"iban": own_account},
                        remittanceInformationUnstructuredArray=["Invoice", "A-101"],
                    ),
                    booked(
                        "fixture-supplier",
                        "-10.00",
                        creditorName="Fixture Supplier",
                        creditorAccount={"iban": supplier_account},
                    ),
                    booked(
                        "fixture-empty",
                        "5.00",
                        debtorName="Fixture Donor",
                        remittanceInformationUnstructured="",
                    ),
                ],
                "pending": [],
            }
        }
        wizard = (
            self.env["online.bank.statement.pull.wizard"]
            .with_context(active_model="account.journal", active_id=self.journal.id)
            .create({"date_since": "2020-10-01", "date_until": "2020-10-31"})
        )
        with mock.patch(
            _provider_class + "._gocardless_request_transactions", return_value=payload
        ) as request:
            wizard.action_pull()
            statements = self.env["account.bank.statement"].search(
                [("journal_id", "=", self.journal.id)]
            )
            self.assertEqual(len(statements), 1)
            lines = statements.line_ids
            self.assertEqual(len(lines), 3)
            self.assertEqual(sum(lines.mapped("amount")), 20)
            for identifier, reference, amount, account in [
                ("fixture-array", "Invoice A-101", 25, False),
                ("fixture-supplier", "Fixture Supplier", -10, supplier_account),
                ("fixture-empty", "Fixture Donor", 5, False),
            ]:
                line = lines.filtered(
                    lambda item, identifier=identifier: item.unique_import_id
                    == f"{own_account}-{self.journal.id}-{identifier}"
                )
                self.assertEqual(len(line), 1)
                self.assertEqual(line.payment_ref, reference)
                self.assertEqual(line.amount, amount)
                self.assertEqual(line.account_number, account)
                self.assertEqual(line.date, fields.Date.from_string("2020-10-30"))
            wizard.action_pull()
            self.assertEqual(request.call_count, 2)
        self.assertEqual(
            self.env["account.bank.statement"].search(
                [("journal_id", "=", self.journal.id)]
            ),
            statements,
        )
        self.assertEqual(statements.line_ids, lines)

    def test_provider_gocardless_finish_requisition(self):
        with self.mock_requisition(), self.mock_account(), self.mock_agreement():
            res = self.provider._gocardless_finish_requisition(dry=True)
            self.assertTrue(res, "Bank account not found!")

    def _http_transaction_response(self, status):
        response = requests.Response()
        response.status_code = status
        response.url = (
            "https://bankaccountdata.gocardless.com/api/v2/accounts/"
            f"{self.provider.gocardless_account_id}/transactions/"
        )
        payload = (
            {"transactions": {"booked": []}}
            if status == 200
            else {"detail": "fabricated refusal"}
        )
        response._content = json.dumps(payload).encode()
        return response

    def test_transaction_http_errors_keep_the_scheduled_checkpoint(self):
        since = fields.Datetime.to_datetime("2020-10-01 00:00:00")
        until = fields.Datetime.to_datetime("2020-11-01 00:00:00")
        for status in (200, 401, 500):
            with self.subTest(status=status):
                self.provider.write(
                    {
                        "tz": "UTC",
                        "last_successful_run": since,
                        "next_run": until,
                        "gocardless_token": "fabricated-access-token",
                        "gocardless_token_expiration": self.now + relativedelta(days=1),
                    }
                )
                response = self._http_transaction_response(status)
                with (
                    mock.patch(
                        _module_ns
                        + ".models.online_bank_statement_provider.requests.get",
                        return_value=response,
                    ) as request,
                    mute_logger(
                        "odoo.addons.account_statement_import_online.models.online_bank_statement_provider"
                    ),
                ):
                    self.provider.with_context(scheduled=True)._pull(since, until)
                self.assertEqual(
                    self.provider.last_successful_run, until if status == 200 else since
                )
                self.assertGreater(self.provider.next_run, until)
                request.assert_called_once()
                self.assertFalse(
                    self.env["account.bank.statement"].search(
                        [("journal_id", "=", self.journal.id)]
                    )
                )

    def test_transaction_http_errors_reach_manual_pull(self):
        since = fields.Datetime.to_datetime("2020-10-01 00:00:00")
        until = fields.Datetime.to_datetime("2020-11-01 00:00:00")
        self.provider.write(
            {
                "tz": "UTC",
                "gocardless_token": "fabricated-access-token",
                "gocardless_token_expiration": self.now + relativedelta(days=1),
            }
        )
        for status in (401, 500):
            with self.subTest(status=status):
                response = self._http_transaction_response(status)
                with (
                    mock.patch(
                        _module_ns
                        + ".models.online_bank_statement_provider.requests.get",
                        return_value=response,
                    ),
                    self.assertRaises(requests.HTTPError) as raised,
                ):
                    self.provider._pull(since, until)
                self.assertIs(raised.exception.response, response)

    @staticmethod
    def _json_response(status, payload, endpoint):
        response = requests.Response()
        response.status_code = status
        response.url = "https://bankaccountdata.gocardless.com/api/v2/" + endpoint + "/"
        response._content = json.dumps(payload).encode()
        return response

    def test_new_token_is_cached_with_its_refresh_expiration(self):
        self.provider.write({"username": "fabricated-id", "password": "fabricated-key"})
        payload = {
            "access": "fabricated-access",
            "access_expires": 3600,
            "refresh": "fabricated-refresh",
            "refresh_expires": 7200,
        }
        response = self._json_response(201, payload, "token/new")
        before = fields.Datetime.now()
        with mock.patch(
            _module_ns + ".models.online_bank_statement_provider.requests.post",
            return_value=response,
        ) as request:
            self.assertEqual(self.provider._gocardless_get_token(), payload["access"])
            self.assertEqual(self.provider._gocardless_get_token(), payload["access"])
        after = fields.Datetime.now()
        request.assert_called_once()
        args, kwargs = request.call_args
        self.assertEqual(args, (response.url,))
        self.assertEqual(
            json.loads(kwargs["data"]),
            {"secret_id": "fabricated-id", "secret_key": "fabricated-key"},
        )
        self.assertEqual(kwargs["timeout"], 60)
        self.assertEqual(
            kwargs["headers"],
            {"accept": "application/json", "Content-Type": "application/json"},
        )
        self.assertEqual(self.provider.gocardless_refresh_token, payload["refresh"])
        for field, seconds in (
            ("gocardless_token_expiration", 3600),
            ("gocardless_refresh_expiration", 7200),
        ):
            self.assertGreaterEqual(
                self.provider[field], before + relativedelta(seconds=seconds)
            )
            self.assertLessEqual(
                self.provider[field], after + relativedelta(seconds=seconds)
            )

    def test_expired_access_refreshes_without_overwriting_an_unrotated_refresh(self):
        refresh_expiration = self.now + relativedelta(days=1)
        self.provider.write(
            {
                "gocardless_token": "fabricated-expired-access",
                "gocardless_token_expiration": self.now - relativedelta(days=1),
                "gocardless_refresh_token": "fabricated-refresh",
                "gocardless_refresh_expiration": refresh_expiration,
            }
        )
        payload = {"access": "fabricated-renewed-access", "access_expires": 3600}
        response = self._json_response(200, payload, "token/refresh")
        before = fields.Datetime.now()
        with mock.patch(
            _module_ns + ".models.online_bank_statement_provider.requests.post",
            return_value=response,
        ) as request:
            self.assertEqual(self.provider._gocardless_get_token(), payload["access"])
        request.assert_called_once()
        args, kwargs = request.call_args
        self.assertEqual(args, (response.url,))
        self.assertEqual(json.loads(kwargs["data"]), {"refresh": "fabricated-refresh"})
        self.assertNotIn("Authorization", kwargs["headers"])
        self.assertEqual(kwargs["timeout"], 60)
        self.assertEqual(self.provider.gocardless_refresh_token, "fabricated-refresh")
        self.assertEqual(
            self.provider.gocardless_refresh_expiration, refresh_expiration
        )
        self.assertGreaterEqual(
            self.provider.gocardless_token_expiration,
            before + relativedelta(seconds=3600),
        )
        self.assertLessEqual(
            self.provider.gocardless_token_expiration,
            fields.Datetime.now() + relativedelta(seconds=3600),
        )

    def test_expired_refresh_requests_a_new_token_pair(self):
        expired = self.now - relativedelta(days=1)
        self.provider.write(
            {
                "username": "fabricated-id",
                "password": "fabricated-key",
                "gocardless_token": "fabricated-expired-access",
                "gocardless_token_expiration": expired,
                "gocardless_refresh_token": "fabricated-expired-refresh",
                "gocardless_refresh_expiration": expired,
            }
        )
        payload = {
            "access": "fabricated-new-access",
            "access_expires": 3600,
            "refresh": "fabricated-new-refresh",
            "refresh_expires": 7200,
        }
        response = self._json_response(201, payload, "token/new")
        with mock.patch(
            _module_ns + ".models.online_bank_statement_provider.requests.post",
            return_value=response,
        ) as request:
            self.assertEqual(self.provider._gocardless_get_token(), payload["access"])
        request.assert_called_once()
        args, kwargs = request.call_args
        self.assertEqual(args, (response.url,))
        self.assertEqual(
            json.loads(kwargs["data"]),
            {"secret_id": "fabricated-id", "secret_key": "fabricated-key"},
        )
        self.assertEqual(self.provider.gocardless_refresh_token, payload["refresh"])
        self.assertGreater(self.provider.gocardless_refresh_expiration, self.now)

    def test_institution_refusals_keep_their_user_facing_reason(self):
        self.provider.write(
            {
                "gocardless_token": "fabricated-access",
                "gocardless_token_expiration": self.now + relativedelta(days=1),
                "gocardless_country_id": self.env.ref("base.nl").id,
            }
        )
        for status, reason in (
            (400, "Incorrect country code or country not supported."),
            (429, "fabricated rate limit"),
        ):
            with self.subTest(status=status):
                response = self._json_response(
                    status, {"detail": reason}, "institutions"
                )
                with (
                    mock.patch(
                        _module_ns
                        + ".models.online_bank_statement_provider.requests.get",
                        return_value=response,
                    ) as request,
                    self.assertRaises(UserError) as raised,
                ):
                    self.provider._gocardless_select_bank_institution()
                self.assertEqual(str(raised.exception), reason)
                request.assert_called_once()
                args, kwargs = request.call_args
                self.assertEqual(args, (response.url,))
                self.assertEqual(kwargs["params"], {"country": "NL"})
                self.assertEqual(
                    kwargs["headers"]["Authorization"], "Bearer fabricated-access"
                )
                self.assertEqual(kwargs["timeout"], 60)

    def test_institution_dialog_retains_the_selected_country_and_bank_data(self):
        self.provider.write(
            {
                "gocardless_token": "fabricated-access",
                "gocardless_token_expiration": self.now + relativedelta(days=1),
                "gocardless_country_id": self.env.ref("base.nl").id,
            }
        )
        institutions = [
            {"id": "fabricated-bank", "name": "Fabricated Bank", "countries": ["NL"]}
        ]
        response = self._json_response(200, institutions, "institutions")
        with mock.patch(
            _module_ns + ".models.online_bank_statement_provider.requests.get",
            return_value=response,
        ):
            action = self.provider._gocardless_select_bank_institution()
        self.assertEqual(action["tag"], "online_sync_institution_selector_gocardless")
        self.assertEqual(action["target"], "new")
        self.assertEqual(action["context"]["institutions"], institutions)
        self.assertEqual(action["context"]["country"], "NL")
        self.assertEqual(action["context"]["provider_id"], self.provider.id)
        self.assertEqual(
            action["context"]["country_names"],
            [{"code": "NL", "name": self.env.ref("base.nl").name}],
        )

    def test_transaction_request_caps_a_future_end_at_today(self):
        self.provider.write(
            {
                "gocardless_token": "fabricated-access",
                "gocardless_token_expiration": self.now + relativedelta(days=1),
            }
        )
        since = fields.Datetime.now() - relativedelta(days=2)
        until = fields.Datetime.now() + relativedelta(days=2)
        payload = {"transactions": {"booked": []}}
        response = self._http_transaction_response(200)
        before = fields.Date.today()
        with mock.patch(
            _module_ns + ".models.online_bank_statement_provider.requests.get",
            return_value=response,
        ) as request:
            self.assertEqual(
                self.provider._gocardless_request_transactions(since, until), payload
            )
        after = fields.Date.today()
        request.assert_called_once()
        params = request.call_args.kwargs["params"]
        self.assertEqual(params["date_from"], since.strftime("%Y-%m-%d"))
        self.assertIn(params["date_to"], {before.isoformat(), after.isoformat()})
        self.assertNotEqual(params["date_to"], until.strftime("%Y-%m-%d"))

    def test_expired_consent_keeps_the_scheduled_checkpoint(self):
        since = fields.Datetime.to_datetime("2020-10-01 00:00:00")
        until = fields.Datetime.to_datetime("2020-11-01 00:00:00")
        self.provider.write(
            {
                "tz": "UTC",
                "last_successful_run": since,
                "next_run": until,
                "gocardless_requisition_expiration": self.now - relativedelta(days=1),
            }
        )
        with (
            mock.patch(
                _module_ns + ".models.online_bank_statement_provider.requests.get"
            ) as request,
            mute_logger(
                "odoo.addons.account_statement_import_online.models.online_bank_statement_provider"
            ),
        ):
            self.provider.with_context(scheduled=True)._pull(since, until)
        request.assert_not_called()
        self.assertEqual(self.provider.last_successful_run, since)
        self.assertGreater(self.provider.next_run, until)
        self.assertFalse(
            self.env["account.bank.statement"].search(
                [("journal_id", "=", self.journal.id)]
            )
        )
        self.assertTrue(
            any(
                "renew the authorization" in (message.body or "")
                for message in self.provider.message_ids
            )
        )

    def test_expired_consent_reaches_the_manual_pull_as_a_user_error(self):
        self.provider.gocardless_requisition_expiration = self.now - relativedelta(
            days=1
        )
        with (
            mock.patch(
                _module_ns + ".models.online_bank_statement_provider.requests.get"
            ) as request,
            self.assertRaises(UserError) as raised,
        ):
            self.provider._pull(
                fields.Datetime.to_datetime("2020-10-01 00:00:00"),
                fields.Datetime.to_datetime("2020-11-01 00:00:00"),
            )
        request.assert_not_called()
        self.assertIn("renew the authorization", str(raised.exception))

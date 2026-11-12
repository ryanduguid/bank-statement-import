# Copyright 2026 Ryan Duguid
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import requests
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import HttpCase, tagged

_REQUESTS = (
    "odoo.addons.account_statement_import_online_gocardless.models."
    "online_bank_statement_provider.requests"
)
_API = "https://bankaccountdata.gocardless.com/api/v2/"


@tagged("post_install", "-at_install")
class TestGocardlessConnection(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.accepted = fields.Datetime.now()
        currency = cls.env.ref("base.EUR")
        currency.active = True
        bank = cls.env["res.bank"].create(
            {"name": "Callback fixture bank", "country": cls.env.ref("base.nl").id}
        )
        providers = []
        for code, iban in (
            ("GC1", "NL77ABNA0574908765"),
            ("GC2", "NL91ABNA0417164300"),
        ):
            account = cls.env["res.partner.bank"].create(
                {
                    "acc_number": iban,
                    "partner_id": cls.env.company.partner_id.id,
                    "company_id": cls.env.company.id,
                    "bank_id": bank.id,
                }
            )
            journal = cls.env["account.journal"].create(
                {
                    "name": f"Callback fixture {code}",
                    "type": "bank",
                    "code": code,
                    "currency_id": currency.id,
                    "bank_statements_source": "online",
                    "online_bank_statement_provider": "gocardless",
                    "bank_account_id": account.id,
                }
            )
            provider = journal.online_bank_statement_provider_id
            provider.write(
                {
                    "gocardless_token": "fabricated-callback-access",
                    "gocardless_token_expiration": cls.accepted + relativedelta(days=1),
                }
            )
            providers.append(provider)
        cls.donor, cls.recipient = providers
        cls.donor.write(
            {
                "gocardless_requisition_ref": "fabricated-callback-reference",
                "gocardless_requisition_id": "fabricated-requisition",
                "gocardless_requisition_expiration": cls.accepted
                + relativedelta(days=1),
                "gocardless_institution_id": "fabricated-institution",
            }
        )

    def setUp(self):
        super().setUp()
        donor_iban = self.donor.journal_id.bank_account_id.sanitized_acc_number
        recipient_iban = self.recipient.journal_id.bank_account_id.sanitized_acc_number
        self.api_payloads = {
            "requisitions/fabricated-requisition/": {
                "accounts": ["fabricated-account-one", "fabricated-account-two"],
                "agreement": "fabricated-agreement",
            },
            "accounts/fabricated-account-one/": {
                "id": "fabricated-account-one",
                "iban": donor_iban.lower(),
            },
            "accounts/fabricated-account-two/": {
                "id": "fabricated-account-two",
                "iban": recipient_iban,
            },
            "agreements/enduser/fabricated-agreement/": {
                "accepted": self.accepted.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "access_valid_for_days": 90,
            },
        }

    def _get_response(self, url, **kwargs):
        self.assertTrue(url.startswith(_API), url)
        self.assertEqual(kwargs["timeout"], 60)
        self.assertEqual(
            kwargs["headers"]["Authorization"], "Bearer fabricated-callback-access"
        )
        response = requests.Response()
        response.status_code = 200
        response.url = url
        response._content = json.dumps(
            self.api_payloads[url.removeprefix(_API)]
        ).encode()
        return response

    def _callback(self, reference, view_type, provider=None):
        response = self.url_open(
            f"/gocardless/response?ref={reference}", allow_redirects=False
        )
        self.assertEqual(response.status_code, 303)
        location = urlsplit(response.headers["Location"])
        self.assertEqual(location.path, "/web")
        parameters = parse_qs(location.fragment)
        action = self.env.ref(
            "account_statement_import_online.online_bank_statement_provider_action"
        )
        self.assertEqual(parameters["action"], [str(action.id)])
        self.assertEqual(parameters["model"], ["online.bank.statement.provider"])
        self.assertEqual(parameters["view_type"], [view_type])
        if provider:
            self.assertEqual(parameters["id"], [str(provider.id)])
        else:
            self.assertNotIn("id", parameters)

    def test_unknown_callback_returns_the_provider_list_without_api_requests(self):
        with patch(_REQUESTS + ".get") as get:
            self._callback("fabricated-unknown-reference", "list")
            get.assert_not_called()

    def test_single_callback_binds_the_journal_account_and_returns_its_form(self):
        messages = self.donor.message_ids
        with patch(_REQUESTS + ".get", side_effect=self._get_response):
            self._callback(self.donor.gocardless_requisition_ref, "form", self.donor)
        self.assertEqual(self.donor.gocardless_account_id, "fabricated-account-one")
        self.assertEqual(
            self.donor.gocardless_requisition_expiration,
            self.accepted + relativedelta(days=90),
        )
        added = self.donor.message_ids - messages
        self.assertEqual(len(added), 1)
        self.assertIn("is successfully attached", str(added.body))
        self.assertFalse(self.recipient.gocardless_account_id)

    def test_callback_after_reuse_binds_both_journals_and_returns_the_list(self):
        with patch(_REQUESTS + ".get", side_effect=self._get_response):
            action = self.recipient.action_select_gocardless_bank()
            self.assertEqual(
                action["res_model"], "online.bank.statement.provider.existing"
            )
            wizard = self.env[action["res_model"]].browse(action["res_id"])
            self.assertEqual(wizard.provider_id, self.recipient)
            self.assertEqual(wizard.other_provider_id, self.donor)
            wizard.link_existing()
            reference = self.donor.gocardless_requisition_ref
            self.assertEqual(self.recipient.gocardless_requisition_ref, reference)
            self.assertEqual(
                self.recipient.gocardless_account_id, "fabricated-account-two"
            )
            (self.donor | self.recipient).write(
                {
                    "gocardless_account_id": "fabricated-stale-account",
                    "gocardless_requisition_expiration": self.accepted
                    + relativedelta(days=2),
                }
            )
            messages = {
                provider.id: provider.message_ids
                for provider in self.donor | self.recipient
            }
            self._callback(reference, "list")
        for provider, account_id in (
            (self.donor, "fabricated-account-one"),
            (self.recipient, "fabricated-account-two"),
        ):
            self.assertEqual(provider.gocardless_account_id, account_id)
            self.assertEqual(
                provider.gocardless_requisition_id, "fabricated-requisition"
            )
            self.assertEqual(provider.gocardless_requisition_ref, reference)
            self.assertEqual(
                provider.gocardless_requisition_expiration,
                self.accepted + relativedelta(days=90),
            )
            added = provider.message_ids - messages[provider.id]
            self.assertEqual(len(added), 1)
            self.assertIn("is successfully attached", str(added.body))

    def test_unmatched_callback_resets_the_requisition_and_records_the_reason(self):
        for key in (
            "accounts/fabricated-account-one/",
            "accounts/fabricated-account-two/",
        ):
            self.api_payloads[key]["iban"] = "GB82WEST12345698765432"
        messages = self.donor.message_ids
        with patch(_REQUESTS + ".get", side_effect=self._get_response):
            self._callback(self.donor.gocardless_requisition_ref, "form", self.donor)
        self.assertFalse(self.donor.gocardless_requisition_ref)
        self.assertFalse(self.donor.gocardless_requisition_id)
        self.assertFalse(self.donor.gocardless_requisition_expiration)
        added = self.donor.message_ids - messages
        self.assertEqual(len(added), 1)
        self.assertIn("account numbers found", str(added.body))
        self.assertIn("GB82WEST12345698765432", str(added.body))

    def test_agreement_creation_sends_the_persisted_reference_and_callback(self):
        old_reference = self.donor.gocardless_requisition_ref
        response = requests.Response()
        response.status_code = 201
        response._content = json.dumps(
            {
                "id": "fabricated-new-requisition",
                "link": "https://fabricated.invalid/consent",
            }
        ).encode()
        with patch(_REQUESTS + ".post", return_value=response) as post:
            self.assertEqual(
                self.donor.action_check_gocardless_agreement(),
                "https://fabricated.invalid/consent",
            )
            post.assert_called_once()
            self.assertEqual(post.call_args.args, (_API + "requisitions/",))
            self.assertEqual(
                json.loads(post.call_args.kwargs["data"]),
                {
                    "redirect": self.base_url() + "/gocardless/response",
                    "institution_id": "fabricated-institution",
                    "reference": self.donor.gocardless_requisition_ref,
                },
            )
            self.assertNotEqual(self.donor.gocardless_requisition_ref, old_reference)
            self.assertEqual(
                self.donor.gocardless_requisition_id, "fabricated-new-requisition"
            )
            response.status_code = 400
            response._content = b'{"detail": "fabricated refusal"}'
            self.assertIsNone(self.donor.action_check_gocardless_agreement())

    def _assert_bank_selection_navigation(
        self, status, institution="fabricated-ui-institution"
    ):
        redirect = "https://fabricated.invalid/consent"
        self.donor.write(
            {
                "username": "fabricated-ui-client",
                "password": "fabricated-ui-secret",
                "gocardless_country_id": self.env.ref("base.nl").id,
            }
        )
        self.api_payloads["institutions/"] = [
            {
                "id": institution,
                "name": "Fabricated UI Bank",
                "countries": ["NL"],
                "logo": (
                    "data:image/gif;base64,"
                    "R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="
                ),
            }
        ]
        response = requests.Response()
        response.status_code = status
        response._content = json.dumps(
            {"id": "fabricated-ui-requisition", "link": redirect}
            if status == 201
            else {"detail": "fabricated refusal"}
        ).encode()
        previous_reference = self.donor.gocardless_requisition_ref
        recipient_fields = [
            "gocardless_institution_id",
            "gocardless_requisition_ref",
            "gocardless_requisition_id",
        ]
        recipient_before = self.recipient.read(recipient_fields)
        donor_before = self.donor.read(recipient_fields)
        action = self.env.ref(
            "account_statement_import_online.online_bank_statement_provider_action"
        )
        real_get = requests.get

        def get_response(url, **kwargs):
            if url.startswith(_API):
                return self._get_response(url, **kwargs)
            return real_get(url, **kwargs)

        with (
            patch(_REQUESTS + ".get", side_effect=get_response) as get,
            patch(_REQUESTS + ".post", return_value=response) as post,
        ):
            self.browser_js(
                f"/odoo/action-{action.id}/{self.donor.id}",
                "const expectedRedirects = "
                f"{json.dumps([redirect] if status == 201 and institution else [])};\n"
                f"const expectedInstitution = {json.dumps(institution)};\n"
                + r"""
(async () => {
    const {registry} = odoo.loader.modules.get("@web/core/registry");
    const {browser} = odoo.loader.modules.get("@web/core/browser/browser");
    const actions = registry.category("actions");
    const tag = "online_sync_institution_selector_gocardless";
    const originalAction = actions.get(tag);
    const locationDescriptor = Object.getOwnPropertyDescriptor(browser, "location");
    const redirects = [];
    const callbackIds = [];
    let resolve, reject;
    const completed = new Promise((accept, refuse) => {
        resolve = accept; reject = refuse;
    });
    Object.defineProperty(browser, "location", {
        configurable: true,
        value: {...browser.location, replace: (url) => redirects.push(url)},
    });
    actions.add(tag, async (env, action) => {
        const dialog = env.services.dialog;
        const originalAdd = dialog.add;
        dialog.add = (Component, props, ...options) => originalAdd.call(
            dialog, Component, {
            ...props,
            onClickInstitution: async (...args) => {
                callbackIds.push(args[0]);
                try { await props.onClickInstitution(...args); resolve(); }
                catch (error) { reject(error); throw error; }
            },
            }, ...options);
        try { return await originalAction(env, action); }
        finally { dialog.add = originalAdd; }
    }, {force: true});
    try {
        document.querySelector(
            ".o_form_view button[name='action_select_gocardless_bank']"
        ).click();
        const deadline = performance.now() + 5000;
        let selected;
        while (!(selected = document.querySelector(
            ".institution-container .list-institution a"
        ))) {
            if (performance.now() >= deadline) {
                throw new Error("real institution dialog did not mount");
            }
            await new Promise((accept) => setTimeout(accept, 10));
        }
        if (!selected.textContent.includes("Fabricated UI Bank")) {
            throw new Error("wrong institution card");
        }
        selected.click();
        await completed;
        if (JSON.stringify(callbackIds) !== JSON.stringify([expectedInstitution])) {
            throw new Error(
                "original callback did not receive exactly the rendered institution ID"
            );
        }
        if (JSON.stringify(redirects) !== JSON.stringify(expectedRedirects)) {
            throw new Error(
                "completed consent navigation mismatch: " + JSON.stringify(redirects)
            );
        }
        if (!selected.isConnected) {
            throw new Error("selection dialog was unexpectedly removed");
        }
    } finally {
        actions.add(tag, originalAction, {force: true});
        Object.defineProperty(browser, "location", locationDescriptor);
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
                ready=(
                    "document.querySelector("
                    "\".o_form_view button[name='action_select_gocardless_bank']\""
                    ") !== null"
                ),
                login="admin",
                timeout=90,
            )
        provider_calls = [
            call for call in get.call_args_list if call.args[0].startswith(_API)
        ]
        self.assertEqual(len(provider_calls), 1)
        self.assertEqual(provider_calls[0].args, (_API + "institutions/",))
        self.assertEqual(provider_calls[0].kwargs["params"], {"country": "NL"})
        self.recipient.invalidate_recordset()
        self.assertEqual(self.recipient.read(recipient_fields), recipient_before)
        self.donor.invalidate_recordset()
        if not institution:
            post.assert_not_called()
            self.assertEqual(self.donor.read(recipient_fields), donor_before)
            return
        post.assert_called_once()
        self.assertEqual(post.call_args.args, (_API + "requisitions/",))
        self.assertEqual(self.donor.gocardless_institution_id, institution)
        self.assertNotEqual(self.donor.gocardless_requisition_ref, previous_reference)
        self.assertEqual(
            json.loads(post.call_args.kwargs["data"]),
            {
                "redirect": self.base_url() + "/gocardless/response",
                "institution_id": institution,
                "reference": self.donor.gocardless_requisition_ref,
            },
        )
        if status == 201:
            self.assertEqual(
                self.donor.gocardless_requisition_id, "fabricated-ui-requisition"
            )
        else:
            self.assertEqual(
                self.donor.gocardless_requisition_id, "fabricated-requisition"
            )

    def test_refused_bank_consent_keeps_the_mounted_selection_dialog(self):
        self._assert_bank_selection_navigation(400)

    def test_accepted_bank_consent_navigates_to_the_returned_link(self):
        self._assert_bank_selection_navigation(201)

    def test_empty_institution_id_keeps_the_dialog_and_saved_selection(self):
        self._assert_bank_selection_navigation(201, institution="")

    def test_connection_without_a_journal_bank_account_is_refused(self):
        with (
            self.assertRaisesRegex(UserError, "configure bank account"),
            self.env.cr.savepoint(),
        ):
            self.donor.journal_id.bank_account_id = False
            self.donor.action_select_gocardless_bank()

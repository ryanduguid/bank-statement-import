# Copyright 2026 Ryan Duguid
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from types import SimpleNamespace
from unittest.mock import patch

from odoo.tests import HttpCase, tagged

LINK_SCRIPT = "https://cdn.plaid.com/link/v2/stable/link-initialize.js"
SDK_FIXTURE = """
window.linkSessions = [];
window.Plaid = {
    create(options) {
        const frame = document.createElement("iframe");
        frame.title = "Fixture Link";
        const bodyStyle = document.body.style.cssText;
        const session = {options, frame, destroyed: 0};
        window.linkSessions.push(session);
        return {
            open() {
                document.body.append(frame);
                if (matchMedia("(max-width: 500px)").matches) {
                    document.body.style.setProperty("height", "100px", "important");
                    document.body.style.overflow = "hidden";
                }
            },
            destroy() {
                session.destroyed++;
                frame.remove();
                document.body.style.cssText = bodyStyle;
            },
        };
    },
};
"""

BROWSER_HELPERS = """
function check(condition, message) {
    if (!condition) throw new Error(message);
}
async function waitFor(condition, message) {
    const deadline = performance.now() + 8000;
    while (!condition()) {
        check(performance.now() < deadline, message);
        await new Promise((resolve) => setTimeout(resolve, 20));
    }
}
"""


@tagged("post_install", "-at_install")
class TestPlaidLinkLifecycle(HttpCase):
    def setUp(self):
        super().setUp()
        self.script_requests = 0
        self.fail_first_load = False

    def fetch_proxy(self, url):
        if url != LINK_SCRIPT:
            return super().fetch_proxy(url)
        self.script_requests += 1
        if self.fail_first_load and self.script_requests == 1:
            return self.make_fetch_proxy_response("", code=503)
        response = self.make_fetch_proxy_response(SDK_FIXTURE)
        response["responseHeaders"] = [
            {"name": "content-type", "value": "application/javascript"},
            {"name": "cache-control", "value": "no-store"},
        ]
        return response

    def test_load_failure_retries_and_pending_link_owns_its_callback(self):
        self.fail_first_load = True
        self.browser_js(
            "/odoo",
            BROWSER_HELPERS
            + """
(async () => {
    const {registry} = odoo.loader.modules.get("@web/core/registry");
    const login = registry.category("actions").get("plaid_login");
    const calls = [];
    const notifications = [];
    const env = {services: {
        orm: {call: (...args) => calls.push(args)},
        notification: {add: (...args) => notifications.push(args)},
    }};
    const params = {
        token: "fixture-link",
        call_model: "online.bank.statement.provider",
        call_method: "plaid_create_access_token",
        object_id: 41,
    };
    check(!window.Plaid, "Link must be absent before the action");
    await Promise.all([login(env, {params}), login(env, {params})]);
    check(notifications.length === 1 && notifications[0][1].type === "danger",
        "failed load must produce one error notification");
    check(!window.Plaid && calls.length === 0, "failed load cannot exchange a token");

    const retry = login(env, {params});
    const duplicate = {params: {...params, object_id: 42}};
    await login(env, duplicate);
    await waitFor(() => window.linkSessions?.[0]?.frame.isConnected,
        "Link must open on retry");
    await login(env, duplicate);
    check(window.linkSessions.length === 1, "concurrent actions must open one Link");
    const [session] = window.linkSessions;
    const account = {id: "croft-manor-fixture", name: "Croft Manor"};
    session.options.onSuccess("fixture-public", {accounts: [account]});
    session.options.onSuccess("duplicate-public", {accounts: []});
    await retry;
    check(session.destroyed === 1 && !session.frame.isConnected,
        "successful Link must destroy its handler once");
    check(JSON.stringify(calls) === JSON.stringify([[
        params.call_model, params.call_method, ["fixture-public", 41, [account]],
    ]]), "only the owning action can forward the account and token");

    const failedLink = login(env, {params});
    await waitFor(() => window.linkSessions[1]?.frame.isConnected,
        "the next Link session must open");
    const failed = window.linkSessions[1];
    failed.options.onExit({error_code: "FIXTURE_ERROR"});
    await failedLink;
    check(failed.destroyed === 1 && !failed.frame.isConnected
        && notifications.length === 2 && calls.length === 1,
        "a Link error must clean up, notify and leave the account alone");
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready=(
                "window.odoo?.loader?.modules.has("
                "'@account_statement_import_online_plaid/js/plaid_integration.esm')"
            ),
            login="admin",
        )
        self.assertEqual(self.script_requests, 2)

    def test_mobile_sync_cancels_and_links_the_selected_account(self):
        self.browser_size = "390x844"
        self.touch_enabled = True
        bank = self.env["res.bank"].create(
            {"name": "Plaid UI fixture", "country": self.env.ref("base.us").id}
        )
        bank_account = self.env["res.partner.bank"].create(
            {
                "acc_number": "PLAID-UI-FIXTURE",
                "bank_id": bank.id,
                "partner_id": self.env.company.partner_id.id,
            }
        )
        journal = self.env["account.journal"].create(
            {
                "name": "Plaid UI fixture",
                "code": "PLUI",
                "type": "bank",
                "currency_id": self.env.ref("base.USD").id,
                "bank_account_id": bank_account.id,
            }
        )
        provider = self.env["online.bank.statement.provider"].create(
            {
                "journal_id": journal.id,
                "service": "plaid",
                "username": "fixture-client-id",
                "password": "fixture-secret",
                "plaid_host": "sandbox",
            }
        )
        self.assertFalse(provider.plaid_access_token)
        self.assertFalse(provider.plaid_account_id)
        action = self.env.ref(
            "account_statement_import_online.online_bank_statement_provider_action"
        )
        with (
            patch(
                "plaid.api.plaid_api.PlaidApi.link_token_create",
                side_effect=[
                    SimpleNamespace(to_dict=lambda: {"link_token": "fixture-first"}),
                    SimpleNamespace(to_dict=lambda: {"link_token": "fixture-second"}),
                ],
            ) as link,
            patch(
                "plaid.api.plaid_api.PlaidApi.item_public_token_exchange",
                return_value={"access_token": "fixture-access"},
            ) as exchange,
        ):
            self.browser_js(
                f"/odoo/action-{action.id}/{provider.id}",
                BROWSER_HELPERS
                + """
(async () => {
    const selector = ".o_form_view button[name='action_sync_with_plaid']";
    const sync = () => document.querySelector(selector);
    const bodyStyle = document.body.style.cssText;
    check(window.innerWidth === 390 && !window.Plaid, "expected lazy Link on mobile");
    sync().click();
    await waitFor(() => window.linkSessions?.[0]?.frame.isConnected,
        "the mobile sync button must open Link");
    const [cancelled] = window.linkSessions;
    check(cancelled.options.token === "fixture-first" && sync().disabled,
        "the sync action must remain pending while Link is open");
    check(document.body.style.overflow === "hidden", "fixture locks mobile scrolling");
    cancelled.options.onExit(null);
    await waitFor(() => sync() && !sync().disabled, "sync must be available again");
    check(cancelled.destroyed === 1 && !cancelled.frame.isConnected
        && document.body.style.cssText === bodyStyle, "exit must restore layout");

    sync().click();
    await waitFor(() => window.linkSessions[1]?.frame.isConnected,
        "the mobile sync button must reopen Link");
    const completed = window.linkSessions[1];
    check(completed.options.token === "fixture-second", "retry must use a new token");
    completed.options.onSuccess("fixture-public", {accounts: [
        {id: "fixture-single-account", name: "Fixture account"},
    ]});
    await waitFor(() => sync() && !sync().disabled, "sync must finish the write");
    check(completed.destroyed === 1 && !completed.frame.isConnected
        && document.body.style.cssText === bodyStyle,
        "successful Link must also release mobile layout");
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
                ready="""document.querySelector(
                    ".o_form_view button[name='action_sync_with_plaid']"
                ) !== null""",
                login="admin",
            )
            self.assertEqual(link.call_count, 2)
            exchange.assert_called_once()
            self.assertEqual(exchange.call_args.args[0].public_token, "fixture-public")
        provider.invalidate_recordset(["plaid_access_token", "plaid_account_id"])
        self.assertEqual(provider.plaid_access_token, "fixture-access")
        self.assertEqual(provider.plaid_account_id, "fixture-single-account")
        self.assertEqual(self.script_requests, 1)

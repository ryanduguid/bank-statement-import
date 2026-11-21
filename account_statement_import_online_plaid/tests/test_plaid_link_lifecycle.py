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
        const root = document.documentElement;
        const rootHeight = root.style.height;
        const overflow = document.body.style.overflow;
        const isIOSChrome = /CriOS/.test(navigator.userAgent);
        const session = {options, frame, destroyed: 0};
        window.linkSessions.push(session);
        return {
            open() {
                document.body.append(frame);
                if (isIOSChrome) {
                    root.id = "fixture-link-active";
                    root.style.setProperty("height", "100px", "important");
                    document.body.style.overflow = "hidden";
                    setTimeout(() => {
                        session.resizeAfterDestroy = !frame.isConnected;
                        document.body.style.setProperty("height", "100px", "important");
                    }, 100);
                    if (options.token === "fixture-first") {
                        options.onExit(null);
                    }
                }
            },
            destroy() {
                session.destroyed++;
                frame.remove();
                if (isIOSChrome) {
                    root.removeAttribute("id");
                    root.style.height = rootHeight;
                    document.body.style.overflow = overflow;
                }
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
    const actionsSelector = ".o_form_view .o_cp_action_menus button";
    const actions = () => document.querySelector(actionsSelector);
    const sync = () => document.querySelector("button[name='action_sync_with_plaid']");
    async function startLink() {
        actions().click();
        await waitFor(sync, "Odoo must offer Plaid sync in the mobile Actions menu");
        sync().click();
    }
    const root = document.documentElement;
    Object.defineProperty(navigator, "userAgent", {value: "iPhone CriOS Mobile"});
    root.id = "odoo-fixture-root";
    root.style.setProperty("height", "94vh", "important");
    document.body.style.setProperty("height", "95vh", "important");
    const bodyOverflow = document.body.style.overflow;
    function checkLayout() {
        check(root.id === "odoo-fixture-root" && root.style.height === "94vh"
            && root.style.getPropertyPriority("height") === "important",
            "Link must restore the document root ID and height with priority");
        check(document.body.style.height === "95vh"
            && document.body.style.getPropertyPriority("height") === "important"
            && document.body.style.overflow === bodyOverflow,
            "Link must restore body height, priority and scroll state");
    }
    check(window.innerWidth === 390 && !window.Plaid, "expected lazy Link on mobile");
    await startLink();
    await waitFor(() => window.linkSessions?.[0]?.destroyed && !actions()?.disabled,
        "early exit must destroy Link and re-enable Actions");
    const [cancelled] = window.linkSessions;
    check(cancelled.options.token === "fixture-first" && cancelled.resizeAfterDestroy
        && cancelled.destroyed === 1 && !cancelled.frame.isConnected,
        "early exit must survive a viewport resize after the iframe closes");
    checkLayout();

    await startLink();
    await waitFor(() => window.linkSessions[1]?.frame.isConnected,
        "the mobile sync button must reopen Link");
    const completed = window.linkSessions[1];
    check(completed.options.token === "fixture-second" && actions().disabled,
        "the new Link session must keep Actions disabled while it is open");
    check(document.body.style.overflow === "hidden", "Link must lock scrolling");
    completed.options.onSuccess("fixture-public", {accounts: [
        {id: "fixture-single-account", name: "Fixture account"},
    ]});
    await waitFor(() => actions() && !actions().disabled, "sync must finish the write");
    check(completed.destroyed === 1 && !completed.frame.isConnected,
        "successful Link must destroy its handler once");
    checkLayout();
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
                ready="""document.querySelector(
                    ".o_form_view .o_cp_action_menus button"
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

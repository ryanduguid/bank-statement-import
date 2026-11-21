import {_t} from "@web/core/l10n/translation";
import {loadJS} from "@web/core/assets";
import {registry} from "@web/core/registry";

const linkScript = "https://cdn.plaid.com/link/v2/stable/link-initialize.js";
let linkActive = false;

async function openLink(token) {
    await loadJS(linkScript);
    let handler = null;
    try {
        return await new Promise((resolve, reject) => {
            handler = globalThis.Plaid.create({
                token,
                onSuccess: (publicToken, metadata) =>
                    resolve([publicToken, metadata?.accounts ?? []]),
                onExit: (error) => (error ? reject(error) : resolve()),
            });
            handler.open();
        });
    } finally {
        handler?.destroy();
    }
}

export async function plaid_login(env, action) {
    if (linkActive) {
        return;
    }
    linkActive = true;
    try {
        const {token, call_model, call_method, object_id} = action.params;
        const result = await openLink(token).catch(() => {
            env.services.notification.add(
                _t("Could not complete Plaid Link. Reload the page if retrying fails."),
                {type: "danger"}
            );
        });
        if (result) {
            const [publicToken, accounts] = result;
            await env.services.orm.call(call_model, call_method, [
                publicToken,
                object_id,
                accounts,
            ]);
        }
    } finally {
        linkActive = false;
    }
}

registry.category("actions").add("plaid_login", plaid_login);

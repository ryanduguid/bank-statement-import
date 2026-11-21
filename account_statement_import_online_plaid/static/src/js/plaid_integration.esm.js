import {_t} from "@web/core/l10n/translation";
import {browser} from "@web/core/browser/browser";
import {isMobileOS} from "@web/core/browser/feature_detection";
import {loadJS} from "@web/core/assets";
import {registry} from "@web/core/registry";

const linkScript = "https://cdn.plaid.com/link/v2/stable/link-initialize.js";
const iosChromeResizeDelay = 100;
let linkActive = false;

function rememberHeight(element) {
    const {style} = element;
    const height = style.getPropertyValue("height");
    const priority = style.getPropertyPriority("height");
    return () => style.setProperty("height", height, priority);
}

async function openLink(token, abandoned, signal) {
    await Promise.race([loadJS(linkScript), abandoned]);
    if (signal.aborted) {
        return;
    }
    const {userAgent} = browser.navigator;
    const isIOSChrome = /CriOS/i.test(userAgent);
    const root = globalThis.document.documentElement;
    const rootId = root.getAttribute("id");
    const restoreRootHeight =
        isMobileOS() || /Mobi/i.test(userAgent) ? rememberHeight(root) : null;
    const restoreBodyHeight = isIOSChrome
        ? rememberHeight(globalThis.document.body)
        : null;
    let handler = null;
    let viewportSettled = null;
    try {
        const linked = new Promise((resolve, reject) => {
            handler = globalThis.Plaid.create({
                token,
                onSuccess: (publicToken, metadata) =>
                    resolve([publicToken, metadata?.accounts ?? []]),
                onExit: (error) => (error ? reject(error) : resolve()),
            });
            try {
                handler.open();
            } finally {
                if (isIOSChrome) {
                    viewportSettled = new Promise((done) =>
                        browser.setTimeout(done, iosChromeResizeDelay)
                    );
                }
            }
        });
        return await Promise.race([linked, abandoned]);
    } finally {
        try {
            handler?.destroy();
        } finally {
            if (restoreRootHeight) {
                restoreRootHeight();
                if (rootId === null) {
                    root.removeAttribute("id");
                } else {
                    root.setAttribute("id", rootId);
                }
            }
            if (restoreBodyHeight) {
                await viewportSettled;
                restoreBodyHeight();
            }
        }
    }
}

export async function plaid_login(env, action) {
    if (linkActive) {
        return;
    }
    linkActive = true;
    const navigation = new window.AbortController();
    const cancel = () => navigation.abort();
    const {signal} = navigation;
    const abandoned = new Promise((resolve) =>
        signal.addEventListener("abort", () => resolve(), {once: true})
    );
    try {
        globalThis.addEventListener("pagehide", cancel, {signal});
        globalThis.addEventListener("popstate", cancel, {signal});
        env.bus.addEventListener("ACTION_MANAGER:UPDATE", cancel, {signal});
        const {token, call_model, call_method, object_id} = action.params;
        const result = await openLink(token, abandoned, signal).catch(() => {
            env.services.notification.add(
                _t("Could not complete Plaid Link. Reload the page if retrying fails."),
                {type: "danger"}
            );
        });
        if (result && !signal.aborted) {
            const [publicToken, accounts] = result;
            await env.services.orm.call(call_model, call_method, [
                publicToken,
                object_id,
                accounts,
            ]);
        }
    } finally {
        navigation.abort();
        linkActive = false;
    }
}

registry.category("actions").add("plaid_login", plaid_login);

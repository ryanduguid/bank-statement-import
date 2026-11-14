# Copyright 2026 Ryan Duguid
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import hashlib
import json
import os
from pathlib import Path
from queue import SimpleQueue
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import urlparse

from odoo.tests import HttpCase, common, tagged

from .iframe_proxy import FrameProxy, fixture_browser

PLAID_PEER = r"""<!doctype html><meta charset="utf-8"><script>
const instance = new URL(location.href).searchParams.get("uniqueId");
function send(action, payload = {}, id = instance) {
    parent.postMessage(JSON.stringify({
        ...payload, action: `plaid_link-${id}::${action}`,
    }), "*");
}
function receipt(kind, payload = {}) {
    parent.postMessage({plaidFixture: true, instance, kind, ...payload}, "*");
}
addEventListener("message", (event) => {
    if (event.source !== parent) return;
    let message = event.data;
    if (typeof message === "string") {
        try { message = JSON.parse(message); } catch { return; }
    }
    if (message.plaidFixture === true) {
        if (message.kind === "raw") parent.postMessage(message.value, "*");
        else send(message.action, message.payload, message.instance || instance);
        receipt("emitted", {tag: message.tag});
    } else if (message.action === "plaid_link::configure") {
        receipt("configure", {message});
        send("ready");
    } else if (["plaid_link::open", "plaid_link::submit", "plaid_link::exit",
        "plaid_link::web3-message"]
        .includes(message.action)) {
        receipt(message.action.split("::")[1], {message});
    }
});
receipt("boot");
send("ready-for-configure");
</script>"""

BROWSER_HARNESS = r"""
const receipts = [];
function record(event) {
    if (["https://cdn.plaid.com", "https://secure.plaid.com",
        "https://plaid-peer.invalid"].includes(event.origin)
        && event.data?.plaidFixture) {
        receipts.push({source: event.source, origin: event.origin, ...event.data});
    }
}
window.addEventListener("message", record);
function check(condition, message) {
    if (!condition) throw new Error(message);
}
async function take(frame, kind, tag) {
    const deadline = performance.now() + 5000;
    while (performance.now() < deadline) {
        const index = receipts.findIndex((item) => item.source === frame.contentWindow
            && item.kind === kind && (tag === undefined || item.tag === tag));
        if (index >= 0) return receipts.splice(index, 1)[0];
        await new Promise((resolve) => setTimeout(resolve, 10));
    }
    throw new Error(`Plaid fixture timed out: ${kind}`);
}
async function emit(frame, action, payload = {}, extra = {}) {
    const tag = `${action}-${receipts.length}-${performance.now()}`;
    frame.contentWindow.postMessage({
        plaidFixture: true, kind: "emit", action, payload, tag, ...extra,
    }, new URL(frame.src).origin);
    await take(frame, "emitted", tag);
}
function frameFor(expectedOrigin = "https://cdn.plaid.com") {
    const frame = document.querySelector("iframe[id^='plaid-link-iframe-']");
    check(frame !== null, "real SDK iframe missing");
    check(new URL(frame.src).origin === expectedOrigin, "iframe origin");
    check(frame.title === "Plaid Link", "iframe accessible title");
    check(frame.sandbox.contains("allow-scripts"), "iframe sandbox");
    return frame;
}
"""

WEB3_COMPANIONS = (
    "0.js",
    "2.js",
    "10.js",
    "vendors~LazyLink~web3Bridge.js",
    "web3Bridge.js",
)


ARRAY_FALLBACK_BOOTSTRAP = r"""<script>
// The SDK needs concat to build export keys before it can install polyfills.
window.plaidArrayFallbacks = {
    native: {concat: Array.prototype.concat}, before: {},
};
for (const name of ["filter", "map", "reduce"]) {
    plaidArrayFallbacks.native[name] = Array.prototype[name];
    delete Array.prototype[name];
    plaidArrayFallbacks.before[name] = typeof Array.prototype[name];
}
</script>"""

INDEXOF_FALLBACK_BOOTSTRAP = r"""<script>
window.plaidSingleSdkFallback = {
    owner: Array.prototype, name: "indexOf", native: Array.prototype.indexOf,
    concat: Array.prototype.concat, other: Array.from,
};
delete Array.prototype.indexOf;
plaidSingleSdkFallback.before = typeof Array.prototype.indexOf;
</script>"""

ARRAY_FROM_FALLBACK_BOOTSTRAP = r"""<script>
window.plaidSingleSdkFallback = {
    owner: Array, name: "from", native: Array.from,
    concat: Array.prototype.concat, other: Array.prototype.indexOf,
};
delete Array.from;
plaidSingleSdkFallback.before = typeof Array.from;
</script>"""

URL_SEARCH_PARAMS_FALLBACK_BOOTSTRAP = r"""<script>
window.plaidSingleSdkFallback = {
    owner: window, name: "URLSearchParams", native: URLSearchParams,
    concat: Array.prototype.concat, other: URL, arrayFrom: Array.from,
    request: Request, fetch, headers: Headers,
};
delete window.URLSearchParams;
plaidSingleSdkFallback.before = typeof URLSearchParams;
</script>"""

WEAKMAP_FALLBACK_BOOTSTRAP = r"""<script>
window.plaidSingleSdkFallback = {
    owner: window, name: "WeakMap", native: WeakMap,
    concat: Array.prototype.concat, arrayFrom: Array.from,
    indexOf: Array.prototype.indexOf, assign: Object.assign,
    natives: {URL, URLSearchParams, Map, Set, WeakSet, Promise},
};
delete window.WeakMap;
plaidSingleSdkFallback.before = typeof WeakMap;
</script>"""

SDK_FALLBACK_PAGES = {
    "/array-fallbacks.html": ARRAY_FALLBACK_BOOTSTRAP,
    "/indexof-fallback.html": INDEXOF_FALLBACK_BOOTSTRAP,
    "/arrayfrom-fallback.html": ARRAY_FROM_FALLBACK_BOOTSTRAP,
    "/urlsearchparams-fallback.html": URL_SEARCH_PARAMS_FALLBACK_BOOTSTRAP,
    "/weakmap-fallback.html": WEAKMAP_FALLBACK_BOOTSTRAP,
}


PLAID_FORM_PAGE = (
    r"""<!doctype html><meta charset="utf-8"><title>Fabricated Plaid form</title>
<form id="plaid-form" method="get" action="/submission.html"
    target="plaid-form-submission"></form>
<iframe name="plaid-form-submission" src="/submission.html?initial=1"
    title="Fabricated form submission"></iframe>
<script defer src="https://plaid-form.invalid/link-initialize.js"
    data-form-id="plaid-form" data-env="sandbox"
    data-token="public-sandbox-00000000-0000-0000-0000-000000000001"
    data-client-name="Fabricated form integration" data-product="auth"
    data-select-account="true" data-webhook="https://fixture.invalid/webhook">
</script><script>
"""
    + BROWSER_HARNESS
    + r"""
window.plaidFormReady = true;
</script>"""
)


@tagged("post_install", "-at_install")
class TestPlaidLinkLifecycle(HttpCase):
    _fixture_frame_proxy = FrameProxy

    def setUp(self):
        super().setUp()
        self._fixture_requests = SimpleQueue()
        self._companion_responses = SimpleQueue()
        self._companion_status = None
        self._genuine_companions = {}

    def browser_js(self, *args, **kwargs):
        # Chrome can move a reloaded or navigated iframe to a child process.
        # Its requests still need the same fabricated responses as the page.
        browser = fixture_browser(common.ChromeBrowser, common.HOST)
        with patch.object(common, "ChromeBrowser", browser):
            return super().browser_js(*args, **kwargs)

    def fetch_proxy(self, url):
        parsed = urlparse(url)
        content_type = "text/html; charset=utf-8"
        response_code = 200
        if parsed.scheme == "https" and parsed.hostname in (
            "cdn.plaid.com",
            "secure.plaid.com",
        ):
            if parsed.path == "/link/v2/stable/link.html":
                content = PLAID_PEER
            elif parsed.path == "/link/v2/stable/link-open.html":
                content = "<!doctype html><title>Fabricated link-open receipt</title>"
            elif (
                parsed.hostname == "cdn.plaid.com"
                and (self._companion_status is not None or self._genuine_companions)
                and parsed.path
                in {f"/link/2.0.1951/{name}" for name in WEB3_COMPANIONS}
            ):
                response_code = (
                    200 if self._companion_status is None else self._companion_status
                )
                content_type = "application/javascript; charset=utf-8"
                if self._genuine_companions:
                    content = self._genuine_companions[Path(parsed.path).name]
                else:
                    content = (
                        "" if response_code == 200 else "/* Missing fixture asset */"
                    )
                self._companion_responses.put(
                    (url, response_code, content_type, content)
                )
            else:
                return super().fetch_proxy(url)
        elif parsed.hostname == "plaid-form.invalid" and (
            parsed.scheme == "https"
            or (
                parsed.scheme == "http"
                and parsed.path in {"/uuid-fallback.html", "/link-initialize.js"}
            )
        ):
            if parsed.path == "/form.html":
                content = PLAID_FORM_PAGE
            elif parsed.path in ("/web3.html", "/uuid-fallback.html") or (
                parsed.path in SDK_FALLBACK_PAGES
            ):
                content = (
                    '<!doctype html><meta charset="utf-8">'
                    "<title>Fabricated Plaid lifecycle</title>"
                    + SDK_FALLBACK_PAGES.get(parsed.path, "")
                    + '<script src="/link-initialize.js"></script>'
                )
            elif parsed.path == "/link-initialize.js":
                sdk = (
                    Path(__file__).resolve().parents[1]
                    / "static/src/lib/link/v2/stable/link-initialize.js"
                )
                content = sdk.read_bytes().decode("utf-8")
                content_type = "application/javascript; charset=utf-8"
            elif parsed.path == "/submission.html":
                content = "<!doctype html><title>Fabricated form receipt</title>"
            else:
                return super().fetch_proxy(url)
        elif (
            parsed.scheme == "https"
            and parsed.hostname == "plaid-peer.invalid"
            and parsed.path == "/link.html"
        ):
            content = PLAID_PEER.replace('send("ready-for-configure");', "")
        elif (
            parsed.scheme == "https"
            and parsed.hostname in ("sandbox.plaid.com", "production.plaid.com")
            and parsed.path == "/link/heartbeat"
        ):
            content = "{}"
        else:
            return super().fetch_proxy(url)
        self._fixture_requests.put(url)
        response = self.make_fetch_proxy_response(content)
        response["responseCode"] = response_code
        response["responseHeaders"] = [
            {"name": "content-type", "value": content_type},
            {"name": "cache-control", "value": "no-store"},
            {"name": "access-control-allow-origin", "value": "*"},
            {"name": "access-control-allow-headers", "value": "content-type"},
            {"name": "access-control-allow-methods", "value": "POST, OPTIONS"},
        ]
        return response

    def test_fixture_delegates_requests_outside_its_owned_routes(self):
        cases = (
            (None, "https://cdn.plaid.com/link/2.0.1951/0.js"),
            (404, "https://secure.plaid.com/link/2.0.1951/0.js"),
            (404, "https://cdn.plaid.com/link/2.0.1951/unknown.js"),
            (404, "https://plaid-form.invalid/unknown.html"),
            (404, "http://plaid-form.invalid/form.html"),
            (404, "http://sandbox.plaid.com/link/heartbeat"),
            (404, "https://foreign.invalid/link/heartbeat"),
            (404, "https://sandbox.plaid.com/link/unknown"),
        )
        for status, url in cases:
            response = {"responseCode": 418, "body": "Framework fallback"}
            expected = response.copy()
            with (
                self.subTest(status=status, url=url),
                patch.object(self, "_companion_status", status),
                patch.object(
                    HttpCase, "fetch_proxy", autospec=True, return_value=response
                ) as delegate,
            ):
                self.assertIs(self.fetch_proxy(url), response)
                delegate.assert_called_once_with(self, url)
                self.assertEqual(response, expected)
                self.assertTrue(self._fixture_requests.empty())
                self.assertTrue(self._companion_responses.empty())

    def test_real_sdk_restores_missing_array_methods_and_keeps_link_usable(self):
        self.browser_js(
            "https://plaid-form.invalid/array-fallbacks.html",
            BROWSER_HARNESS
            + r"""
(async () => {
    let handler;
    const bodyStyle = document.body.style.cssText;
    const successes = [], exits = [];
    function expectTypeError(run, label) {
        try {
            run();
        } catch (error) {
            check(error instanceof TypeError, label);
            return;
        }
        throw new Error(`${label}: expected TypeError`);
    }
    try {
        for (const name of ["filter", "map", "reduce"]) {
            check(typeof plaidArrayFallbacks.native[name] === "function"
                && plaidArrayFallbacks.before[name] === "undefined",
                `${name} is genuinely absent before the original SDK loads`);
            check(typeof Array.prototype[name] === "function"
                && Array.prototype[name] !== plaidArrayFallbacks.native[name]
                && !Array.prototype.propertyIsEnumerable(name),
                `${name} is restored as a non-enumerable fallback`);
        }

        check(Array.prototype.concat === plaidArrayFallbacks.native.concat,
            "the SDK preserves the working native concat required at startup");
        const spread = {1: "middle", length: 3,
            [Symbol.isConcatSpreadable]: true};
        const combined = ["head"].concat(spread, "tail");
        check(combined.length === 5 && combined[0] === "head"
            && !(1 in combined) && combined[2] === "middle"
            && !(3 in combined) && combined[4] === "tail",
            "concat preserves sparse spreadable entries and following values");
        const opaque = [1, 2];
        opaque[Symbol.isConcatSpreadable] = false;
        const unspread = [].concat(opaque);
        check(unspread.length === 1 && unspread[0] === opaque,
            "concat retains a non-spreadable array as one value");
        class Result extends Array {}
        class Source extends Array {
            static get [Symbol.species]() { return Result; }
        }
        const speciesResult = new Source(1, 2).concat([3]);
        check(speciesResult instanceof Result
            && JSON.stringify(speciesResult) === "[1,2,3]",
            "concat respects the receiver's array species");
        const huge = {length: Number.MAX_SAFE_INTEGER,
            [Symbol.isConcatSpreadable]: true};
        Object.defineProperty(huge, "0", {get() {
            throw new Error("overflow must be refused before reading an entry");
        }});
        expectTypeError(() => ["head"].concat(huge),
            "concat refuses a result longer than the safe integer limit");
        expectTypeError(() => Array.prototype.concat.call(null),
            "concat refuses a null receiver");

        const sparse = new Array(4);
        sparse[1] = 2;
        sparse[3] = 4;
        const context = {offset: 10}, mapVisits = [];
        const mapped = sparse.map(function (value, index, input) {
            mapVisits.push([value, index, input === sparse, this === context]);
            return value + this.offset;
        }, context);
        check(mapped.length === 4 && !(0 in mapped) && mapped[1] === 12
            && !(2 in mapped) && mapped[3] === 14
            && JSON.stringify(mapVisits) === "[[2,1,true,true],[4,3,true,true]]",
            "map preserves holes, callback arguments and thisArg");
        const changing = [1, 2, 3], changedVisits = [];
        const changed = changing.map((value, index) => {
            changedVisits.push(index);
            if (index === 0) {
                delete changing[1];
                changing.push(4);
            }
            return value * 2;
        });
        check(changed.length === 3 && changed[0] === 2 && !(1 in changed)
            && changed[2] === 6 && JSON.stringify(changedVisits) === "[0,2]",
            "map skips deleted entries and retains its initial iteration bound");
        const arrayLike = Object.assign(Object.create({1: 3}),
            {0: 2, 2: 5, length: 3});
        const filterVisits = [];
        const filtered = Array.prototype.filter.call(arrayLike,
            function (value, index, input) {
                filterVisits.push([index, input === arrayLike, this === context]);
                return value % 2 === 1;
            }, context);
        check(JSON.stringify(filtered) === "[3,5]"
            && JSON.stringify(filterVisits)
                === "[[0,true,true],[1,true,true],[2,true,true]]",
            "filter visits inherited array-like entries with the supplied context");
        expectTypeError(() => sparse.map(null), "map requires a callback");
        expectTypeError(() => sparse.filter(null), "filter requires a callback");
        expectTypeError(() => Array.prototype.map.call(undefined, () => 0),
            "map refuses an undefined receiver");

        const reduceVisits = [];
        const total = Array.prototype.reduce.call(arrayLike,
            (previous, value, index, input) => {
                reduceVisits.push([previous, value, index, input === arrayLike]);
                return previous + value;
            });
        check(total === 10 && JSON.stringify(reduceVisits)
            === "[[2,3,1,true],[5,5,2,true]]",
            "reduce takes its initial value from the first present entry");
        check(sparse.reduce((previous, value) => previous + value, 10) === 16,
            "reduce preserves an explicit initial value and skips holes");
        let emptyCalls = 0;
        check(new Array(3).reduce(() => { emptyCalls++; }, 7) === 7
            && emptyCalls === 0, "empty sparse reduction retains its seed");
        expectTypeError(() => [].reduce(() => 0),
            "reduce refuses an empty array without a seed");
        expectTypeError(() => new Array(3).reduce(() => 0),
            "reduce refuses an all-hole array without a seed");
        expectTypeError(() => [].reduce(null, 0),
            "reduce validates its callback even for an empty seeded array");

        handler = Plaid.create({
            env: "sandbox", token: "link-sandbox-fabricated",
            onSuccess: (...args) => successes.push(args),
            onExit: (...args) => exits.push(args),
        }, {forceDesktop: true});
        const frame = frameFor();
        const configured = (await take(frame, "configure")).message.config;
        check(configured.origin === location.origin,
            "the SDK configures its owned frame after installing fallbacks");
        handler.open();
        await take(frame, "open");
        handler.exit({force: true});
        await take(frame, "exit");
        await emit(frame, "exit", {error: null, metadata: {status: "cancelled"}});
        check(successes.length === 0 && exits.length === 1 && exits[0][0] === null
            && exits[0][1].status === "cancelled" && frame.style.display === "none",
            "normal cancellation preserves the callback payload with fallbacks");
        handler.destroy();
        handler = null;
        check(!frame.isConnected && successes.length === 0,
            "destroy removes the owned frame without reporting a success");
    } finally {
        if (handler) handler.destroy();
        window.removeEventListener("message", record);
        document.body.style.cssText = bodyStyle;
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

    def _assert_single_sdk_fallback(self, route, assertions):
        self.browser_js(
            "https://plaid-form.invalid" + route,
            BROWSER_HARNESS
            + r"""
(async () => {
    let handler;
    const bodyStyle = document.body.style.cssText;
    const successes = [], exits = [];
    function expectTypeError(run, label) {
        try {
            run();
        } catch (error) {
            check(error instanceof TypeError, label);
            return;
        }
        throw new Error(`${label}: expected TypeError`);
    }
    try {
        const fallback = plaidSingleSdkFallback;
        check(typeof fallback.native === "function" && fallback.before === "undefined",
            "the selected native API is absent before the original SDK loads");
        check(typeof fallback.owner[fallback.name] === "function"
            && fallback.owner[fallback.name] !== fallback.native
            && !fallback.owner.propertyIsEnumerable(fallback.name),
            "the original SDK installs a non-enumerable replacement");
        check(Array.prototype.concat === fallback.concat,
            "the native concat required by SDK startup is preserved");
"""
            + assertions
            + r"""
        handler = Plaid.create({
            env: "sandbox", token: "link-sandbox-fabricated",
            onSuccess: (...args) => successes.push(args),
            onExit: (...args) => exits.push(args),
        }, {forceDesktop: true});
        const frame = frameFor();
        const configured = (await take(frame, "configure")).message.config;
        check(configured.origin === location.origin,
            "the real SDK configures its owned frame with the fallback installed");
        handler.open();
        await take(frame, "open");
        handler.exit({force: true});
        await take(frame, "exit");
        await emit(frame, "exit", {error: null, metadata: {status: "cancelled"}});
        check(successes.length === 0 && exits.length === 1 && exits[0][0] === null
            && exits[0][1].status === "cancelled" && frame.style.display === "none",
            "cancellation retains its callback payload without a success callback");
        handler.open();
        await take(frame, "open");
        const metadata = {
            public_token: "public-sandbox-fabricated",
            accounts: [{id: "fabricated-fallback-account"}],
        };
        await emit(frame, "connected", {metadata});
        check(successes.length === 1 && successes[0][0] === metadata.public_token
            && successes[0][1].accounts[0].id === "fabricated-fallback-account"
            && exits.length === 1 && frame.style.display === "none",
            "reopening delivers the real success token and account metadata");
        handler.destroy();
        handler = null;
        check(!frame.isConnected && successes.length === 1 && exits.length === 1,
            "destroy removes the owned frame without adding callbacks");
    } finally {
        if (handler) handler.destroy();
        window.removeEventListener("message", record);
        document.body.style.cssText = bodyStyle;
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

    def test_real_sdk_indexof_fallback_preserves_search_contracts(self):
        self._assert_single_sdk_fallback(
            "/indexof-fallback.html",
            r"""
        check(Array.from === fallback.other, "Array.from remains native on this page");
        const find = Array.prototype.indexOf;
        const sparse = new Array(4);
        sparse[1] = undefined;
        sparse[3] = "last";
        check(find.call(sparse, undefined) === 1
            && find.call({length: 3}, undefined) === -1,
            "indexOf skips holes but matches an explicitly undefined entry");
        const inherited = Object.assign(Object.create({1: "inherited"}),
            {0: "own", length: 2});
        check(find.call(inherited, "inherited") === 1
            && find.call("abc", "b") === 1,
            "indexOf supports inherited array-like entries and string receivers");
        const needle = {};
        check([NaN, needle].indexOf(NaN) === -1
            && [needle].indexOf(needle) === 0 && [needle].indexOf({}) === -1,
            "indexOf uses strict equality and object identity");
        const repeated = ["a", "b", "a"];
        check(repeated.indexOf("a") === 0 && repeated.indexOf("a", 1.9) === 2
            && repeated.indexOf("a", -1.9) === 2
            && repeated.indexOf("a", -99) === 0
            && repeated.indexOf("a", 99) === -1
            && repeated.indexOf("a", Infinity) === -1
            && repeated.indexOf("a", -Infinity) === 0
            && repeated.indexOf("a", "2") === 2
            && repeated.indexOf("a", NaN) === 0
            && Object.is(repeated.indexOf("a", -0), 0),
            "indexOf coerces and bounds fromIndex and returns positive zero");
        const changing = {0: "first", length: 2};
        let coercions = 0;
        const start = {valueOf() {
            coercions++;
            changing.length = 0;
            changing[1] = "created";
            changing[2] = "created";
            return 0;
        }};
        check(find.call(changing, "created", start) === 1 && coercions === 1,
            "indexOf captures length before coercion but reads entries afterwards");
        expectTypeError(() => find.call(null, "a"), "indexOf refuses null");
        expectTypeError(() => find.call(undefined, "a"), "indexOf refuses undefined");
        expectTypeError(() => repeated.indexOf("a", Symbol("start")),
            "indexOf refuses a Symbol fromIndex");
""",
        )

    def test_real_sdk_arrayfrom_fallback_preserves_copy_and_iterator_contracts(self):
        self._assert_single_sdk_fallback(
            "/arrayfrom-fallback.html",
            r"""
        check(Array.prototype.indexOf === fallback.other,
            "indexOf remains native on this page");
        const sparse = new Array(3);
        sparse[1] = 7;
        const dense = Array.from(sparse);
        check(dense.length === 3 && 0 in dense && 1 in dense && 2 in dense
            && dense[0] === undefined && dense[1] === 7 && dense[2] === undefined,
            "Array.from copies sparse input into explicit dense entries");
        const arrayLike = Object.assign(Object.create({1: 5}), {0: 3, length: 3});
        const context = {offset: 10}, visits = [];
        const mapped = Array.from(arrayLike, function (value, index) {
            visits.push([value === undefined ? "missing" : value,
                index, arguments.length, this === context]);
            return value === undefined ? "missing" : value + this.offset;
        }, context);
        check(JSON.stringify(mapped) === '[13,15,"missing"]'
            && JSON.stringify(visits)
                === '[[3,0,2,true],[5,1,2,true],["missing",2,2,true]]',
            "Array.from maps inherited and missing entries with exactly two arguments");
        const changing = {0: 2, 1: 4, 2: 6, length: 3}, indexes = [];
        const changed = Array.from(changing, (value, index) => {
            indexes.push(index);
            if (index === 0) {
                delete changing[1];
                changing[3] = 8;
                changing.length = 4;
            }
            return value;
        });
        check(changed.length === 3 && 1 in changed && changed[1] === undefined
            && JSON.stringify(changed) === "[2,null,6]"
            && JSON.stringify(indexes) === "[0,1,2]",
            "Array.from keeps its initial array-like length and reads later mutations");
        const iterable = {
            get length() { throw new Error("iterable length must not be read"); },
            *[Symbol.iterator]() { yield "first"; yield "second"; },
        };
        check(JSON.stringify(Array.from(iterable)) === '["first","second"]',
            "Array.from prefers the iterator over an array-like length");
        const unicode = Array.from("A\u{1F600}B");
        check(unicode.length === 3 && unicode[1] === "\u{1F600}"
            && unicode[1].length === 2,
            "Array.from retains a Unicode surrogate pair as one iterator value");
        function Result(...args) { this.constructorArgs = args; }
        const generic = Array.from.call(Result, {0: "a", 1: "b", length: 2});
        const iterated = Array.from.call(Result, iterable);
        check(generic instanceof Result && generic.length === 2
            && generic[0] === "a" && generic[1] === "b"
            && JSON.stringify(generic.constructorArgs) === "[2]"
            && iterated instanceof Result && iterated.length === 2
            && iterated[0] === "first" && iterated[1] === "second"
            && iterated.constructorArgs.length === 0,
            "Array.from passes length only to the array-like result constructor");
        expectTypeError(() => Array.from(null), "Array.from refuses null");
        expectTypeError(() => Array.from(undefined), "Array.from refuses undefined");
        expectTypeError(() => Array.from([], null), "Array.from validates its mapper");
        expectTypeError(() => Array.from({[Symbol.iterator]: 3}),
            "Array.from refuses a non-callable iterator method");
        expectTypeError(() => Array.from({[Symbol.iterator]() { return 1; }}),
            "Array.from refuses a primitive iterator factory result");
        for (const returnThrows of [false, true]) {
            const original = new Error("mapper failure"), closing = new Error("close");
            let steps = 0, closes = 0, observed;
            const source = {[Symbol.iterator]() { return {
                next() { return {value: ++steps, done: steps > 2}; },
                return() {
                    closes++;
                    if (returnThrows) throw closing;
                    return {};
                },
            }; }};
            try {
                Array.from(source, () => { throw original; });
            } catch (error) {
                observed = error;
            }
            check(observed === original && steps === 1 && closes === 1,
                "mapper failure closes once and retains the original error");
        }
""",
        )

    def test_real_sdk_weakmap_fallback_preserves_object_and_frozen_key_storage(self):
        self._assert_single_sdk_fallback(
            "/weakmap-fallback.html",
            r"""
        for (const [name, native] of Object.entries(fallback.natives)) {
            check(window[name] === native, `${name} remains native`);
        }
        check(Array.from === fallback.arrayFrom
            && Array.prototype.indexOf === fallback.indexOf
            && Object.assign === fallback.assign, "other native helpers survive");
        const map = new WeakMap(), other = new WeakMap();
        const key = {label: "first"}, distinct = {label: "first"};
        Object.defineProperty(key, "sentinel", {value: 7});
        check(map.get(key) === undefined && map.has(key) === false
            && map.delete(key) === false, "a new object key is absent");
        check(map.set(key, "initial") === map
            && map.set(distinct, "separate") === map
            && map.get(key) === "initial" && map.get(distinct) === "separate",
            "set is chainable and equal-looking objects retain distinct identities");
        map.set(key, "updated");
        other.set(key, "other-map");
        check(map.get(key) === "updated" && other.get(key) === "other-map"
            && other.has(distinct) === false && other.delete(distinct) === false,
            "overwrites and metadata from one map do not affect another map");
        map.set(distinct, undefined);
        check(map.has(distinct) === true && map.get(distinct) === undefined,
            "has distinguishes a stored undefined value from an absent key");
        const callable = function fixtureKey() {}, array = [];
        map.set(callable, "function").set(array, "array");
        check(map.get(callable) === "function" && map.get(array) === "array",
            "functions and arrays are valid identity keys");
        check(Object.keys(key).join(",") === "label"
            && Object.getOwnPropertyNames(key).sort().join(",") === "label,sentinel"
            && JSON.stringify(key) === '{"label":"first"}'
            && key.sentinel === 7
            && Object.getOwnPropertyDescriptor(key, "sentinel").enumerable === false,
            "fallback storage preserves visible enumerable and non-enumerable fields");
        const frozen = Object.freeze({label: "frozen"});
        const closed = Object.preventExtensions({label: "closed"});
        const later = {label: "later"};
        check(map.get(frozen) === undefined && map.has(frozen) === false
            && map.delete(frozen) === false, "an unseen frozen key is absent");
        map.set(frozen, "first-frozen").set(closed, "closed-value");
        map.set(later, "before-freeze");
        Object.freeze(later);
        map.set(later, "after-freeze");
        other.set(frozen, "independent-frozen");
        map.set(frozen, "updated-frozen");
        check(map.get(frozen) === "updated-frozen" && map.has(frozen) === true
            && map.get(closed) === "closed-value" && map.has(closed) === true
            && map.get(later) === "after-freeze",
            "keys closed before and after insertion retain independent values");
        check(map.delete(frozen) === true && map.delete(frozen) === false
            && map.get(frozen) === undefined && map.has(frozen) === false
            && map.get(closed) === "closed-value"
            && other.get(frozen) === "independent-frozen",
            "frozen deletion removes only the selected key from its own map");
        map.set(frozen, undefined);
        check(map.has(frozen) === true && map.get(frozen) === undefined
            && map.delete(closed) === true && map.delete(closed) === false,
            "frozen keys support reinsertion, undefined values and repeated deletion");
        check(map.delete(key) === true && map.delete(key) === false
            && other.get(key) === "other-map",
            "ordinary deletion preserves other maps");
        for (const primitive of [null, undefined, false, true, 0, 1, "", "key"]) {
            check(map.get(primitive) === undefined && map.has(primitive) === false
                && map.delete(primitive) === false, "primitive lookup is absent");
            expectTypeError(() => map.set(primitive, "refused"), "primitive set");
        }
        for (const method of ["get", "has", "delete", "set"]) {
            expectTypeError(() => WeakMap.prototype[method].call({}, key, "value"),
                `${method} refuses an incompatible receiver`);
        }
        expectTypeError(() => WeakMap(), "WeakMap requires new");
""",
        )

    def test_real_sdk_weakmap_fallback_preserves_finite_constructor_iteration(self):
        self._assert_single_sdk_fallback(
            "/weakmap-fallback.html",
            r"""
        for (const [name, native] of Object.entries(fallback.natives)) {
            check(window[name] === native, `${name} remains native`);
        }
        check(Array.from === fallback.arrayFrom
            && Array.prototype.indexOf === fallback.indexOf
            && Object.assign === fallback.assign, "other native helpers survive");
        const key = {}, second = {}, absent = {};
        check(new WeakMap().has(absent) === false
            && new WeakMap(null).has(absent) === false
            && new WeakMap(undefined).has(absent) === false,
            "missing, null and undefined constructor inputs create empty maps");
        const pairs = new WeakMap([[key, "first"], [key, "last"], [second]]);
        check(pairs.get(key) === "last" && pairs.has(second) === true
            && pairs.get(second) === undefined, "array entries replace duplicate keys");
        let steps = 0;
        const value = {label: "same-value"};
        const iterable = {[Symbol.iterator]() {
            return {next() {
                steps++;
                if (steps === 1) return {done: false, value: [key, value]};
                if (steps === 2) return {done: false, value: [second, "second"]};
                return {done: true};
            }};
        }};
        const copied = new WeakMap(iterable);
        check(steps === 3 && copied.get(key) === value
            && copied.get(second) === "second",
            "finite custom iteration stores entries");
        for (const input of [1, true, {}, "x"]) {
            expectTypeError(() => new WeakMap(input), "invalid constructor input");
        }
        for (const entry of [1, null, undefined, [1, "value"], [null, "value"]]) {
            expectTypeError(() => new WeakMap([entry]), "invalid constructor entry");
        }
        for (const slot of ["0", "1"]) {
            for (const failReturn of [false, true]) {
                const failure = new Error("fabricated entry read failure");
                const closeFailure = new Error("fabricated iterator close failure");
                const entry = {0: {}, 1: "unused"};
                Object.defineProperty(entry, slot, {get() { throw failure; }});
                let reads = 0, closes = 0, observed;
                const failing = {[Symbol.iterator]() {
                    return {
                        next() {
                            reads++;
                            return reads === 1 ? {done: false, value: entry}
                                : {done: true};
                        },
                        return() {
                            closes++;
                            if (failReturn) throw closeFailure;
                            return {done: true};
                        },
                    };
                }};
                try { new WeakMap(failing); } catch (error) { observed = error; }
                check(observed === failure && reads === 1 && closes === 1,
                    "entry failure closes once and preserves the original error");
            }
        }
""",
        )

    def test_real_sdk_urlsearchparams_fallback_preserves_query_contracts(self):
        self._assert_single_sdk_fallback(
            "/urlsearchparams-fallback.html",
            r"""
        const Params = URLSearchParams;
        check(URL === fallback.other && Headers === fallback.headers
            && Array.from === fallback.arrayFrom,
            "the fallback retains native URL, Headers and array conversion");
        check(new URL("https://fixture.invalid/?a=1").searchParams.get("a") === "1",
            "native URL query handling remains usable");
        check(new Params().size === 0 && String(new Params(undefined)) === ""
            && String(new Params(7)) === "7=",
            "empty and scalar constructors retain their query meaning");
        const params = new Params("?dup=first&empty=&dup=second&space=two+words"
            + "&encoded=%21%27%28%29%7E&unicode=%C3%A9%F0%9F%98%80"
            + "&equals=a=b&&bare");
        const serialized = "dup=first&empty=&dup=second&space=two+words"
            + "&encoded=%21%27%28%29%7E&unicode=%C3%A9%F0%9F%98%80"
            + "&equals=a%3Db&bare=";
        check(params.size === 8 && params.get("dup") === "first"
            && JSON.stringify(params.getAll("dup")) === '["first","second"]'
            && params.get("empty") === "" && params.get("bare") === ""
            && params.get("space") === "two words" && params.get("encoded") === "!'()~"
            && params.get("unicode") === "\u00e9\u{1F600}"
            && params.get("equals") === "a=b" && String(params) === serialized,
            "query parsing retains duplicates, empty values, Unicode and encoding");
        check(params.get("missing") === null && params.getAll("missing").length === 0
            && params.has("dup") && params.has("dup", "second")
            && !params.has("dup", "absent") && !params.has("missing"),
            "lookup distinguishes missing keys and requested values");
        const malformed = new Params("x=%41%C3%A9%C3%A9%ZZ");
        check(malformed.get("x") === "A\u00e9\u00e9%ZZ"
            && String(malformed) === "x=A%C3%A9%C3%A9%25ZZ",
            "malformed escapes retain valid UTF-8 and invalid percent text");
        let reads = 0;
        const recordInput = Object.create({inherited: "ignored"});
        Object.defineProperty(recordInput, "count", {
            enumerable: true, get() { reads++; return 7; },
        });
        recordInput.nullable = null;
        const fromRecord = new Params(recordInput);
        check(reads === 1 && String(fromRecord) === "count=7&nullable=null"
            && !fromRecord.has("inherited"),
            "records read own enumerable values once and exclude inheritance");
        let iterations = 0;
        const pairs = {*[Symbol.iterator]() {
            iterations++;
            yield ["x", 1];
            yield ["x", 2];
        }};
        const fromPairs = new Params(pairs), copied = new Params(fromPairs);
        fromPairs.append("x", 3);
        check(iterations === 1 && String(copied) === "x=1&x=2"
            && String(fromPairs) === "x=1&x=2&x=3",
            "iterable construction copies pairs without sharing mutable storage");
        for (const pair of [[], ["only"], ["too", "many", "items"]]) {
            expectTypeError(() => new Params([pair]),
                "iterable entries require exactly two elements");
        }
        expectTypeError(() => new Params([null]), "primitive pairs are refused");
        expectTypeError(() => new Params(Symbol("query")), "Symbol input is refused");
        expectTypeError(() => Params("x=1"), "the constructor requires new");
        const edited = new Params("key=first&keep=yes&key=second&key=third");
        edited.set("key", "replacement");
        edited.append("key", "last");
        edited.set("added", "a b");
        check(edited.size === 4
            && String(edited) === "key=replacement&keep=yes&key=last&added=a+b",
            "set replaces duplicates in place and append retains later duplicates");
        edited.delete("key");
        edited.delete("absent");
        edited.append("filter", "one");
        edited.append("filter", "two");
        edited.delete("filter", "one");
        check(edited.size === 3 && String(edited) === "keep=yes&added=a+b&filter=two"
            && edited.has("filter", "two") && !edited.has("filter", "one"),
            "deletion preserves unrelated entries and the selected other value");
        const small = new Params("z=last&a=first&z=second&b=middle");
        small.sort();
        check(String(small) === "a=first&b=middle&z=last&z=second",
            "small sorting is ordered and stable for duplicate keys");
        const large = new Params([
            ["z", "0"], ["c", "1"], ["b", "2"], ["a", "3"],
            ["b", "4"], ["d", "5"], ["c", "6"], ["a", "7"],
            ["e", "8"], ["b", "9"], ["d", "10"], ["f", "11"],
        ]);
        large.sort();
        check(String(large) === "a=3&a=7&b=2&b=4&b=9&c=1&c=6"
            + "&d=5&d=10&e=8&f=11&z=0",
            "larger sorting preserves duplicate order across merge boundaries");
        const changing = new Params("a=1&b=2"), visits = [], context = {};
        changing.forEach(function (value, key, owner) {
            visits.push([value, key, owner === changing, this === context,
                arguments.length]);
            if (key === "a") changing.append("c", "3");
        }, context);
        check(JSON.stringify(visits)
            === '[["1","a",true,true,3],["2","b",true,true,3],["3","c",true,true,3]]',
            "forEach retains arguments and context and sees finite appends");
        check(JSON.stringify(Array.from(changing.keys())) === '["a","b","c"]'
            && JSON.stringify(Array.from(changing.values())) === '["1","2","3"]'
            && JSON.stringify(Array.from(changing))
                === '[["a","1"],["b","2"],["c","3"]]',
            "key, value and default entry iteration retain insertion order");
        const iterator = changing.entries();
        check(iterator[Symbol.iterator]() === iterator,
            "the entry iterator is its own iterable");
        check(JSON.stringify(Array.from(iterator)) === '[["a","1"],["b","2"],["c","3"]]'
            && iterator.next().done, "entry iteration reaches exhaustion");
        changing.append("d", "4");
        const exhausted = iterator.next();
        check(exhausted.done && exhausted.value === undefined,
            "an exhausted iterator remains exhausted after a later append");
        const unchanged = String(params);
        expectTypeError(() => params.append("missing"), "append needs two arguments");
        for (const name of ["delete", "get", "getAll", "has", "set"]) {
            expectTypeError(() => params[name](),
                `${name} needs its required arguments`);
        }
        expectTypeError(() => params.get.call({}, "x"), "get checks its receiver");
        expectTypeError(() => params.entries.call({}), "entries checks its receiver");
        expectTypeError(() => params.toString.call({}),
            "serialization checks its receiver");
        expectTypeError(() => params.forEach(null), "forEach requires a callback");
        expectTypeError(() => params.append("x", Symbol("value")),
            "append refuses a Symbol value");
        const size = Object.getOwnPropertyDescriptor(Params.prototype, "size").get;
        expectTypeError(() => size.call({}), "size checks its receiver");
        check(String(params) === unchanged,
            "rejected operations preserve all existing query entries");
""",
        )

    def test_real_sdk_urlsearchparams_fallback_serializes_real_web_requests(self):
        self._assert_single_sdk_fallback(
            "/urlsearchparams-fallback.html",
            r"""
        check(URL === fallback.other && Headers === fallback.headers
            && Array.from === fallback.arrayFrom,
            "web integration retains the other native APIs");
        check(Request !== fallback.request
            && Request.prototype === fallback.request.prototype
            && fetch !== fallback.fetch,
            "the genuine SDK installs its Request and fetch integration");
        const target = "https://plaid-form.invalid/submission.html";
        const body = new URLSearchParams([
            ["memo", "two words"], ["unicode", "\u00e9"], ["dup", "1"], ["dup", "2"],
        ]);
        const encoded = "memo=two+words&unicode=%C3%A9&dup=1&dup=2";
        const request = new Request(target, {method: "POST", body});
        check(request instanceof fallback.request && request.method === "POST"
            && request.headers.get("content-type")
                === "application/x-www-form-urlencoded;charset=UTF-8"
            && await request.text() === encoded,
            "Request serializes fallback parameters with the form content type");
        const headers = new Headers({"content-type": "application/vnd.fixture",
            "x-fixture": "preserved"});
        const options = {method: "POST", headers, body};
        const explicit = new Request(target, options);
        check(explicit.headers.get("content-type") === "application/vnd.fixture"
            && explicit.headers.get("x-fixture") === "preserved"
            && await explicit.text() === encoded
            && options.body === body && options.headers === headers
            && headers.get("content-type") === "application/vnd.fixture"
            && String(body) === encoded,
            "explicit headers and original options survive request construction");
        const empty = new Request(target), clone = new Request(empty);
        const plain = new Request(target, {method: "POST", body: "plain"});
        check(empty.method === "GET" && empty.body === null
            && empty.headers.get("content-type") === null && clone.url === empty.url
            && plain.headers.get("content-type") === "text/plain;charset=UTF-8"
            && await plain.text() === "plain",
            "other request bodies retain native defaults and string handling");
        expectTypeError(() => Request(target), "Request still requires new");
        for (const [suffix, init] of [
            ["fallback", {method: "POST", body}],
            ["plain", {method: "POST", body: "plain"}],
        ]) {
            const response = await fetch(`${target}?urlparams=${suffix}`, init);
            check(response.ok
                && (await response.text()).includes("Fabricated form receipt"),
                "real fetch completes against the owned route for each body type");
        }
        const response = await fetch(new Request(`${target}?urlparams=prebuilt`));
        check(response.ok
            && (await response.text()).includes("Fabricated form receipt"),
            "real fetch also accepts a prebuilt request without an options argument");
""",
        )
        requests = []
        while not self._fixture_requests.empty():
            requests.append(self._fixture_requests.get_nowait())
        for suffix in ("fallback", "plain", "prebuilt"):
            self.assertIn(
                f"https://plaid-form.invalid/submission.html?urlparams={suffix}",
                requests,
            )

    def test_insecure_page_generates_uuid_fallback_across_reopen(self):
        self.browser_js(
            "http://plaid-form.invalid/uuid-fallback.html",
            BROWSER_HARNESS
            + r"""
(async () => {
    let handler;
    const bodyStyle = document.body.style.cssText;
    const successes = [], exits = [];
    const uuid =
        /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
    try {
        check(location.origin === "http://plaid-form.invalid"
            && !isSecureContext, "fixture uses a real insecure origin");
        check(!("randomUUID" in crypto)
            && typeof crypto.getRandomValues === "function",
            "native browser crypto requires the SDK UUID fallback");
        const randomBytes = new Uint8Array(16);
        check(crypto.getRandomValues(randomBytes) === randomBytes,
            "browser retains its standard random-byte API");
        handler = Plaid.create({
            env: "sandbox", token: "link-sandbox-fabricated",
            onSuccess: (...args) => successes.push(args),
            onExit: (...args) => exits.push(args),
        }, {forceDesktop: true});
        const frame = frameFor();
        const configured = (await take(frame, "configure")).message.config;
        const frameUrl = new URL(frame.src);
        const initialId = configured.linkOpenId;
        check(uuid.test(initialId), "initial configuration receives a UUIDv4");
        check(frameUrl.searchParams.get("linkOpenId") === initialId
            && frameUrl.searchParams.get("uniqueId") === configured.uniqueId,
            "iframe URL carries the public configuration identifiers");
        check(configured.origin === location.origin
            && frameUrl.searchParams.get("origin") === location.origin,
            "configuration and iframe URL preserve the insecure parent origin");
        handler.open();
        check((await take(frame, "open")).message.linkOpenId === initialId,
            "initial open carries the configured UUID");
        check(frame.style.display === "block" && exits.length === 0
            && successes.length === 0, "opening does not complete the link");
        handler.exit({force: true});
        check((await take(frame, "exit")).message.config.force === true,
            "public force exit reaches the owned peer");
        await emit(frame, "exit", {error: null, metadata: {status: "cancelled"}});
        check(frame.style.display === "none" && exits.length === 1
            && exits[0][0] === null && exits[0][1].status === "cancelled",
            "peer cancellation hides Link and preserves the callback payload");
        handler.open();
        const reopened = (await take(frame, "open")).message;
        check(uuid.test(reopened.linkOpenId) && reopened.linkOpenId !== initialId,
            "reopening after cancellation generates a fresh UUIDv4");
        check(frameFor() === frame && frame.style.display === "block"
            && new URL(frame.src).searchParams.get("linkOpenId") === initialId,
            "reopening reuses the configured peer without rewriting its URL");
        handler.destroy();
        handler = null;
        check(!frame.isConnected && successes.length === 0 && exits.length === 1,
            "destroy removes the peer without a fabricated success or extra exit");
    } finally {
        if (handler) handler.destroy();
        window.removeEventListener("message", record);
        document.body.style.cssText = bodyStyle;
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

    def _assert_web3_companion_failure(self, status, failure_type):
        self._companion_status = status
        self.browser_js(
            "https://plaid-form.invalid/web3.html",
            BROWSER_HARNESS
            + r"""
(async () => {
    const names = ["0.js", "2.js", "10.js",
        "vendors~LazyLink~web3Bridge.js", "web3Bridge.js"];
    const urls = names.map(name => "https://cdn.plaid.com/link/2.0.1951/" + name);
    const scriptEvents = [], failures = [], unexpected = [];
    const successes = [], exits = [];
    function resource(event) {
        if (event.target instanceof HTMLScriptElement
            && urls.includes(event.target.src)) {
            scriptEvents.push({url: event.target.src, type: event.type});
        }
    }
    function rejection(event) {
        const error = event.reason;
        if (error?.name === "ChunkLoadError"
            && error.type === "__FAILURE_TYPE__" && urls.includes(error.request)) {
            failures.push(error);
            event.preventDefault();
        } else {
            unexpected.push(error);
        }
    }
    document.addEventListener("load", resource, true);
    document.addEventListener("error", resource, true);
    window.addEventListener("unhandledrejection", rejection);
    let handler, frame;
    try {
        handler = Plaid.create({
            env: "sandbox", token: "link-sandbox-fabricated",
            onSuccess: (...args) => successes.push(args),
            onExit: (...args) => exits.push(args),
        }, {web3ValidChains: ["eip155:1"]});
        handler.open();
        frame = frameFor();
        const configured = (await take(frame, "configure")).message.config;
        await take(frame, "open");
        check(configured.token === "link-sandbox-fabricated", "configured token");
        check(JSON.stringify(configured.web3ValidChains) === '["eip155:1"]',
            "configured Web3 chains");
        await emit(frame, "web3-message", {message: "START_BRIDGE"});
        const deadline = performance.now() + 5000;
        while ((scriptEvents.length < 5 || failures.length < 1)
            && performance.now() < deadline) {
            await new Promise(resolve => setTimeout(resolve, 10));
        }
        check(scriptEvents.length === 5, "all five real companion script events");
        check(new Set(scriptEvents.map(event => event.url)).size === 5,
            "one browser event per companion URL");
        const expectedEvent = "__FAILURE_TYPE__" === "error" ? "error" : "load";
        check(scriptEvents.every(event => event.type === expectedEvent),
            "actual browser resource failure kind");
        check(failures.length === 1 && unexpected.length === 0,
            "only the expected chunk rejection is suppressed");
        check(failures[0].message.includes(failures[0].request),
            "chunk error retains the actual request URL");
        check(successes.length === 0 && exits.length === 0,
            "failed companion loading produces no successful provider result or exit");
    } finally {
        handler?.destroy();
        document.removeEventListener("load", resource, true);
        document.removeEventListener("error", resource, true);
        window.removeEventListener("unhandledrejection", rejection);
        window.removeEventListener("message", record);
        for (const script of document.querySelectorAll("script[src]")) {
            if (urls.includes(script.src)) script.remove();
        }
    }
    check(frame && !frame.isConnected, "public destroy removes the owned Link iframe");
    console.log("test successful");
})().catch(error => console.error(error.stack));
""".replace("__FAILURE_TYPE__", failure_type),
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        responses = []
        while not self._companion_responses.empty():
            responses.append(self._companion_responses.get())
        self.assertEqual(
            sorted(urlparse(url).path for url, *_rest in responses),
            sorted(f"/link/2.0.1951/{name}" for name in WEB3_COMPANIONS),
        )
        for url, code, content_type, body in responses:
            self.assertEqual(urlparse(url).hostname, "cdn.plaid.com")
            self.assertEqual(code, status)
            self.assertEqual(content_type, "application/javascript; charset=utf-8")
            self.assertEqual(
                body, "" if status == 200 else "/* Missing fixture asset */"
            )

    def test_web3_companion_http_failures_reject_the_real_sdk_loader(self):
        self._assert_web3_companion_failure(404, "error")

    def test_web3_companions_without_registration_reject_the_real_sdk_loader(self):
        self._assert_web3_companion_failure(200, "missing")

    def test_real_web3_companions_report_wallet_plugin_discovery(self):
        manifest = json.loads(
            (Path(__file__).parent / "fixtures/plaid_web3_companions.json").read_text()
        )
        cache = Path(os.environ["PLAID_TEST_COMPANION_DIR"])
        self.assertEqual(
            [asset["name"] for asset in manifest["assets"]], list(WEB3_COMPANIONS)
        )
        for asset in manifest["assets"]:
            content = (cache / asset["name"]).read_bytes()
            self.assertEqual(len(content), asset["bytes"])
            self.assertEqual(hashlib.sha256(content).hexdigest(), asset["sha256"])
            self._genuine_companions[asset["name"]] = content.decode("utf-8")
        self.browser_js(
            "https://plaid-form.invalid/web3.html",
            BROWSER_HARNESS
            + r"""
(async () => {
    const names = ["0.js", "2.js", "10.js",
        "vendors~LazyLink~web3Bridge.js", "web3Bridge.js"];
    const urls = names.map(name => "https://cdn.plaid.com/link/2.0.1951/" + name);
    const scripts = [], failures = [], successes = [], exits = [];
    const bodyStyle = document.body.style.cssText;
    function resource(event) {
        if (event.target instanceof HTMLScriptElement
            && urls.includes(event.target.src)) {
            scripts.push({url: event.target.src, type: event.type});
        }
    }
    function rejection(event) {
        failures.push(event.reason);
    }
    function pluginReceipt(receipt) {
        const message = receipt.message;
        check(message.action === "plaid_link::web3-message"
            && message.message === "RESPONSE_PLUGIN_DATA",
            "genuine bridge responds through the configured peer");
        check(JSON.stringify(message.metadata) === '{"installedWalletIds":[]}',
            "clean browser reports no installed wallet plugins");
    }
    document.addEventListener("load", resource, true);
    document.addEventListener("error", resource, true);
    window.addEventListener("unhandledrejection", rejection);
    let handler, frame;
    try {
        check(!window.ethereum, "clean browser has no injected Ethereum provider");
        handler = Plaid.create({
            env: "sandbox", token: "link-sandbox-fabricated",
            onSuccess: (...args) => successes.push(args),
            onExit: (...args) => exits.push(args),
        }, {forceDesktop: true, web3ValidChains: ["eip155:1"]});
        handler.open();
        frame = frameFor();
        await take(frame, "configure");
        await take(frame, "open");
        await emit(frame, "web3-message", {message: "START_BRIDGE"});
        await emit(frame, "web3-message", {message: "REQUEST_PLUGIN_DATA"});
        pluginReceipt(await take(frame, "web3-message"));
        check(scripts.length === 5
            && new Set(scripts.map(event => event.url)).size === 5
            && scripts.every(event => event.type === "load"),
            "all five genuine companions load and register once");
        await emit(frame, "web3-message", {message: "START_BRIDGE"});
        await emit(frame, "web3-message", {message: "REQUEST_PLUGIN_DATA"});
        pluginReceipt(await take(frame, "web3-message"));
        check(scripts.length === 5 && failures.length === 0,
            "repeated start reuses successful initialisation without rejection");
        check(successes.length === 0 && exits.length === 0,
            "plugin discovery does not complete or cancel Link");
    } finally {
        handler?.destroy();
        document.removeEventListener("load", resource, true);
        document.removeEventListener("error", resource, true);
        window.removeEventListener("unhandledrejection", rejection);
        window.removeEventListener("message", record);
        document.body.style.cssText = bodyStyle;
        for (const script of document.querySelectorAll("script[src]")) {
            if (urls.includes(script.src)) script.remove();
        }
    }
    check(frame && !frame.isConnected, "destroy removes the owned Link iframe");
    console.log("test successful");
})().catch(error => console.error(error.stack));
""",
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        responses = []
        while not self._companion_responses.empty():
            responses.append(self._companion_responses.get())
        self.assertEqual(
            sorted(urlparse(url).path for url, *_rest in responses),
            sorted(f"/link/2.0.1951/{name}" for name in WEB3_COMPANIONS),
        )
        for url, code, content_type, content in responses:
            name = Path(urlparse(url).path).name
            self.assertEqual(code, 200)
            self.assertEqual(content_type, "application/javascript; charset=utf-8")
            self.assertEqual(content, self._genuine_companions[name])

    def test_sync_button_links_the_selected_account(self):
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
                return_value=SimpleNamespace(
                    to_dict=lambda: {"link_token": "link-sandbox-fabricated"}
                ),
            ) as link,
            patch(
                "plaid.api.plaid_api.PlaidApi.item_public_token_exchange",
                return_value={"access_token": "access-sandbox-fabricated"},
            ) as exchange,
        ):
            self.browser_js(
                f"/odoo/action-{action.id}/{provider.id}",
                f"const providerId = {provider.id};\n"
                + BROWSER_HARNESS
                + r"""
(async () => {
    try {
        document.querySelector(
            ".o_form_view button[name='action_sync_with_plaid']"
        ).click();
        const frameDeadline = performance.now() + 5000;
        while (!document.querySelector("iframe[id^='plaid-link-iframe-']")
            && performance.now() < frameDeadline) {
            await new Promise((resolve) => setTimeout(resolve, 10));
        }
        const frame = frameFor();
        const configured = (await take(frame, "configure")).message.config;
        await take(frame, "open");
        check(configured.token === "link-sandbox-fabricated", "button link token");
        await emit(frame, "connected", {metadata: {
            public_token: "public-sandbox-fabricated",
            accounts: [{id: "fabricated-ui-account", name: "Fixture account"}],
        }});
        let saved;
        const deadline = performance.now() + 10000;
        while (performance.now() < deadline) {
            const response = await fetch("/web/dataset/call_kw", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    jsonrpc: "2.0", method: "call", id: 1,
                    params: {
                        model: "online.bank.statement.provider", method: "read",
                        args: [
                            [providerId], ["plaid_access_token", "plaid_account_id"],
                        ],
                        kwargs: {},
                    },
                }),
            });
            check(response.ok, "provider read response");
            const reply = await response.json();
            check(!reply.error, JSON.stringify(reply.error));
            [saved] = reply.result;
            if (saved.plaid_access_token === "access-sandbox-fabricated"
                && saved.plaid_account_id === "fabricated-ui-account") break;
            await new Promise((resolve) => setTimeout(resolve, 25));
        }
        check(saved?.plaid_access_token === "access-sandbox-fabricated"
            && saved?.plaid_account_id === "fabricated-ui-account",
            "real ORM callback must persist the selected account and token");
    } finally {
        window.removeEventListener("message", record);
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
                ready="""typeof Plaid !== 'undefined' && document.querySelector(
                    ".o_form_view button[name='action_sync_with_plaid']"
                ) !== null""",
                login="admin",
                timeout=90,
            )
            link.assert_called_once()
            exchange.assert_called_once()
            self.assertEqual(
                exchange.call_args.args[0].public_token, "public-sandbox-fabricated"
            )
        provider.invalidate_recordset(["plaid_access_token", "plaid_account_id"])
        self.assertEqual(provider.plaid_access_token, "access-sandbox-fabricated")
        self.assertEqual(provider.plaid_account_id, "fabricated-ui-account")
        self.assertFalse(self._fixture_requests.empty())

    def test_script_tag_integration_submits_the_original_form(self):
        self.browser_js(
            "https://plaid-form.invalid/form.html",
            r"""
(async () => {
    const form = document.getElementById("plaid-form");
    const submitted = document.querySelector("iframe[name='plaid-form-submission']");
    const button = document.getElementById("plaid-link-button");
    check(button.form === form && button.textContent === "Link your bank account",
        "SDK creates the public-token button inside the original form");
    const initialDeadline = performance.now() + 5000;
    while ((!submitted.contentWindow.location.search.includes("initial=1")
        || submitted.contentDocument.readyState !== "complete")
        && performance.now() < initialDeadline) {
        await new Promise((resolve) => setTimeout(resolve, 10));
    }
    check(submitted.contentWindow.location.search === "?initial=1"
        && submitted.contentDocument.readyState === "complete", "initial receipt page");
    const frame = frameFor();
    const configured = (await take(frame, "configure")).message.config;
    for (const [key, value] of Object.entries({
        env: "sandbox", token: "public-sandbox-00000000-0000-0000-0000-000000000001",
        clientName: "Fabricated form integration", product: "auth",
        selectAccount: true, webhook: "https://fixture.invalid/webhook",
        isSimpleIntegration: true,
    })) check(configured[key] === value, "script attribute: " + key);
    button.disabled = true;
    await emit(frame, "acknowledged");
    check(button.disabled === false, "acknowledgement enables the button");
    button.click();
    await take(frame, "open");
    check(frame.style.display === "block", "button opens the real Link frame");
    await emit(frame, "connected", {metadata: {
        public_token: "public-sandbox-fabricated",
        institution: {id: "fixture-bank", name: "Fixture Bank"},
        accounts: [{id: "fixture-account", name: "Fixture Account"}],
    }});
    const expected = {
        public_token: "public-sandbox-fabricated",
        "institution[id]": "fixture-bank", "institution[name]": "Fixture Bank",
        "accounts[0][id]": "fixture-account", "accounts[0][name]": "Fixture Account",
    };
    const fields = [...form.querySelectorAll("input[type='hidden']")];
    check(fields.length === Object.keys(expected).length,
        "exact hidden-field inventory");
    for (const [name, value] of Object.entries(expected)) {
        const matches = fields.filter(input => input.name === name);
        check(matches.length === 1 && matches[0].value === value,
            "hidden field: " + name);
    }
    const deadline = performance.now() + 5000;
    while ((!submitted.contentWindow.location.search.includes("public_token=")
        || submitted.contentDocument.readyState !== "complete")
        && performance.now() < deadline) {
        await new Promise((resolve) => setTimeout(resolve, 10));
    }
    check(submitted.contentDocument.readyState === "complete",
        "submitted receipt loaded");
    const parameters = new URL(submitted.contentWindow.location.href).searchParams;
    check([...parameters].length === Object.keys(expected).length,
        "exact submitted inventory");
    for (const [name, value] of Object.entries(expected)) {
        check(parameters.getAll(name).length === 1 && parameters.get(name) === value,
            "real form submission: " + name);
    }
    check(frame.style.display === "none", "success hides the Link frame");
    check(location.href === "https://plaid-form.invalid/form.html",
        "submission keeps the original page alive");
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready=(
                "window.plaidFormReady === true && typeof Plaid !== 'undefined'"
                " && typeof Plaid.create === 'function'"
                " && document.getElementById('plaid-link-button') !== null"
            ),
            login="admin",
            timeout=90,
        )
        requests = []
        while not self._fixture_requests.empty():
            requests.append(urlparse(self._fixture_requests.get()))
        form_requests = [
            request for request in requests if request.hostname == "plaid-form.invalid"
        ]
        self.assertEqual(
            sum(request.path == "/link-initialize.js" for request in form_requests), 1
        )
        self.assertEqual(
            sum(
                request.path == "/submission.html" and "public_token=" in request.query
                for request in form_requests
            ),
            1,
        )

    def test_real_desktop_link_lifecycle_and_callback_payloads(self):
        self.browser_js(
            "/web",
            BROWSER_HARNESS
            + r"""
(async () => {
    let handler;
    const bodyStyle = document.body.style.cssText;
    const originalWarn = console.warn, warnings = [];
    console.warn = (...args) => warnings.push(args);
    const focus = document.createElement("button");
    focus.textContent = "Return focus here";
    document.body.appendChild(focus);
    focus.focus();
    const successes = [], exits = [], events = [], results = [];
    let loads = 0;
    try {
        for (const options of [{token: "fixture"}, {onSuccess() {}}]) {
            let refused = false;
            try { Plaid.create(options); } catch { refused = true; }
            check(refused, "incomplete create options must be refused");
        }
        handler = Plaid.create({
            env: "sandbox", token: "link-sandbox-fabricated",
            forceIframe: false,
            onSuccess: (...args) => successes.push(args),
            onExit: (...args) => exits.push(args),
            onEvent: (...args) => events.push(args),
            onResult: (result) => results.push(result),
            onLoad: () => { loads += 1; },
        });
        check(warnings.some(([message]) => message ===
            "The forceIframe option has been deprecated. " +
            "Link will use an iframe by default when possible."),
            "deprecated iframe option reports its public warning");
        const frame = frameFor();
        check(frame.style.display === "none", "initially hidden");
        handler.open();
        const configured = (await take(frame, "configure")).message.config;
        await take(frame, "open");
        check(configured.token === "link-sandbox-fabricated", "configured token");
        check(configured.isUsingOnEventCallback === true, "event callback contract");
        check(configured.isUsingOnResultCallback === true, "result callback contract");
        check(loads === 1 && document.body.style.overflow === "hidden", "open state");
        const incremental = [
            {status: "pending", accounts: []},
            {status: "available", accounts: [{id: "fabricated-account"}]},
        ];
        for (const result of incremental) {
            await emit(frame, "result", {incremental_result: result});
        }
        check(JSON.stringify(results) === JSON.stringify(incremental),
            "incremental results arrive unchanged and in order");
        check(successes.length === 0 && exits.length === 0
            && frame.style.display === "block", "results do not complete the link");
        await emit(frame, "connected", {metadata: {public_token: "wrong-instance"}},
            {instance: "not-this-instance"});
        await emit(frame, "unused", {}, {kind: "raw", value: "{malformed"});
        check(successes.length === 0, "invalid messages must not invoke success");
        handler.submit({accounts: ["fabricated-account"]});
        const submitted = (await take(frame, "submit")).message.data;
        check(submitted.accounts[0] === "fabricated-account", "submit payload");
        await emit(frame, "event", {
            eventName: "SELECT_INSTITUTION", metadata: {view_name: "CONSENT"},
        });
        check(events.length === 1 && events[0][0] === "SELECT_INSTITUTION"
            && events[0][1].view_name === "CONSENT", "event callback payload");
        const metadata = {
            public_token: "public-sandbox-fabricated",
            accounts: [{id: "fabricated-account", name: "Fixture bank account"}],
        };
        await emit(frame, "connected", {metadata});
        check(successes.length === 1
            && successes[0][0] === metadata.public_token
            && successes[0][1].accounts[0].id === "fabricated-account",
            "success payload");
        check(frame.style.display === "none" && document.activeElement === focus,
            "success hides iframe and restores focus");
        handler.open();
        await take(frame, "open");
        let refused = false;
        try { handler.exit("invalid"); } catch { refused = true; }
        check(refused, "invalid exit options must be refused");
        handler.exit({force: true});
        check((await take(frame, "exit")).message.config.force === true,
            "exit request");
        await emit(frame, "exit", {error: null, metadata: {status: "cancelled"}});
        check(exits.length === 1 && exits[0][0] === null
            && exits[0][1].status === "cancelled", "exit callback payload");
        handler.destroy();
        check(!frame.isConnected, "destroy removes iframe");
        refused = false;
        try { handler.open(); } catch (error) {
            refused = error.message.includes("already destroyed");
        }
        check(refused, "destroyed handler cannot reopen");
    } finally {
        if (handler) handler.destroy();
        console.warn = originalWarn;
        window.removeEventListener("message", record);
        document.body.style.cssText = bodyStyle;
        focus.remove();
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

    def test_flow_callbacks_preserve_payloads_and_suppress_exit_after_success(self):
        self.browser_js(
            "/web",
            BROWSER_HARNESS
            + r"""
(async () => {
    let handler;
    const bodyStyle = document.body.style.cssText;
    const previousFocus = document.activeElement;
    const successes = [], exits = [], events = [];
    try {
        handler = Plaid.create({
            env: "sandbox", token: "link-sandbox-fabricated",
            onSuccess: (...args) => successes.push(args),
            onExit: (...args) => exits.push(args),
            onEvent: (...args) => events.push(args),
        });
        const frame = frameFor();
        handler.open();
        const instance = (await take(frame, "configure")).message.config.uniqueId;
        check(typeof instance === "string" && instance.length > 0,
            "owned configure supplies the instance");
        await take(frame, "open");
        const eventMetadata = {institution_id: "fixture-institution"};
        await emit(frame, "flow-event", {}, {kind: "raw", value: JSON.stringify({
            action: "plaid_flow-" + instance + "::event",
            event_name: "SELECT_INSTITUTION", metadata: eventMetadata,
        })});
        check(JSON.stringify(events) === JSON.stringify([
            ["SELECT_INSTITUTION", eventMetadata],
        ]), "Flow event preserves its name and metadata");
        const successMetadata = {status: "completed"};
        await emit(frame, "flow-success", {}, {kind: "raw", value: JSON.stringify({
            action: "plaid_flow-" + instance + "::success", metadata: successMetadata,
        })});
        check(JSON.stringify(successes) === JSON.stringify([["", successMetadata]]),
            "Flow success preserves metadata and supplies an empty token");
        check(frame.style.display === "block", "Flow success awaits the exit message");
        await emit(frame, "flow-exit", {}, {kind: "raw", value: JSON.stringify({
            action: "plaid_flow-" + instance + "::exit",
            error: null, metadata: successMetadata,
        })});
        check(exits.length === 0 && frame.style.display === "none",
            "exit after Flow success hides the frame without reporting cancellation");
        handler.destroy();
        handler = null;

        handler = Plaid.create({
            env: "sandbox", token: "link-sandbox-fabricated-cancel",
            onSuccess: (...args) => successes.push(args),
            onExit: (...args) => exits.push(args),
        });
        const cancelled = frameFor();
        handler.open();
        const cancelledConfig = (await take(cancelled, "configure")).message.config;
        const cancelledId = cancelledConfig.uniqueId;
        await take(cancelled, "open");
        const error = {error_code: "FIXTURE_CANCELLED"};
        const metadata = {status: "cancelled"};
        await emit(cancelled, "flow-exit", {}, {kind: "raw", value: JSON.stringify({
            action: "plaid_flow-" + cancelledId + "::exit", error, metadata,
        })});
        check(JSON.stringify(exits) === JSON.stringify([[error, metadata]]),
            "Flow cancellation preserves error and metadata");
        check(successes.length === 1 && cancelled.style.display === "none",
            "cancellation does not report success and hides its frame");
    } finally {
        if (handler) handler.destroy();
        window.removeEventListener("message", record);
        document.body.style.cssText = bodyStyle;
        if (previousFocus?.isConnected) previousFocus.focus();
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

    def test_embedded_component_variants_reach_the_owned_frame(self):
        self.browser_js(
            "/web",
            BROWSER_HARNESS
            + r"""
(async () => {
    let handler;
    const bodyStyle = document.body.style.cssText;
    const previousFocus = document.activeElement;
    const originalWarn = console.warn, warnings = [];
    console.warn = (...args) => warnings.push(args);
    const container = document.createElement("section");
    const sibling = document.createElement("p");
    sibling.textContent = "Unrelated content";
    document.body.append(container, sibling);
    try {
        for (const [type, key, unsupportedOption = false] of [
            ["button", "button_component_configuration"],
            ["mini_card", "mini_card_component_configuration"],
            ["chip", "chip_component_configuration"],
            [undefined, null],
            ["fabricated-unsupported", null],
            ["button", "button_component_configuration", true],
        ]) {
            const placeholder = document.createElement("p");
            placeholder.textContent = "Embedded Link placeholder";
            container.appendChild(placeholder);
            const options = {
                env: "sandbox", token: "link-sandbox-fabricated", onSuccess() {},
            };
            if (type !== undefined) options.embeddedComponentConfiguration = {type};
            if (unsupportedOption) options.fixtureUnsupportedOption = true;
            handler = Plaid.createEmbedded(options, container);
            if (unsupportedOption) {
                check(warnings.some(([message]) => message ===
                    "Invalid Link parameter: fixtureUnsupportedOption " +
                    "is not a valid Plaid.create() parameter"),
                    "unknown embedded option reports its public warning");
            }
            const embedded = container.querySelector(
                "iframe[id^='plaid-embedded-link-iframe-']"
            );
            check(embedded !== null, "owned embedded iframe for " + type);
            const configured = (await take(embedded, "configure")).message.config;
            await take(embedded, "open");
            check(configured.token === "link-sandbox-fabricated", "embedded token");
            if (key) {
                check(JSON.stringify(configured.embeddedComponentConfiguration) ===
                    JSON.stringify({[key]: {}}), "component configuration for " + type);
            } else {
                check(!Object.hasOwn(configured, "embeddedComponentConfiguration"),
                    "default and unsupported types omit component configuration");
            }
            check(container.children.length === 1 && !placeholder.isConnected,
                "embedding replaces only the supplied container's children");
            check(sibling.isConnected && sibling.textContent === "Unrelated content",
                "embedding preserves its sibling");
            handler.destroy();
            handler = null;
            check(!embedded.isConnected && container.isConnected
                && container.children.length === 0 && sibling.isConnected,
                "destroy preserves the host and sibling for " + type);
        }
    } finally {
        if (handler) handler.destroy();
        console.warn = originalWarn;
        window.removeEventListener("message", record);
        document.body.style.cssText = bodyStyle;
        container.remove();
        sibling.remove();
        if (previousFocus?.isConnected) previousFocus.focus();
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready=(
                "typeof Plaid !== 'undefined'"
                " && typeof Plaid.createEmbedded === 'function'"
            ),
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

    def test_reopening_link_reconfigures_the_selected_institution(self):
        self.browser_js(
            "/web",
            BROWSER_HARNESS
            + r"""
(async () => {
    let handler;
    const bodyStyle = document.body.style.cssText;
    const previousFocus = document.activeElement;
    const focus = document.createElement("button");
    focus.textContent = "Return after institution selection";
    document.body.appendChild(focus);
    focus.focus();
    const successes = [], exits = [];
    let loads = 0;
    let ready;
    const initiallyReady = new Promise((resolve) => { ready = resolve; });
    try {
        handler = Plaid.create({
            env: "sandbox", token: "link-sandbox-fabricated",
            onSuccess: (...args) => successes.push(args),
            onExit: (...args) => exits.push(args),
            onLoad: () => { loads += 1; ready(); },
        }, {forceDesktop: true});
        const frame = frameFor();
        const initialConfig = (await take(frame, "configure")).message.config;
        check(initialConfig.token === "link-sandbox-fabricated",
            "initial configuration preserves the Link token");
        await initiallyReady;
        for (const [institution, reload, expectedLoads] of [
            ["ins_109508", true, 2],
            ["ins_109508", false, 2],
            ["ins_109509", true, 3],
        ]) {
            console.log("Reopening institution", institution, "after loads", loads);
            handler.open(institution);
            if (reload) {
                const config = (await take(frame, "configure")).message.config;
                check(config.institution === institution,
                    "reloaded peer receives the selected institution");
                check(config.token === "link-sandbox-fabricated",
                    "reconfiguration preserves the Link token");
            }
            const opened = (await take(frame, "open")).message;
            check(opened.institution === institution,
                "each open request carries the selected institution");
            check(loads === expectedLoads, "same institution reuses the loaded peer");
            check(frameFor() === frame && frame.style.display === "block",
                "institution changes retain the owned visible iframe");
            await emit(frame, "exit", {error: null, metadata: {institution}});
            check(frame.style.display === "none" && document.activeElement === focus,
                "each cancellation restores the page focus");
        }
        check(receipts.filter((item) => item.source === frame.contentWindow
            && item.kind === "boot").length === 3,
            "initial load and both institution reloads use the fabricated peer");
        check(successes.length === 0 && exits.length === 3,
            "reopening reports only the three peer cancellations");
        check(exits.every(([error]) => error === null) &&
            exits.map(([, metadata]) => metadata.institution).join(",") ===
            "ins_109508,ins_109508,ins_109509", "cancellation metadata is preserved");
        handler.destroy();
        handler = null;
        check(!frame.isConnected, "destroy removes the reconfigured iframe");
    } finally {
        if (handler) handler.destroy();
        window.removeEventListener("message", record);
        document.body.style.cssText = bodyStyle;
        focus.remove();
        if (previousFocus?.isConnected) previousFocus.focus();
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

    def test_mobile_exit_restores_the_original_document_height(self):
        self.browser_js(
            "/web",
            BROWSER_HARNESS
            + r"""
(async () => {
    let handler;
    const root = document.documentElement;
    const originalId = root.id, originalStyle = root.style.cssText;
    const previousFocus = document.activeElement;
    const focus = document.createElement("button");
    focus.textContent = "Return after mobile Link";
    document.body.appendChild(focus);
    focus.focus();
    try {
        root.id = "plaid-fixture-original-root";
        const styles = [["321px", "important"], ["456px", ""], ["", ""]];
        for (const [height, priority] of styles) {
            root.style.setProperty("height", height, priority);
            handler = Plaid.create({
                env: "sandbox", token: "link-sandbox-fabricated", onSuccess() {},
            }, {forceMobile: true});
            const unopenedFrame = frameFor();
            handler.destroy();
            handler = null;
            check(!unopenedFrame.isConnected, "destroy removes unopened iframe");
            check(root.id === "plaid-fixture-original-root"
                && root.style.getPropertyValue("height") === height
                && root.style.getPropertyPriority("height") === priority,
                "destroy before open preserves document layout");

            const exits = [];
            let ready;
            const initiallyReady = new Promise((resolve) => { ready = resolve; });
            handler = Plaid.create({
                env: "sandbox", token: "link-sandbox-fabricated", onSuccess() {},
                onExit: (...args) => exits.push(args), onLoad: () => ready(),
            }, {forceMobile: true});
            const frame = frameFor();
            await take(frame, "configure");
            await initiallyReady;
            for (const institution of ["ins_109508", "ins_109509"]) {
                handler.open(institution);
                const config = (await take(frame, "configure")).message.config;
                check(config.institution === institution
                    && config.token === "link-sandbox-fabricated",
                    "mobile reload preserves the institution and token");
                check((await take(frame, "open")).message.institution === institution,
                    "mobile open receives the selected institution");
                check(frameFor() === frame && frame.style.display === "block",
                    "mobile reload retains the owned visible iframe");
            }
            await emit(frame, "resize", {height: "777px"});
            check(root.style.getPropertyValue("height") === "777px", "mobile resize");
            handler.exit({force: true});
            check((await take(frame, "exit")).message.config.force === true,
                "public mobile exit sends its options to the owned peer");
            await emit(frame, "exit", {error: null, metadata: {status: "cancelled"}});
            check(exits.length === 1 && exits[0][0] === null
                && exits[0][1].status === "cancelled"
                && document.activeElement === focus,
                "public mobile exit restores focus and preserves the callback payload");
            check(root.id === "plaid-fixture-original-root",
                "restore original root id");
            check(root.style.getPropertyValue("height") === height
                && root.style.getPropertyPriority("height") === priority,
                "mobile exit must restore the original height and priority");
            check(document.getElementById("plaid-link-stylesheet") === null,
                "mobile exit removes temporary stylesheet");
            root.style.setProperty("height", "654px");
            handler.destroy();
            handler = null;
            check(!frame.isConnected, "destroy removes closed iframe");
            check(root.style.getPropertyValue("height") === "654px",
                "destroy after exit preserves subsequent document layout");
        }
    } finally {
        if (handler) handler.destroy();
        root.id = originalId;
        root.style.cssText = originalStyle;
        focus.remove();
        if (previousFocus?.isConnected) previousFocus.focus();
        window.removeEventListener("message", record);
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

    def test_injected_provider_detection_does_not_request_wallet_access(self):
        self.browser_js(
            "/web",
            BROWSER_HARNESS
            + r"""
(async () => {
    let handler;
    const names = ["ethereum", "solana", "coinbaseWalletExtension", "bitkeep"];
    const descriptors = names.map((name) =>
        Object.getOwnPropertyDescriptor(window, name));
    const agentDescriptor = Object.getOwnPropertyDescriptor(navigator, "userAgent");
    const desktopAgent = navigator.userAgent;
    const mobileAgent = "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Mobile";
    let requests = 0;
    const provider = (flags = {}) => ({
        ...flags,
        request() { requests += 1; throw new Error("wallet request forbidden"); },
        enable() { requests += 1; throw new Error("wallet enable forbidden"); },
        send() { requests += 1; throw new Error("wallet send forbidden"); },
    });
    const metamask = provider({isMetaMask: true});
    const coinbase = provider({isCoinbaseWallet: true});
    const rabby = provider({isMetaMask: true, isRabby: true});
    const unknown = provider();
    const cases = [
        {name: "absent", expected: []},
        {name: "desktop metamask", ethereum: metamask, expected: ["wallet_347"]},
        {name: "unknown desktop", ethereum: unknown, expected: ["wallet_381"]},
        {name: "named provider", coinbaseWalletExtension: coinbase,
            expected: ["wallet_374"]},
        {name: "nested provider", bitkeep: {ethereum: provider()},
            expected: ["wallet_354"]},
        {name: "deduplicated providers", ethereum: {providers: [
            metamask, metamask, coinbase, unknown, rabby,
        ]}, expected: ["wallet_347", "wallet_374"]},
        {name: "solana", chain: "solana:mainnet", ethereum: metamask,
            solana: provider({isPhantom: true}), expected: ["wallet_420"]},
        {name: "unsupported chain", chain: "unsupported:fixture", ethereum: metamask,
            expected: []},
        {name: "hex chain", chain: "0x1", ethereum: metamask,
            expected: ["wallet_347"]},
        {name: "unqualified unknown chain", chain: "fixture", ethereum: metamask,
            expected: []},
        {name: "mobile metamask", mobile: true, ethereum: metamask,
            expected: ["wallet_358"]},
        {name: "unknown mobile", mobile: true, ethereum: unknown,
            expected: ["wallet_380"]},
    ];
    try {
        for (const fixture of cases) {
            for (const name of names) {
                Object.defineProperty(window, name, {
                    configurable: true, value: fixture[name],
                });
            }
            Object.defineProperty(navigator, "userAgent", {
                configurable: true, value: fixture.mobile ? mobileAgent : desktopAgent,
            });
            handler = Plaid.create({
                env: "sandbox", token: "link-sandbox-fabricated", onSuccess() {},
            }, {web3ValidChains: [fixture.chain || "eip155:1"]});
            const frame = frameFor();
            const config = (await take(frame, "configure")).message.config;
            check(JSON.stringify([...config.detectedWeb3WalletIds].sort())
                === JSON.stringify([...fixture.expected].sort()),
                `${fixture.name}: detected provider IDs must survive configuration`);
            check(requests === 0, "detection must not request wallet access");
            handler.destroy();
            handler = null;
            check(!frame.isConnected, "each detection handler releases its iframe");
        }
    } finally {
        if (handler) handler.destroy();
        names.forEach((name, index) => {
            if (descriptors[index])
                Object.defineProperty(window, name, descriptors[index]);
            else delete window[name];
        });
        if (agentDescriptor)
            Object.defineProperty(navigator, "userAgent", agentDescriptor);
        else delete navigator.userAgent;
        window.removeEventListener("message", record);
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

    def test_ios_chrome_exit_and_destroy_restore_the_original_body_height(self):
        self.browser_js(
            "/web",
            BROWSER_HARNESS
            + r"""
(async () => {
    let handler;
    const body = document.body, root = document.documentElement;
    const originalBodyStyle = body.style.cssText;
    const originalRootStyle = root.style.cssText;
    const originalId = root.id;
    const agentDescriptor = Object.getOwnPropertyDescriptor(navigator, "userAgent");
    try {
        Object.defineProperty(navigator, "userAgent", {
            configurable: true,
            value: "Mozilla/5.0 (iPhone) AppleWebKit/605.1.15 "
                + "CriOS/120.0 Mobile Safari/604.1",
        });
        for (const close of ["exit", "destroy"]) {
            for (const [height, priority] of [
                ["321px", "important"], ["456px", ""], ["", ""],
            ]) {
                body.style.setProperty("height", height, priority);
                root.id = "plaid-fixture-ios-root";
                handler = Plaid.create({
                    env: "sandbox", token: "link-sandbox-fabricated", onSuccess() {},
                });
                const frame = frameFor();
                handler.open();
                await take(frame, "open");
                const deadline = performance.now() + 2000;
                while (body.style.getPropertyValue("height")
                    !== `${window.innerHeight}px`
                    && performance.now() < deadline) {
                    await new Promise((resolve) => setTimeout(resolve, 10));
                }
                check(body.style.getPropertyValue("height") ===
                    `${window.innerHeight}px`
                    && body.style.getPropertyPriority("height") === "important",
                    "iOS Chrome applies its temporary body height");
                if (close === "exit") {
                    await emit(frame, "exit", {
                        error: null, metadata: {status: "cancelled"},
                    });
                } else {
                    handler.destroy();
                    handler = null;
                }
                check(body.style.getPropertyValue("height") === height
                    && body.style.getPropertyPriority("height") === priority,
                    `${close} must restore the original body height and priority`);
                check(root.id === "plaid-fixture-ios-root"
                    && root.style.cssText === originalRootStyle,
                    "closing iOS Chrome Link restores the document root");
                check(document.getElementById("plaid-link-stylesheet") === null,
                    "closing iOS Chrome Link releases its stylesheet");
                body.style.setProperty("height", "654px");
                if (handler) handler.destroy();
                handler = null;
                check(!frame.isConnected &&
                    body.style.getPropertyValue("height") === "654px",
                    "destroying a closed handler preserves subsequent page layout");
            }
        }
    } finally {
        if (handler) handler.destroy();
        body.style.cssText = originalBodyStyle;
        root.style.cssText = originalRootStyle;
        root.id = originalId;
        if (agentDescriptor)
            Object.defineProperty(navigator, "userAgent", agentDescriptor);
        else delete navigator.userAgent;
        window.removeEventListener("message", record);
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

    def test_ios_chrome_destroy_cancels_pending_body_resize(self):
        self.browser_js(
            "/web",
            BROWSER_HARNESS
            + r"""
(async () => {
    let handler;
    const body = document.body, root = document.documentElement;
    const originalBodyStyle = body.style.cssText;
    const originalRootStyle = root.style.cssText;
    const originalId = root.id;
    const agentDescriptor = Object.getOwnPropertyDescriptor(navigator, "userAgent");
    try {
        Object.defineProperty(navigator, "userAgent", {
            configurable: true,
            value: "Mozilla/5.0 (iPhone) AppleWebKit/605.1.15 "
                + "CriOS/120.0 Mobile Safari/604.1",
        });
        body.style.setProperty("height", "321px", "important");
        handler = Plaid.create({
            env: "sandbox", token: "link-sandbox-fabricated", onSuccess() {},
        });
        const frame = frameFor();
        await take(frame, "configure");
        handler.open();
        handler.destroy();
        handler = null;
        body.style.setProperty("height", "654px");
        await new Promise((resolve) => setTimeout(resolve, 150));
        check(!frame.isConnected, "destroy releases an opened iframe");
        check(body.style.getPropertyValue("height") === "654px"
            && body.style.getPropertyPriority("height") === "",
            "a pending iOS Chrome resize must not change the page after destroy");
        check(root.id === originalId && root.style.cssText === originalRootStyle,
            "destroy restores the document root before a pending resize");
        check(document.getElementById("plaid-link-stylesheet") === null,
            "destroy releases the temporary stylesheet");
    } finally {
        if (handler) handler.destroy();
        body.style.cssText = originalBodyStyle;
        root.style.cssText = originalRootStyle;
        root.id = originalId;
        if (agentDescriptor)
            Object.defineProperty(navigator, "userAgent", agentDescriptor);
        else delete navigator.userAgent;
        window.removeEventListener("message", record);
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

    def test_another_link_frame_cannot_invoke_the_owned_callbacks(self):
        self.browser_js(
            "/web",
            BROWSER_HARNESS
            + r"""
(async () => {
    const bodyStyle = document.body.style.cssText;
    const rootStyle = document.documentElement.style.cssText;
    const rootId = document.documentElement.id;
    let victim, other;
    try {
        for (const forceMobile of [false, true]) {
            const successes = [], exits = [], otherCallbacks = [];
            victim = Plaid.create({
                env: "sandbox", token: "link-sandbox-fabricated",
                onSuccess: (...args) => successes.push(args),
                onExit: (...args) => exits.push(args),
            }, {forceMobile});
            const ownedFrame = frameFor();
            await take(ownedFrame, "configure");
            other = Plaid.create({
                env: "sandbox", token: "link-sandbox-other-fixture",
                onSuccess: (...args) => otherCallbacks.push(args),
                onExit: (...args) => otherCallbacks.push(args),
            }, {forceMobile});
            const otherFrame = [...document.querySelectorAll(
                "iframe[id^='plaid-link-iframe-']"
            )].find((frame) => frame !== ownedFrame);
            check(otherFrame !== undefined, "second real SDK iframe missing");
            check(new URL(otherFrame.src).origin === new URL(ownedFrame.src).origin,
                "both native peers have the configured Plaid origin");
            await take(otherFrame, "configure");
            victim.open();
            await take(ownedFrame, "open");
            const instance = new URL(ownedFrame.src).searchParams.get("uniqueId");
            await emit(otherFrame, "connected", {metadata: {
                public_token: "public-sandbox-foreign-fixture", accounts: [],
            }}, {instance});
            await emit(otherFrame, "exit", {
                error: null, metadata: {status: "foreign-frame"},
            }, {instance});
            check(successes.length === 0 && exits.length === 0,
                `another iframe invoked callbacks: ${successes.length} successes, `
                + `${exits.length} exits, mobile=${forceMobile}`);
            check(ownedFrame.style.display === "block" && otherCallbacks.length === 0,
                "foreign messages preserve both instances and the open viewport");
            const metadata = {
                public_token: "public-sandbox-owned-fixture", accounts: [],
            };
            await emit(ownedFrame, "connected", {metadata});
            check(JSON.stringify(successes) === JSON.stringify([
                [metadata.public_token, metadata],
            ]) && ownedFrame.style.display === "none", "owned success is accepted");
            victim.open();
            await take(ownedFrame, "open");
            await emit(ownedFrame, "exit", {
                error: null, metadata: {status: "cancelled"},
            });
            check(JSON.stringify(exits) ===
                JSON.stringify([[null, {status: "cancelled"}]]),
                "owned cancellation is accepted");
            other.destroy();
            other = null;
            victim.destroy();
            victim = null;
        }
    } finally {
        if (other) other.destroy();
        if (victim) victim.destroy();
        document.body.style.cssText = bodyStyle;
        document.documentElement.style.cssText = rootStyle;
        document.documentElement.id = rootId;
        window.removeEventListener("message", record);
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

    def test_link_messages_keep_the_configured_origin_after_frame_navigation(self):
        self.browser_js(
            "/web",
            BROWSER_HARNESS
            + r"""
(async () => {
    let handler;
    const bodyStyle = document.body.style.cssText;
    const rootStyle = document.documentElement.style.cssText;
    const rootId = document.documentElement.id;
    try {
        for (const [forceMobile, hosted] of [
            [false, false], [true, false], [false, true],
        ]) {
            const successes = [], exits = [];
            handler = Plaid.create({
                env: "sandbox", token: "link-sandbox-fabricated",
                ...(hosted ? {hostedLinkVersion: "1.1.0"} : {}),
                onSuccess: (...args) => successes.push(args),
                onExit: (...args) => exits.push(args),
            }, {forceMobile});
            const expectedOrigin = hosted ? "https://secure.plaid.com"
                : "https://cdn.plaid.com";
            const frame = frameFor(expectedOrigin);
            const originalUrl = frame.src, ownedWindow = frame.contentWindow;
            await take(frame, "boot");
            const configured = await take(frame, "configure");
            check(configured.origin === expectedOrigin,
                "configuration uses the configured normal or hosted origin");
            handler.open();
            await take(frame, "open");
            const instance = new URL(originalUrl).searchParams.get("uniqueId");
            frame.src = "https://plaid-peer.invalid/link.html?uniqueId="
                + encodeURIComponent(instance);
            const boot = await take(frame, "boot");
            check(boot.origin === "https://plaid-peer.invalid" &&
                frame.contentWindow === ownedWindow,
                "navigation changes origin while preserving the owned WindowProxy");
            await emit(frame, "connected", {metadata: {
                public_token: "public-sandbox-navigated-fixture", accounts: [],
            }});
            await emit(frame, "exit", {
                error: null, metadata: {status: "foreign-origin"},
            });
            check(successes.length === 0 && exits.length === 0 &&
                frame.style.display === "block",
                "a navigated owner must not change the configured message origin");
            frame.src = originalUrl;
            await take(frame, "boot");
            await take(frame, "configure");
            const metadata = {public_token: "public-sandbox-restored-fixture"};
            await emit(frame, "connected", {metadata});
            check(JSON.stringify(successes) ===
                JSON.stringify([[metadata.public_token, metadata]]) &&
                frame.style.display === "none", "the restored origin is accepted");
            handler.destroy();
            handler = null;
        }
    } finally {
        if (handler) handler.destroy();
        document.body.style.cssText = bodyStyle;
        document.documentElement.style.cssText = rootStyle;
        document.documentElement.id = rootId;
        window.removeEventListener("message", record);
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

    def test_configuration_survives_transport_before_unlinked_cancellation(self):
        self.browser_js(
            "/web",
            BROWSER_HARNESS
            + r"""
(async () => {
    let handler;
    const bodyStyle = document.body.style.cssText;
    const focus = document.createElement("button");
    focus.textContent = "Return after cancellation";
    document.body.appendChild(focus);
    focus.focus();
    const successes = [], exits = [];
    const expected = {
        countryCodes: ["US", "CA"], product: ["transactions", "auth"],
        accountSubtypes: {depository: ["checking", "savings"]},
    };
    function same(actual, value, label) {
        check(JSON.stringify(actual) === JSON.stringify(value), label);
    }
    try {
        handler = Plaid.create({
            ...JSON.parse(JSON.stringify(expected)),
            env: "sandbox", token: "link-sandbox-fabricated",
            onSuccess: (...args) => successes.push(args),
            onExit: (...args) => exits.push(args),
        });
        const frame = frameFor();
        const parameters = new URL(frame.src).searchParams;
        same(parameters.getAll("countryCodes"), expected.countryCodes,
            "iframe URL preserves country order");
        same(parameters.getAll("product"), expected.product,
            "iframe URL preserves product order");
        same(JSON.parse(parameters.get("accountSubtypes")), expected.accountSubtypes,
            "iframe URL preserves account subtypes");
        handler.open();
        const configured = (await take(frame, "configure")).message.config;
        await take(frame, "open");
        for (const [key, value] of Object.entries(expected)) {
            same(configured[key], value, "configure preserves " + key);
        }
        check(successes.length === 0 && exits.length === 0,
            "configuration and opening do not complete a link");
        handler.exit({force: true});
        check((await take(frame, "exit")).message.config.force === true,
            "forced cancellation reaches iframe");
        await emit(frame, "exit", {error: null, metadata: {status: "cancelled"}});
        same(exits, [[null, {status: "cancelled"}]], "cancellation callback payload");
        check(successes.length === 0, "cancellation must not link an account");
        check(frame.style.display === "none" && document.activeElement === focus,
            "cancellation hides iframe and restores focus");
    } finally {
        if (handler) handler.destroy();
        window.removeEventListener("message", record);
        document.body.style.cssText = bodyStyle;
        focus.remove();
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready="typeof Plaid !== 'undefined' && typeof Plaid.create === 'function'",
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

    def test_embedded_link_handoff_replaces_and_destroys_owned_modals(self):
        self.browser_js(
            "/web",
            BROWSER_HARNESS
            + r"""
(async () => {
    let handler, other;
    const bodyStyle = document.body.style.cssText;
    const overflow = document.body.style.overflow;
    const previousFocus = document.activeElement;
    const focus = document.createElement("button");
    focus.textContent = "Return after embedded Link";
    const container = document.createElement("section");
    const placeholder = document.createElement("p");
    placeholder.textContent = "Embedded Link placeholder";
    container.appendChild(placeholder);
    const sibling = document.createElement("p");
    sibling.textContent = "Unrelated content";
    document.body.append(focus, container, sibling);
    focus.focus();
    const successes = [], exits = [];
    try {
        handler = Plaid.createEmbedded({
            env: "sandbox", token: "link-sandbox-fabricated",
            embeddedComponentConfiguration: {type: "institution_select"},
            onSuccess: (...args) => successes.push(args),
            onExit: (...args) => exits.push(args),
        }, container, {forceDarkMode: true});
        const embedded = container.querySelector(
            "iframe[id^='plaid-embedded-link-iframe-']"
        );
        check(embedded !== null, "real embedded SDK iframe missing");
        check(new URL(embedded.src).origin === "https://cdn.plaid.com",
            "embedded iframe origin");
        check(embedded.title === "Plaid Link", "embedded iframe accessible title");
        check(embedded.width === "100%" && embedded.height === "100%",
            "embedded iframe fills its container");
        check(container.children.length === 1 && !placeholder.isConnected,
            "embedded iframe replaces only its container children");
        check(sibling.isConnected && sibling.textContent === "Unrelated content",
            "embedding preserves unrelated content");
        const configured = (await take(embedded, "configure")).message.config;
        await take(embedded, "open");
        for (const key of ["isEmbedded", "isEmbeddedLink", "isLinkInitialize",
            "forceDarkMode"]) {
            check(configured[key] === true, "embedded configure preserves " + key);
        }
        check(JSON.stringify(configured.embeddedComponentConfiguration) ===
            JSON.stringify({institution_select_component_configuration: {}}),
            "embedded component configuration reaches peer");
        check(document.body.style.overflow === overflow &&
            document.activeElement === focus, "embedding alone preserves page state");
        other = Plaid.create({
            env: "sandbox", token: "link-sandbox-other-fixture", onSuccess() {},
        });
        const otherFrame = frameFor();
        await take(otherFrame, "configure");
        await emit(otherFrame, "internal-event", {event: {start_link: {
            link_token_configuration: {
                institution_id: "ins_109508",
                embedded_workflow_session_id: "fabricated-foreign-session",
                embedded_open_link_configuration: {},
            },
        }}}, {instance: new URL(embedded.src).searchParams.get("uniqueId")});
        check(document.querySelectorAll("iframe[id^='plaid-link-iframe-']")
            .length === 1,
            "another iframe must not create an embedded handler's modal");
        check(document.body.style.overflow === overflow &&
            document.activeElement === focus, "foreign handoff preserves page state");
        other.destroy();
        other = null;
        let previousModal;
        for (const [institution, session, fixture] of [
            ["ins_109508", "fabricated-embedded-session-1", "first"],
            ["ins_109509", "fabricated-embedded-session-2", "second"],
        ]) {
            await emit(embedded, "internal-event", {event: {start_link: {
                link_token_configuration: {
                    institution_id: institution, embedded_workflow_session_id: session,
                    embedded_open_link_configuration: {fixture},
                },
            }}});
            const modal = frameFor();
            check(previousModal === undefined || !previousModal.isConnected,
                "a new handoff removes the previously owned modal");
            check(modal !== previousModal, "handoff creates a new modal");
            const config = (await take(modal, "configure")).message.config;
            check(config.embeddedWorkflowSessionId === session,
                "modal configure preserves embedded session");
            check(JSON.stringify(config.embeddedOpenLinkConfiguration) ===
                JSON.stringify({fixture}), "modal configure preserves handoff data");
            const opened = (await take(modal, "open")).message;
            check(opened.institution === institution, "selected modal institution");
            check(modal.style.display === "block" &&
                document.body.style.overflow === "hidden", "handoff opens real modal");
            previousModal = modal;
        }
        check(successes.length === 0 && exits.length === 0,
            "configuration and handoffs do not complete a link");
        handler.destroy();
        handler = null;
        check(!embedded.isConnected && !previousModal.isConnected,
            "destroy removes both embedded and current modal frames");
        check(container.isConnected && container.children.length === 0 &&
            sibling.isConnected && sibling.textContent === "Unrelated content",
            "destroy preserves the host container and unrelated content");
        check(document.body.style.overflow === overflow &&
            document.activeElement === focus, "destroy restores overflow and focus");
        check(successes.length === 0 && exits.length === 0,
            "destroy does not report completion or cancellation");
    } finally {
        if (other) other.destroy();
        if (handler) handler.destroy();
        window.removeEventListener("message", record);
        document.body.style.cssText = bodyStyle;
        container.remove();
        sibling.remove();
        focus.remove();
        if (previousFocus?.isConnected) previousFocus.focus();
    }
    console.log("test successful");
})().catch((error) => console.error(error.stack));
""",
            ready=(
                "typeof Plaid !== 'undefined'"
                " && typeof Plaid.createEmbedded === 'function'"
            ),
            login="admin",
            timeout=90,
        )
        self.assertFalse(self._fixture_requests.empty())

# Native browser coverage

This collector instruments every maintained browser asset listed in `instrument.cjs`, including the Odoo client action that opens Plaid Link. It seeds unexecuted units, binds source bytes and Istanbul AST maps and validates browser counters before producing LCOV. Odoo 18 and 19 retain their own browser teardown.

Python is required by Odoo's import and browser hooks and the coverage.py reporting API; JavaScript is required by the Odoo asset host and Istanbul's AST instrumentation. Dependencies are pinned in package-lock.json.

CI runs the collector regression suites, instruments assets before addon installation, captures live browser/context receipts during oca_run_tests and merges them before the authenticated Codecov upload. Failure to collect or validate a receipt fails the job. Python and JavaScript collector tests also produce coverage for the maintained collector code.

The Plaid action loads Link from Plaid's stable CDN. Its browser tests serve a fixture at that URL and cover loading and retry, concurrent requests, exit and success callbacks, mobile viewport restoration and the selected account write. Backend tests still cover account selection and transaction import. The old polyfill, embedded transport and Web3 tests exercised SDK internals from the removed vendored build. They required companion chunks from that version and no longer match the integration's public API.

The browser uses each addon's ordinary test fixtures and request proxy. The collector neither calls a provider nor supplies credentials. Full source checks and current asset inventory are mandatory.

The Python report retains every tracked addon source, including tests and modules that were never imported. Only literal dictionary addon manifests are metadata; uncollected Python code and external source links fail the report. Collector code is measured separately by its regression suites.

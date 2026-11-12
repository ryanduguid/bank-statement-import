# Copyright 2026 Ryan Duguid
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Lifecycle contracts, independent of an installed Odoo or browser."""

import json
import tempfile
import threading
import unittest
from concurrent.futures import Future
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from odoo_coverage import BINDING, FrameProxy, install


class Browser:
    def __init__(self, major):
        self._handlers = {}
        self.calls = []
        self.closed = False
        self.context_values = {}
        self.sent = []
        self.send_error = None
        self.test_case = SimpleNamespace(fetch_proxy=lambda url: {})
        if major == 19:
            self.cleanup = ExitStack()
            self.cleanup.callback(self.winddown)

    def winddown(self):
        self.calls.append(("winddown", {}))
        self.closed = True

    def stop(self):
        if hasattr(self, "cleanup"):
            self.cleanup.close()
        else:
            self.winddown()

    def _websocket_request(self, method, *, params):
        if self.closed:
            raise AssertionError("CDP called after shutdown")
        self.calls.append((method, params))
        if method == "Runtime.evaluate":
            identity = params.get("uniqueContextId", params.get("contextId"))
            return {"result": {"value": self.context_values[identity]}}
        return {}

    def _websocket_send(self, method, *, params, with_future=False):
        self.sent.append((method, params))
        if with_future:
            future = Future()
            if self.send_error:
                future.set_exception(self.send_error)
            else:
                future.set_result({})
            return future


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        timeout = patch("odoo_coverage.CHILD_SETUP_TIMEOUT", 0, create=True)
        timeout.start()
        self.addCleanup(timeout.stop)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def browser(self, major):
        common = SimpleNamespace(ChromeBrowser=Browser, HOST="127.0.0.1")
        install(common, self.root, major)
        return common.ChromeBrowser(major)

    def records(self):
        return [json.loads(p.read_text()) for p in sorted(self.root.glob("*.json"))]

    def test_declared_fixture_proxy_is_shared_before_lifecycle_cleanup(self):
        class DeclaredFrameProxy(FrameProxy):
            pass

        class FixtureBrowser(Browser):
            def __init__(self, major):
                super().__init__(major)
                self.test_case._fixture_frame_proxy = DeclaredFrameProxy

        for major in (18, 19):
            with self.subTest(major=major):
                common = SimpleNamespace(ChromeBrowser=FixtureBrowser, HOST="127.0.0.1")
                install(common, self.root, major)
                browser = common.ChromeBrowser(major)
                self.assertIs(type(browser._frame_proxy), DeclaredFrameProxy)
                self.assertIs(browser._frame_proxy.browser, browser)
                self.assertEqual(browser._frame_proxy.host, common.HOST)
                self.assertIs(browser._frame_proxy.lock, browser._coverage_lock)
                self.assertEqual(
                    [
                        params["autoAttach"]
                        for method, params in browser.calls
                        if method == "Target.setAutoAttach"
                    ],
                    [True],
                )
                if major == 19:
                    with browser.cleanup:
                        pass
                else:
                    browser.stop()
                detach = browser.calls.index(
                    (
                        "Target.setAutoAttach",
                        {
                            "autoAttach": False,
                            "waitForDebuggerOnStart": False,
                            "flatten": False,
                        },
                    )
                )
                self.assertLess(detach, browser.calls.index(("winddown", {})))

    def test_both_lifecycles_collect_every_live_context_before_shutdown(self):
        for major in (18, 19):
            with self.subTest(major=major):
                browser = self.browser(major)
                for context in (2, 7):
                    browser._handlers["Runtime.executionContextCreated"](
                        {"id": context}
                    )
                    browser.context_values[context] = {
                        f"file-{context}": {"s": {"0": context}}
                    }
                if major == 19:
                    # HttpCase enters ExitStack directly; stop() alone is insufficient.
                    with browser.cleanup:
                        pass
                else:
                    browser.stop()
                before = len(self.records())
                browser.stop()
                self.assertEqual(len(self.records()), before)
                self.assertTrue(browser.closed)
                self.assertEqual(
                    [
                        p[1]["contextId"]
                        for p in browser.calls
                        if p[0] == "Runtime.evaluate"
                    ],
                    [2, 7],
                )

    def test_pagehide_preserves_a_context_that_navigation_later_discards(self):
        browser = self.browser(18)
        browser._handlers["Runtime.executionContextCreated"]({"id": 4})
        browser._handlers["Runtime.bindingCalled"](
            BINDING,
            json.dumps({"old-page.js": {"s": {"0": 1}}}),
            4,
        )
        self.assertFalse(any(call[0] == "Runtime.evaluate" for call in browser.calls))
        browser._handlers["Runtime.executionContextDestroyed"](
            4, executionContextUniqueId="old"
        )
        browser.stop()
        self.assertEqual(self.records()[0]["cdpContext"], 4)
        self.assertEqual(self.records()[0]["coverage"]["old-page.js"]["s"]["0"], 1)

    def test_navigation_without_a_receipt_is_visibly_incomplete(self):
        browser = self.browser(19)
        browser._handlers["Runtime.executionContextCreated"]({"id": 4})
        browser._handlers["Runtime.executionContextsCleared"]()
        with self.assertRaisesRegex(RuntimeError, "without a coverage receipt"):
            browser.stop()
        self.assertTrue(browser.closed)
        self.assertIn("error", self.records()[0])

    def test_destroyed_document_without_a_receipt_is_incomplete(self):
        browser = self.browser(18)
        browser._handlers["Runtime.executionContextCreated"]({"id": 4})
        browser._handlers["Runtime.executionContextDestroyed"](4)
        with self.assertRaisesRegex(RuntimeError, "without a coverage receipt"):
            browser.stop()
        self.assertTrue(browser.closed)

    def test_an_empty_document_receipt_is_complete(self):
        browser = self.browser(19)
        browser._handlers["Runtime.executionContextCreated"]({"id": 4})
        browser._handlers["Runtime.bindingCalled"](BINDING, "{}", 4)
        browser._handlers["Runtime.executionContextsCleared"]()
        browser.stop()
        self.assertEqual(self.records()[0]["coverage"], {})

    def test_reused_numeric_ids_keep_independent_document_counters(self):
        browser = self.browser(18)
        for count in (2, 3):
            browser._handlers["Runtime.executionContextCreated"]({"id": 4})
            browser._handlers["Runtime.bindingCalled"](
                BINDING,
                json.dumps({"file.js": {"s": {"0": count}}}),
                4,
            )
            browser._handlers["Runtime.executionContextDestroyed"](4)
        browser.stop()
        records = self.records()
        self.assertEqual(len({record["context"] for record in records}), 2)
        self.assertEqual([record["cdpContext"] for record in records], [4, 4])

    def test_known_isolated_worlds_do_not_imply_a_lost_document(self):
        browser = self.browser(19)
        browser._handlers["Runtime.executionContextCreated"](
            {"id": 4, "auxData": {"isDefault": False}}
        )
        browser._handlers["Runtime.executionContextDestroyed"](4)
        browser.stop()
        self.assertEqual(self.records(), [])

    def test_collection_uses_renderer_unique_identity_when_available(self):
        browser = self.browser(19)
        browser._handlers["Runtime.executionContextCreated"](
            {"id": 4, "uniqueId": "renderer-2-context-4"}
        )
        browser.context_values["renderer-2-context-4"] = {}
        browser.stop()
        calls = [
            params for method, params in browser.calls if method == "Runtime.evaluate"
        ]
        self.assertEqual(calls[0]["uniqueContextId"], "renderer-2-context-4")
        self.assertNotIn("contextId", calls[0])
        self.assertEqual(self.records()[0]["coverage"], {})

    def test_document_changes_during_collection_are_incomplete(self):
        for major in (18, 19):
            for remove_again in (False, True):
                with self.subTest(major=major, remove_again=remove_again):
                    browser = self.browser(major)
                    browser._handlers["Runtime.executionContextCreated"]({"id": 1})
                    browser.context_values[1] = {}
                    request = browser._websocket_request

                    def create_document(
                        method,
                        *,
                        params,
                        request=request,
                        browser=browser,
                        remove_again=remove_again,
                    ):
                        result = request(method, params=params)
                        if method == "Runtime.evaluate":
                            browser._handlers["Runtime.executionContextCreated"](
                                {"id": 2}
                            )
                            if remove_again:
                                browser._handlers["Runtime.bindingCalled"](
                                    BINDING, "{}", 2
                                )
                                browser._handlers["Runtime.executionContextDestroyed"](
                                    2
                                )
                        return result

                    browser._websocket_request = create_document
                    with self.assertRaisesRegex(
                        RuntimeError, "changed during coverage collection"
                    ):
                        browser.stop()
                    self.assertTrue(browser.closed)
        self.assertEqual(sum("error" in record for record in self.records()), 4)

    def test_in_flight_pagehide_cannot_cross_the_completion_cutoff(self):
        browser = self.browser(18)
        browser._handlers["Runtime.executionContextCreated"]({"id": 1})
        browser.context_values[1] = {}
        started = threading.Event()
        release = threading.Event()
        write = browser._coverage_write
        request = browser._websocket_request
        worker = None

        def delayed_write(context, generation, data):
            if threading.current_thread() is not threading.main_thread():
                started.set()
                if not release.wait(2):
                    raise RuntimeError("Test did not release coverage writer")
            return write(context, generation, data)

        def begin_binding(method, *, params):
            nonlocal worker
            result = request(method, params=params)
            if method == "Runtime.evaluate":
                worker = threading.Thread(
                    target=browser._coverage_binding, args=(BINDING, "{}", 1)
                )
                worker.start()
                self.assertTrue(started.wait(2))
            return result

        browser._coverage_write = delayed_write
        browser._websocket_request = begin_binding
        try:
            with self.assertRaisesRegex(RuntimeError, "still in flight"):
                browser.stop()
        finally:
            release.set()
            if worker is not None:
                worker.join(2)
                self.assertFalse(worker.is_alive())
        self.assertTrue(browser.closed)
        self.assertEqual(sum("error" in record for record in self.records()), 1)

    def test_child_setup_during_collection_cannot_cross_the_completion_cutoff(self):
        for major in (18, 19):
            for enable_acknowledged in (False, True):
                with self.subTest(major=major, enable_acknowledged=enable_acknowledged):
                    browser = self.browser(major)
                    browser._handlers["Runtime.executionContextCreated"]({"id": 1})
                    browser.context_values[1] = {}
                    request = browser._websocket_request

                    def attach_child(
                        method,
                        *,
                        params,
                        browser=browser,
                        request=request,
                        enable_acknowledged=enable_acknowledged,
                    ):
                        result = request(method, params=params)
                        if method == "Runtime.evaluate":
                            browser._handlers["Target.attachedToTarget"](
                                sessionId="late-frame",
                                targetInfo={"type": "iframe"},
                                waitingForDebugger=True,
                            )
                            if enable_acknowledged:
                                message = json.loads(browser.sent[-1][1]["message"])
                                browser._handlers["Target.receivedMessageFromTarget"](
                                    sessionId="late-frame",
                                    message=json.dumps(
                                        {"id": message["id"], "result": {}}
                                    ),
                                )
                        return result

                    browser._websocket_request = attach_child
                    with self.assertRaisesRegex(RuntimeError, "setup did not finish"):
                        browser.stop()
                    self.assertTrue(browser.closed)
        self.assertEqual(sum("error" in record for record in self.records()), 4)

    def worker_acknowledgement_can_finish(self, during_collection):
        browser = self.browser(18)
        browser._handlers["Runtime.executionContextCreated"]({"id": 1})
        browser.context_values[1] = {}
        workers = []

        def attach():
            browser._handlers["Target.attachedToTarget"](
                sessionId="worker",
                targetInfo={"type": "service_worker"},
                waitingForDebugger=True,
            )
            message = json.loads(browser.sent[-1][1]["message"])
            worker = threading.Thread(
                target=browser._handlers["Target.receivedMessageFromTarget"],
                kwargs={
                    "sessionId": "worker",
                    "message": json.dumps({"id": message["id"], "result": {}}),
                },
            )
            workers.append(worker)
            worker.start()

        request = browser._websocket_request

        def collect(method, *, params):
            result = request(method, params=params)
            if method == "Runtime.evaluate":
                attach()
            return result

        if during_collection:
            browser._websocket_request = collect
        try:
            with patch("odoo_coverage.CHILD_SETUP_TIMEOUT", 2, create=True):
                # The receiver cannot acknowledge until collection releases
                # every level of this shared, reentrant lock.
                with browser._coverage_lock:
                    if not during_collection:
                        attach()
                    browser.stop()
        finally:
            for worker in workers:
                worker.join(2)
                self.assertFalse(worker.is_alive())
        self.assertTrue(browser.closed)
        self.assertEqual(sum("error" in record for record in self.records()), 0)

    def test_in_flight_worker_resume_finishes_before_collection_starts(self):
        self.worker_acknowledgement_can_finish(False)

    def test_in_flight_worker_resume_finishes_before_the_atomic_cutoff(self):
        self.worker_acknowledgement_can_finish(True)

    def test_invalid_binding_fails_on_test_thread_and_still_closes_browser(self):
        for major in (18, 19):
            with self.subTest(major=major):
                browser = self.browser(major)
                browser._handlers["Runtime.bindingCalled"](BINDING, "not JSON", 4)
                with self.assertRaises(json.JSONDecodeError):
                    browser.stop()
                self.assertTrue(browser.closed)
        self.assertEqual(sum("error" in record for record in self.records()), 2)

    def test_unrelated_binding_is_left_alone(self):
        browser = self.browser(18)
        browser._handlers["Runtime.bindingCalled"]("not-coverage", "not JSON", 4)
        browser.stop()
        self.assertEqual(self.records(), [])

    def test_proxy_release_precedes_shutdown_even_when_collection_or_release_fails(
        self,
    ):
        for major in (18, 19):
            for failure in (None, "collection", "release"):
                with self.subTest(major=major, failure=failure):
                    browser = self.browser(major)
                    request = browser._websocket_request
                    if failure == "collection":
                        browser._coverage_fail(RuntimeError("collection failed"))

                    def release_proxy(
                        method, *, params, request=request, failure=failure
                    ):
                        result = request(method, params=params)
                        if (
                            method == "Target.setAutoAttach"
                            and not params["autoAttach"]
                        ):
                            if failure == "release":
                                raise RuntimeError("release failed")
                        return result

                    browser._websocket_request = release_proxy
                    if failure:
                        with self.assertRaisesRegex(RuntimeError, failure + " failed"):
                            browser.stop()
                    else:
                        browser.stop()
                    self.assertTrue(browser.closed)
                    self.assertEqual(
                        browser.calls[-2:],
                        [
                            (
                                "Target.setAutoAttach",
                                {
                                    "autoAttach": False,
                                    "waitForDebuggerOnStart": False,
                                    "flatten": False,
                                },
                            ),
                            ("winddown", {}),
                        ],
                    )

    def test_unrecognised_host_fails_explicitly(self):
        with self.assertRaises(RuntimeError):
            install(SimpleNamespace(ChromeBrowser=Browser), self.root, 20)
        with self.assertRaises(RuntimeError):
            install(SimpleNamespace(ChromeBrowser=object), self.root, 19)

    def test_setup_failure_closes_the_browser_it_created(self):
        instances = []

        class ChangedHost(Browser):
            def __init__(self, major):
                super().__init__(major)
                instances.append(self)
                self._handlers["Runtime.bindingCalled"] = object()

        for major in (18, 19):
            with self.subTest(major=major):
                common = SimpleNamespace(ChromeBrowser=ChangedHost, HOST="127.0.0.1")
                install(common, self.root, major)
                with self.assertRaisesRegex(RuntimeError, "already owns"):
                    common.ChromeBrowser(major)
                self.assertTrue(instances[-1].closed)


class FrameProxyTests(unittest.TestCase):
    def setUp(self):
        timeout = patch("odoo_coverage.CHILD_SETUP_TIMEOUT", 0, create=True)
        timeout.start()
        self.addCleanup(timeout.stop)
        temporary = tempfile.TemporaryDirectory()
        self.temporary = temporary
        self.addCleanup(temporary.cleanup)
        self.common = SimpleNamespace(ChromeBrowser=Browser, HOST="127.0.0.1")
        install(self.common, temporary.name, 18)
        self.browser = self.common.ChromeBrowser(18)
        self.addCleanup(Browser.stop, self.browser)

    def attach(self, session="frame", kind="iframe", waiting=True):
        self.browser._handlers["Target.attachedToTarget"](
            sessionId=session, targetInfo={"type": kind}, waitingForDebugger=waiting
        )

    def messages(self, session="frame"):
        return [
            json.loads(params["message"])
            for method, params in self.browser.sent
            if method == "Target.sendMessageToTarget" and params["sessionId"] == session
        ]

    def receive(self, message, session="frame"):
        self.browser._handlers["Target.receivedMessageFromTarget"](
            sessionId=session, message=json.dumps(message)
        )

    def ready(self, session="frame"):
        self.attach(session)
        self.receive({"id": self.messages(session)[-1]["id"], "result": {}}, session)
        self.receive({"id": self.messages(session)[-1]["id"], "result": {}}, session)

    def pause(self, url, session="frame"):
        self.receive(
            {
                "method": "Fetch.requestPaused",
                "params": {"requestId": "same-request", "request": {"url": url}},
            },
            session,
        )

    def test_fetch_is_enabled_before_the_child_runs(self):
        self.attach()
        self.assertEqual([m["method"] for m in self.messages()], ["Fetch.enable"])
        self.receive({"id": self.messages()[-1]["id"], "result": {}})
        self.assertEqual(
            self.messages()[-1]["method"], "Runtime.runIfWaitingForDebugger"
        )
        self.assertFalse(self.browser._coverage_contexts)

    def test_native_default_filter_keeps_related_workers_resumable(self):
        auto_attach = [
            params
            for method, params in self.browser.calls
            if method == "Target.setAutoAttach"
        ]
        self.assertEqual(len(auto_attach), 1)
        self.assertTrue(auto_attach[0]["waitForDebuggerOnStart"])
        self.assertNotIn("filter", auto_attach[0])

    def test_auxiliary_targets_resume_without_request_interception(self):
        for kind in (
            "worker",
            "service_worker",
            "shared_worker",
            "auction_worklet",
            "shared_storage_worklet",
            "future_auxiliary_type",
        ):
            with self.subTest(kind=kind):
                self.attach(kind, kind=kind)
                messages = self.messages(kind)
                self.assertEqual(
                    [m["method"] for m in messages], ["Runtime.runIfWaitingForDebugger"]
                )
                self.receive({"id": messages[0]["id"], "result": {}}, kind)
        self.browser.stop()
        self.assertTrue(self.browser.closed)

    def test_running_auxiliary_target_needs_no_commands_until_detachment(self):
        self.attach("worker", kind="service_worker", waiting=False)
        self.assertEqual(self.messages("worker"), [])
        self.assertIn("worker", self.browser._frame_proxy.sessions)
        self.browser._frame_proxy.verify()
        self.browser._handlers["Target.detachedFromTarget"](sessionId="worker")
        self.assertNotIn("worker", self.browser._frame_proxy.sessions)
        self.browser.stop()
        self.assertTrue(self.browser.closed)

    def test_worker_resume_acknowledgement_is_required_at_collection_cutoff(self):
        self.attach("worker", kind="service_worker")
        with self.assertRaisesRegex(RuntimeError, "setup did not finish"):
            self.browser.stop()
        self.assertTrue(self.browser.closed)

    def test_worker_resume_error_is_reported_and_browser_still_closes(self):
        self.attach("worker", kind="service_worker")
        messages = self.messages("worker")
        self.assertEqual(len(messages), 1)
        self.receive(
            {"id": messages[0]["id"], "error": {"message": "worker resume refused"}},
            "worker",
        )
        with self.assertRaisesRegex(RuntimeError, "worker resume refused"):
            self.browser.stop()
        self.assertTrue(self.browser.closed)

    def test_external_response_uses_the_existing_callback_in_the_same_session(self):
        self.ready()
        response = {"responseCode": 200, "body": "cGVlcg==", "responseHeaders": []}
        requests = []

        def proxy(url):
            requests.append(url)
            return response

        self.browser.test_case.fetch_proxy = proxy
        self.pause("https://cdn.plaid.com/link/v2/stable/link.html")
        message = self.messages()[-1]
        self.assertEqual(message["method"], "Fetch.fulfillRequest")
        self.assertEqual(message["params"], {"requestId": "same-request", **response})
        self.assertEqual(requests, ["https://cdn.plaid.com/link/v2/stable/link.html"])
        self.assertEqual(
            response, {"responseCode": 200, "body": "cGVlcg==", "responseHeaders": []}
        )

    def test_local_requests_continue_and_host_lookalikes_use_the_proxy(self):
        self.ready()
        requests = []
        self.browser.test_case.fetch_proxy = lambda url: requests.append(url) or {}
        self.pause("http://127.0.0.1:8069/web")
        self.assertEqual(self.messages()[-1]["method"], "Fetch.continueRequest")
        self.assertEqual(requests, [])
        self.pause("http://127.0.0.1.example.invalid/remote")
        self.assertEqual(self.messages()[-1]["method"], "Fetch.fulfillRequest")
        self.assertEqual(requests, ["http://127.0.0.1.example.invalid/remote"])

    def test_two_children_can_reuse_request_ids_without_crossed_responses(self):
        self.browser.test_case.fetch_proxy = lambda url: {
            "responseCode": 200,
            "body": url,
        }
        for session in ("left", "right"):
            self.ready(session)
            url = f"https://fixture.invalid/{session}"
            self.pause(url, session)
            self.assertEqual(
                self.messages(session)[-1]["params"],
                {"requestId": "same-request", "responseCode": 200, "body": url},
            )

    def test_enable_error_releases_the_target_and_fails_on_the_test_thread(self):
        self.attach()
        self.receive(
            {"id": self.messages()[-1]["id"], "error": {"message": "unsupported"}}
        )
        self.assertIn(
            ("Target.detachFromTarget", {"sessionId": "frame"}), self.browser.sent
        )
        with self.assertRaisesRegex(RuntimeError, "unsupported"):
            self.browser.stop()
        self.assertTrue(self.browser.closed)

    def test_outer_transport_error_releases_the_target_and_still_closes(self):
        self.browser.send_error = RuntimeError("transport failed")
        self.attach()
        self.assertIn(
            ("Target.detachFromTarget", {"sessionId": "frame"}), self.browser.sent
        )
        with self.assertRaisesRegex(RuntimeError, "transport failed"):
            self.browser.stop()
        self.assertTrue(self.browser.closed)

    def test_detached_target_cancels_setup_and_ignores_late_acknowledgements(self):
        self.attach()
        identity = self.messages()[-1]["id"]
        self.browser._handlers["Target.detachedFromTarget"](sessionId="frame")
        self.receive({"id": identity, "result": {}})
        self.assertEqual([m["method"] for m in self.messages()], ["Fetch.enable"])
        self.browser.stop()
        self.assertTrue(self.browser.closed)

    def test_missing_child_acknowledgement_is_not_silently_accepted(self):
        self.attach()
        with self.assertRaisesRegex(RuntimeError, "setup did not finish"):
            self.browser.stop()
        self.assertTrue(self.browser.closed)

    def test_root_request_handler_stays_owned_by_odoo(self):
        root = object()
        self.browser._handlers["Fetch.requestPaused"] = root
        self.ready()
        self.assertIs(self.browser._handlers["Fetch.requestPaused"], root)

    def test_proxy_release_does_not_block_receiver_detachment(self):
        self.ready()
        request = self.browser._websocket_request
        workers = []

        def release_proxy(method, *, params):
            if method == "Target.setAutoAttach" and not params["autoAttach"]:
                worker = threading.Thread(
                    target=self.browser._handlers["Target.detachedFromTarget"],
                    kwargs={"sessionId": "frame"},
                )
                workers.append(worker)
                worker.start()
                worker.join(2)
                self.assertFalse(worker.is_alive(), "Proxy lock blocks CDP receiver")
            return request(method, params=params)

        self.browser._websocket_request = release_proxy
        try:
            self.browser.stop()
        finally:
            for worker in workers:
                worker.join(2)
                self.assertFalse(worker.is_alive())
        self.assertFalse(self.browser._frame_proxy.sessions)
        self.assertTrue(self.browser.closed)

    def test_fixture_callback_failure_is_visible_and_releases_its_target(self):
        self.ready()

        def unavailable(url):
            raise RuntimeError("fixture unavailable")

        self.browser.test_case.fetch_proxy = unavailable
        self.pause("https://fixture.invalid/peer")
        self.assertIn(
            ("Target.detachFromTarget", {"sessionId": "frame"}), self.browser.sent
        )
        with self.assertRaisesRegex(RuntimeError, "fixture unavailable"):
            self.browser.stop()
        self.assertTrue(self.browser.closed)

    def test_unsupported_auto_attachment_closes_the_browser_it_created(self):
        instances = []

        class ChangedHost(Browser):
            def __init__(self, major):
                super().__init__(major)
                instances.append(self)

            def _websocket_request(self, method, *, params):
                if method == "Target.setAutoAttach":
                    raise RuntimeError("unsupported auto-attachment")
                return super()._websocket_request(method, params=params)

        for major in (18, 19):
            common = SimpleNamespace(ChromeBrowser=ChangedHost, HOST="127.0.0.1")
            install(common, self.temporary.name, major)
            with self.assertRaisesRegex(RuntimeError, "unsupported auto-attachment"):
                common.ChromeBrowser(major)
            self.assertTrue(instances[-1].closed)


if __name__ == "__main__":
    unittest.main()

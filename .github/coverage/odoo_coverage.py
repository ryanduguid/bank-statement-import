# Copyright 2026 Ryan Duguid
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Collect native, AST-instrumented Odoo assets before their browser disappears.

This Python hook is required by Odoo's Python HttpCase host. Odoo owns the
browser lifecycle and fixture responses; production addons stay unchanged.
"""

import json
import os
import threading
import uuid
from concurrent.futures import InvalidStateError
from pathlib import Path
from urllib.parse import urlsplit

BINDING = "__oca_native_coverage_report"
CHILD_SETUP_TIMEOUT = 10
ON_DOCUMENT = """(() => {
  addEventListener('pagehide', () => {
    globalThis.__oca_native_coverage_report(
      JSON.stringify(globalThis.__coverage__ || {}));
  }, {capture: true});
})();"""


class FrameProxy:
    """Route direct child iframe requests through Odoo's existing fixture proxy."""

    def __init__(self, browser, host, report_error, lock):
        self.browser = browser
        self.host = host
        self.report_error = report_error
        self.sessions = {}
        self.sequence = 0
        self.lock = lock
        self.condition = threading.Condition(lock)
        self.closed = False
        handlers = {
            "Target.attachedToTarget": self.attached,
            "Target.receivedMessageFromTarget": self.received,
            "Target.detachedFromTarget": self.detached,
        }
        if any(name in browser._handlers for name in handlers):
            raise RuntimeError("Odoo already owns child target events")
        if not callable(getattr(browser, "_websocket_send", None)):
            raise RuntimeError("Odoo child target CDP contract changed")
        browser._handlers.update(handlers)
        # Odoo's receiver drops flattened session envelopes. Use the native
        # message bridge until that host exposes session-aware dispatch.
        # Chrome 139 pauses workers before evaluating a target filter. Its
        # default admits related targets so every paused worker can be resumed.
        browser._websocket_request(
            "Target.setAutoAttach",
            params={
                "autoAttach": True,
                "waitForDebuggerOnStart": True,
                "flatten": False,
            },
        )

    def failed(self, error, session):
        with self.lock:
            self.report_error(error)
            attached = self.sessions.pop(session, None) is not None
            self.condition.notify_all()
        if attached:
            try:
                self.browser._websocket_send(
                    "Target.detachFromTarget", params={"sessionId": session}
                )
            except Exception:
                # The original browser teardown still closes every target.
                pass

    def command(self, session, method, params, acknowledged=None):
        with self.lock:
            if session not in self.sessions:
                return
            self.sequence += 1
            identity = self.sequence
            self.sessions[session][identity] = (method, acknowledged)
        message = json.dumps({"id": identity, "method": method, "params": params})
        try:
            future = self.browser._websocket_send(
                "Target.sendMessageToTarget",
                params={"sessionId": session, "message": message},
                with_future=True,
            )
            if future is None:
                raise RuntimeError("Child target CDP transport closed")
            future.add_done_callback(lambda result: self.sent(session, result))
        except Exception as error:
            self.failed(error, session)

    def sent(self, session, future):
        with self.lock:
            if session not in self.sessions:
                return
            try:
                future.result()
            except Exception as error:
                self.failed(error, session)

    def attached(self, sessionId, targetInfo, waitingForDebugger, **_unused):
        def resume_if_waiting():
            if waitingForDebugger:
                self.command(sessionId, "Runtime.runIfWaitingForDebugger", {})

        with self.lock:
            if sessionId in self.sessions:
                self.failed(RuntimeError("Child target session reused"), sessionId)
                return
            self.sessions[sessionId] = {}
            if targetInfo.get("type") == "iframe":
                self.command(
                    sessionId,
                    "Fetch.enable",
                    {"patterns": [{"urlPattern": "*"}]},
                    resume_if_waiting,
                )
            else:
                resume_if_waiting()

    def received(self, sessionId, message, **_unused):
        with self.lock:
            if sessionId not in self.sessions:
                return
            try:
                data = json.loads(message)
                if "id" in data:
                    pending = self.sessions.get(sessionId)
                    method, acknowledged = pending.pop(data["id"])
                    if "error" in data:
                        raise RuntimeError(f"Child {method}: {data['error']}")
                    if acknowledged:
                        acknowledged()
                    self.condition.notify_all()
                elif data.get("method") == "Fetch.requestPaused":
                    self.request(sessionId, data["params"])
            except Exception as error:
                self.failed(error, sessionId)

    def request(self, session, params):
        url = params["request"]["url"]
        parsed = urlsplit(url)
        if parsed.scheme == "http" and parsed.hostname == self.host:
            method, response = "Fetch.continueRequest", {}
        else:
            method = "Fetch.fulfillRequest"
            response = self.browser.test_case.fetch_proxy(url)
        self.command(session, method, {"requestId": params["requestId"], **response})

    def detached(self, sessionId, **_unused):
        # Closing an iframe may cancel its in-flight requests normally.
        with self.lock:
            self.sessions.pop(sessionId, None)
            self.condition.notify_all()

    def setup_pending(self):
        return any(
            method in ("Fetch.enable", "Runtime.runIfWaitingForDebugger")
            for pending in self.sessions.values()
            for method, _callback in pending.values()
        )

    def wait(self):
        with self.condition:
            if not self.condition.wait_for(
                lambda: not self.setup_pending(), timeout=CHILD_SETUP_TIMEOUT
            ):
                raise RuntimeError("Child fixture proxy setup did not finish")

    def verify(self):
        with self.lock:
            incomplete = self.setup_pending()
        if incomplete:
            raise RuntimeError("Child fixture proxy setup did not finish")

    def close(self):
        with self.lock:
            if self.closed:
                return
            self.closed = True
        # Release paused targets before Odoo unregisters service workers.
        # The receiver must remain free to handle detachments and the reply.
        self.browser._websocket_request(
            "Target.setAutoAttach",
            params={
                "autoAttach": False,
                "waitForDebuggerOnStart": False,
                "flatten": False,
            },
        )


class CoverageBrowserMixin:
    """Collect live documents before the native browser lifecycle closes them."""

    def __init__(self, *args, **kwargs):
        self._coverage_browser = uuid.uuid4().hex
        self._coverage_contexts = {}
        self._coverage_generation = 0
        self._coverage_revision = 0
        self._coverage_pending = 0
        self._coverage_done = False
        # Child setup acknowledgements may enqueue the next asynchronous
        # command whilst holding the same lock as the collection cutoff.
        self._coverage_lock = threading.RLock()
        self._coverage_collected = False
        self._coverage_error = None
        self._coverage_sequence = 0
        super().__init__(*args, **kwargs)
        try:
            self._coverage_setup()
        except BaseException:
            super().stop()
            raise

    def _coverage_setup(self):
        if any(
            name in self._handlers
            for name in (
                "Runtime.bindingCalled",
                "Runtime.executionContextCreated",
                "Runtime.executionContextDestroyed",
                "Runtime.executionContextsCleared",
            )
        ):
            raise RuntimeError("Odoo already owns the coverage CDP event")
        self._handlers.update(
            {
                "Runtime.bindingCalled": self._coverage_binding,
                "Runtime.executionContextCreated": self._coverage_created,
                "Runtime.executionContextDestroyed": self._coverage_destroyed,
                "Runtime.executionContextsCleared": self._coverage_cleared,
            }
        )
        self._websocket_request("Runtime.addBinding", params={"name": BINDING})
        self._websocket_request(
            "Page.addScriptToEvaluateOnNewDocument", params={"source": ON_DOCUMENT}
        )
        proxy_class = getattr(self.test_case, "_fixture_frame_proxy", FrameProxy)
        self._frame_proxy = proxy_class(
            self, self._coverage_host, self._coverage_fail, self._coverage_lock
        )
        if self._coverage_major == 19:
            if not callable(getattr(self.cleanup, "callback", None)):
                raise RuntimeError("Odoo 19 browser cleanup contract changed")
            # ExitStack is LIFO: collect while CDP is live, before winddown.
            self.cleanup.callback(self._coverage_finish)

    def _coverage_fail(self, error):
        with self._coverage_lock:
            if self._coverage_done:
                return
            if self._coverage_error is None:
                self._coverage_error = error
        result = getattr(self, "_result", None)
        if result is not None and not result.done():
            try:
                result.set_exception(error)
            except InvalidStateError:
                pass

    def _coverage_created(self, context, **_unused):
        # Page assets execute in default worlds. Known isolated worlds have
        # no injected pagehide listener and must not imply missing assets.
        if context.get("auxData", {}).get("isDefault") is False:
            return
        with self._coverage_lock:
            if self._coverage_done:
                return
            if context["id"] in self._coverage_contexts:
                self._coverage_discard(context["id"])
            self._coverage_generation += 1
            self._coverage_revision += 1
            self._coverage_contexts[context["id"]] = {
                "generation": self._coverage_generation,
                "received": False,
                "uniqueId": context.get("uniqueId"),
            }

    def _coverage_discard(self, context):
        if self._coverage_done:
            return
        state = self._coverage_contexts.pop(context, None)
        if state is not None:
            self._coverage_revision += 1
        if state is not None and not state["received"]:
            self._coverage_error = RuntimeError(
                f"Document context {context} disappeared without a coverage receipt"
            )

    def _coverage_destroyed(self, executionContextId, **_unused):
        with self._coverage_lock:
            self._coverage_discard(executionContextId)

    def _coverage_cleared(self, **_unused):
        with self._coverage_lock:
            for context in list(self._coverage_contexts):
                self._coverage_discard(context)

    def _coverage_write(self, context, generation, data):
        if not isinstance(data, dict):
            raise RuntimeError("Browser coverage is not an object")
        with self._coverage_lock:
            self._coverage_sequence += 1
            sequence = self._coverage_sequence
        record = {
            "browser": self._coverage_browser,
            "context": generation,
            "cdpContext": context,
            "coverage": data,
        }
        target = (
            self._coverage_destination / f"{self._coverage_browser}-{sequence:06d}.json"
        )
        with target.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, ensure_ascii=True)

    def _coverage_binding(self, name, payload, executionContextId):
        if name != BINDING:
            return
        with self._coverage_lock:
            if self._coverage_done:
                return
            self._coverage_pending += 1
        try:
            if len(payload) > 32 * 1024 * 1024:
                raise RuntimeError("Browser coverage exceeds 32 MiB")
            data = json.loads(payload)
            with self._coverage_lock:
                state = self._coverage_contexts.get(executionContextId)
                if state is None:
                    raise RuntimeError("Coverage arrived from an untracked document")
                generation = state["generation"]
            self._coverage_write(executionContextId, generation, data)
            with self._coverage_lock:
                state["received"] = True
        except Exception as error:
            # Receiver callbacks must not issue synchronous CDP requests.
            # Odoo may log callback exceptions; surface this on test thread.
            with self._coverage_lock:
                self._coverage_error = error
        finally:
            with self._coverage_lock:
                self._coverage_pending -= 1

    def _coverage_collect(self):
        if self._coverage_collected:
            return
        self._coverage_collected = True
        try:
            with self._coverage_lock:
                self._frame_proxy.wait()
                self._frame_proxy.verify()
                contexts = sorted(self._coverage_contexts.items())
                revision = self._coverage_revision
            for context, state in contexts:
                identity = (
                    {"uniqueContextId": state["uniqueId"]}
                    if state["uniqueId"]
                    else {"contextId": context}
                )
                result = self._websocket_request(
                    "Runtime.evaluate",
                    params={
                        "expression": "globalThis.__coverage__ || {}",
                        **identity,
                        "returnByValue": True,
                    },
                )
                if not result or "exceptionDetails" in result:
                    raise RuntimeError("Native browser coverage evaluation failed")
                with self._coverage_lock:
                    if self._coverage_contexts.get(context) is not state:
                        raise RuntimeError(
                            "Document changed during coverage collection"
                        )
                self._coverage_write(
                    context, state["generation"], result["result"]["value"]
                )
            with self._coverage_lock:
                self._frame_proxy.wait()
                self._frame_proxy.verify()
                if self._coverage_revision != revision:
                    raise RuntimeError("Documents changed during coverage collection")
                if self._coverage_pending:
                    raise RuntimeError(
                        "Coverage receipt still in flight at collection cutoff"
                    )
                if self._coverage_error is not None:
                    raise self._coverage_error
                # Atomic cutoff before Odoo's ordinary browser teardown.
                self._coverage_done = True
        except Exception as error:
            with self._coverage_lock:
                self._coverage_done = True
            target = self._coverage_destination / f"{self._coverage_browser}-error.json"
            target.write_text(json.dumps({"error": str(error)}), encoding="utf-8")
            raise

    def _coverage_finish(self):
        try:
            self._coverage_collect()
        finally:
            self._frame_proxy.close()

    def stop(self):
        if self._coverage_major == 18:
            try:
                self._coverage_finish()
            finally:
                super().stop()
        else:
            super().stop()


def install(common, destination, major):
    """Patch the exact imported common module after its ordinary loader runs."""
    if major not in (18, 19):
        raise RuntimeError("Unsupported native Odoo browser lifecycle")
    original = common.ChromeBrowser
    if not callable(getattr(original, "_websocket_request", None)):
        raise RuntimeError("Odoo browser CDP contract changed")
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / f"installed-{os.getpid()}-odoo{major}.txt").write_text(
        f"Native Odoo {major} browser coverage hook installed\n",
        encoding="utf-8",
    )

    class CoverageBrowser(CoverageBrowserMixin, original):
        _coverage_destination = destination
        _coverage_major = major
        _coverage_host = common.HOST

    common.ChromeBrowser = CoverageBrowser

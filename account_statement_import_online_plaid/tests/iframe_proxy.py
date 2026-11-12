# Copyright 2026 Ryan Duguid
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""Keep fabricated iframe responses local after Chrome process changes."""

import json
import threading
from concurrent.futures import InvalidStateError
from urllib.parse import urlsplit

CHILD_SETUP_TIMEOUT = 10


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


def fixture_browser(original, host):
    """Add fixture routing for child iframe processes to one HttpCase browser."""

    class FixtureBrowser(original):
        def __init__(self, *args, **kwargs):
            self._owned_fixture_proxy = None
            self._fixture_proxy_error = None
            super().__init__(*args, **kwargs)
            try:
                inherited = getattr(self, "_frame_proxy", None)
                if inherited is not None:
                    # A coverage browser may already own this shared proxy.
                    # Keep its collection and teardown with that owner.
                    if not isinstance(inherited, FrameProxy):
                        raise RuntimeError("Incompatible child fixture proxy owner")
                else:
                    self._owned_fixture_proxy = FrameProxy(
                        self, host, self._fixture_proxy_failed, threading.RLock()
                    )
            except BaseException:
                super().stop()
                raise

        def _fixture_proxy_failed(self, error):
            if self._fixture_proxy_error is None:
                self._fixture_proxy_error = error
            result = getattr(self, "_result", None)
            if result is not None and not result.done():
                try:
                    result.set_exception(error)
                except InvalidStateError:
                    pass

        def stop(self):
            proxy = self._owned_fixture_proxy
            try:
                if proxy is not None:
                    proxy.wait()
                    proxy.verify()
                    if self._fixture_proxy_error is not None:
                        raise self._fixture_proxy_error
            finally:
                try:
                    if proxy is not None:
                        proxy.close()
                finally:
                    super().stop()

    return FixtureBrowser

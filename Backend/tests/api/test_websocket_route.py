"""
Direct unit tests for websocket route function using a fake WebSocket.
Exercises missing-token, invalid-token, and happy-path branches without a real server.
"""
from __future__ import annotations

import pytest


class FakeWS:
    def __init__(self):
        self.accepted = False
        self.closed = False
        self.close_code = None
        self.close_reason = None
        self.sent = []
        self._recv = []

    async def accept(self):
        self.accepted = True

    async def close(self, code: int, reason: str = ""):
        self.closed = True
        self.close_code = code
        self.close_reason = reason

    async def receive_json(self):
        if not self._recv:
            # Simulate client disconnect after first loop
            from fastapi import WebSocketDisconnect
            raise WebSocketDisconnect
        return self._recv.pop(0)

    async def send_json(self, data):
        self.sent.append(data)


@pytest.mark.asyncio
async def test_ws_missing_token_closes(monkeypatch):
        from api.routes.websocket import websocket_endpoint
        ws = FakeWS()
        await websocket_endpoint(ws, token=None)
        assert ws.closed is True
        assert ws.close_code == 1008
        assert "Missing" in (ws.close_reason or "")


@pytest.mark.asyncio
async def test_ws_invalid_token_closes(monkeypatch):
    from api.routes import websocket as wsmod
    import core.dependencies as deps

    class BadAuth:
        def verify_token(self, token: str):
            raise ValueError("bad token")

    monkeypatch.setattr(deps, "get_auth_service", lambda: BadAuth())

    ws = FakeWS()
    await wsmod.websocket_endpoint(ws, token="nope")
    assert ws.closed is True
    # Errors inside the endpoint are mapped to 1011 Server error
    assert ws.close_code == 1011


@pytest.mark.asyncio
async def test_ws_success_connect_and_disconnect(monkeypatch):
    from api.routes import websocket as wsmod
    import core.dependencies as deps

    class GoodAuth:
        def verify_token(self, token: str):
            return {"user_id": "u42"}

    events = {"connected": False, "disconnected": False}

    async def fake_connect(ws, user_id):
        events["connected"] = True

    async def fake_handle_message(ws, data):
        # Immediately simulate disconnect by raising the same exception
        from fastapi import WebSocketDisconnect
        raise WebSocketDisconnect

    def fake_disconnect(ws):
        events["disconnected"] = True

    monkeypatch.setattr(deps, "get_auth_service", lambda: GoodAuth())
    monkeypatch.setattr(wsmod.manager, "connect", fake_connect)
    monkeypatch.setattr(wsmod.manager, "handle_message", fake_handle_message)
    monkeypatch.setattr(wsmod.manager, "disconnect", fake_disconnect)

    ws = FakeWS()
    await wsmod.websocket_endpoint(ws, token="ok")
    # Our fake connect does not call accept; just ensure lifecycle hooks ran
    assert events["connected"] is True
    assert events["disconnected"] is True


@pytest.mark.asyncio
async def test_ws_status_route(monkeypatch):
    from api.routes import websocket as wsmod

    class WS(FakeWS):
        async def receive_text(self):
            from fastapi import WebSocketDisconnect
            # trigger a single receive then disconnect
            raise WebSocketDisconnect

    ws = WS()
    await wsmod.websocket_status(ws)
    # Accepted was called
    assert ws.accepted is True
    # First send should be a status message
    assert ws.sent and ws.sent[0].get("type") == "status"

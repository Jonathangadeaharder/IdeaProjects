"""
Tests for core.dependencies authentication helpers: get_current_user and WS variant.
"""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from core import dependencies as deps
from services.authservice.auth_service import SessionExpiredError
from database.models import User


class FakeAuthOK:
    def __init__(self):
        self.user = User(
            id=1,
            username="ok",
            is_superuser=False,
            is_active=True,
            created_at="",
            last_login="",
            native_language="en",
            target_language="de",
        )

    def validate_session(self, token: str):
        return self.user


class FakeAuthExpired:
    def validate_session(self, token: str):
        raise SessionExpiredError("expired")


class FakeAuthInvalid:
    def validate_session(self, token: str):
        raise ValueError("invalid")


def _cred(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


@pytest.mark.asyncio
async def test_get_current_user_success(monkeypatch):
    user = await deps.get_current_user(_cred("t"), FakeAuthOK())
    assert user.username == "ok"


@pytest.mark.asyncio
async def test_get_current_user_expired(monkeypatch):
    with pytest.raises(HTTPException) as exc:
        await deps.get_current_user(_cred("t"), FakeAuthExpired())
    assert exc.value.status_code == 401
    assert "expired" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_get_current_user_invalid(monkeypatch):
    with pytest.raises(HTTPException) as exc:
        await deps.get_current_user(_cred("t"), FakeAuthInvalid())
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_ws(monkeypatch):
    monkeypatch.setattr(deps, "get_auth_service", lambda: FakeAuthOK())
    user = await deps.get_current_user_ws("token")
    assert user.username == "ok"

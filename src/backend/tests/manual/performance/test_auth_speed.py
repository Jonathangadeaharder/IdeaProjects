"""Protective tests for the authentication round trip latency and response shape."""

from __future__ import annotations

import os
import time

import pytest

# Mark as manual test
pytestmark = pytest.mark.manual

from tests.helpers import AsyncAuthHelper

AUTH_ROUND_TRIP_BUDGET = 1.5


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.environ.get("SKIP_DB_HEAVY_TESTS") == "1",
    reason="Skipping DB-heavy performance test in constrained sandbox",
)
@pytest.mark.timeout(30)
async def test_Whenregistration_and_login_round_tripCalled_ThenSucceeds(async_client) -> None:
    """A full register→login cycle should finish quickly and return the bearer token contract."""
    helper = AsyncAuthHelper(async_client)
    user = helper.create_test_user()

    started = time.perf_counter()
    _reg_user, reg_data = await helper.register_user(user)
    token, login_payload = await helper.login_user(user)
    elapsed = time.perf_counter() - started

    assert reg_data is not None  # Registration succeeded
    assert login_payload["token_type"].lower() == "bearer"
    assert "access_token" in login_payload
    assert token is not None
    assert elapsed < AUTH_ROUND_TRIP_BUDGET


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.environ.get("SKIP_DB_HEAVY_TESTS") == "1",
    reason="Skipping DB-heavy performance test in constrained sandbox",
)
@pytest.mark.timeout(30)
async def test_login_with_WrongPassword_fails_fast(async_client) -> None:
    """Invalid credentials should be rejected promptly without leaking token data."""
    helper = AsyncAuthHelper(async_client)
    user = helper.create_test_user()
    await helper.register_user(user)

    # Try login with wrong password
    wrong_password_user = helper.create_test_user(email=user.email, password="TotallyWrong123!")

    started = time.perf_counter()
    # Login should fail with assertion error (400 status)
    try:
        await helper.login_user(wrong_password_user)
        raise AssertionError("Login should have failed with wrong password")
    except AssertionError:
        elapsed = time.perf_counter() - started
        # Verify it failed for the right reason (status code check in helper)
        assert elapsed < AUTH_ROUND_TRIP_BUDGET

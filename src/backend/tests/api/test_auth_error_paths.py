"""Focused auth error-path coverage respecting the CDD/TDD 80/20 rules."""

from __future__ import annotations

import pytest

from tests.assertion_helpers import assert_validation_error_response
from tests.helpers import AsyncAuthHelper


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_WhenRegisterMissingEmail_ThenReturnsvalidation_detail(async_http_client, url_builder):
    """Invalid input: missing email should return FastAPI validation errors."""
    payload = {
        "username": "missing_email",
        "password": "SecureTestPass123!",
    }
    register_url = url_builder.url_for("register:register")

    response = await async_http_client.post(register_url, json=payload)

    assert_validation_error_response(response, "email")


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_WhenLoginbad_credentials_ThenReturnscontract_error(async_http_client, url_builder):
    """Invalid input: wrong password returns user-friendly error message."""
    helper = AsyncAuthHelper(async_http_client)
    user, _data = await helper.register_user()
    login_url = url_builder.url_for("auth:jwt.login")

    response = await async_http_client.post(
        login_url,
        data={"username": user.email, "password": "WrongPass999!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 400
    payload = response.json()
    assert "error" in payload
    # Check for the user-friendly message (translated from LOGIN_BAD_CREDENTIALS)
    assert payload["error"]["message"] == "Invalid email or password"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_WhenLogoutwithout_token_ThenReturnsunauthorized(async_http_client, url_builder):
    """Boundary: logout without Authorization header returns uniform 401 response."""
    logout_url = url_builder.url_for("auth:jwt.logout")
    response = await async_http_client.post(logout_url)

    assert response.status_code == 401
    www_authenticate = response.headers.get("www-authenticate")
    assert www_authenticate is None or "bearer" in www_authenticate.lower()

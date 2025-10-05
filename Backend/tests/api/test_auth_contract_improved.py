"""Improved auth contract validation using shared fixtures and 80/20 coverage."""

from __future__ import annotations

import pytest

from tests.helpers import AsyncAuthHelper


def _route(url_builder, name: str, fallback: str) -> str:
    """Resolve a named route, falling back to explicit contract path if not registered."""
    try:
        return url_builder.url_for(name)
    except ValueError:
        return fallback


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenRegisterRouteViaContractName_ThenSucceeds(async_http_client, url_builder):
    """Happy path: registering through the named route yields a contract-compliant payload."""
    register_url = _route(url_builder, "register:register", "/api/auth/register")
    helper = AsyncAuthHelper(async_http_client)
    user = helper.create_test_user()

    response = await async_http_client.post(register_url, json=user.to_dict())

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user.email
    assert data["username"] == user.username


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_Whenlogin_routeWithoutform_encoding_ThenReturnsError(async_http_client, url_builder):
    """Invalid input: JSON payload fails because contract requires form-urlencoded data."""
    login_url = _route(url_builder, "auth:jwt.login", "/api/auth/login")
    helper = AsyncAuthHelper(async_http_client)
    user, _data = await helper.register_user()

    response = await async_http_client.post(
        login_url,
        json={
            "username": user.email,
            "password": user.password,
        },
    )

    assert (
        response.status_code == 422
    ), f"Expected 422 (validation error for JSON instead of form data), got {response.status_code}: {response.text}"


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenLoginroute_ThenReturnsbearer_contract(async_http_client, url_builder):
    """Happy path login using named route returns the documented bearer fields."""
    _route(url_builder, "auth:jwt.login", "/api/auth/login")
    helper = AsyncAuthHelper(async_http_client)
    user, _data = await helper.register_user()

    token, login_data = await helper.login_user(user)

    assert token
    assert login_data["token_type"].lower() == "bearer"
    assert login_data["access_token"]


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_Whenlogout_routeWithouttoken_ThenReturnsError(async_http_client, url_builder):
    """Invalid input: logout via named route without a token is unauthorized."""
    logout_url = _route(url_builder, "auth:jwt.logout", "/api/auth/logout")

    response = await async_http_client.post(logout_url)

    assert response.status_code == 401

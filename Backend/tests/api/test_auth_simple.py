"""Lightweight auth smoke tests that stay behavior focused and contract aware."""

from __future__ import annotations

import pytest

from tests.assertion_helpers import assert_json_error_response, assert_json_response
from tests.helpers import AsyncAuthHelper


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenRegisterCalled_ThenReturnsJsonResponse(async_http_client, url_builder):
    """Happy path: register responds with JSON payload and 201 status."""
    helper = AsyncAuthHelper(async_http_client)
    user = helper.create_test_user()
    register_url = url_builder.url_for("register:register")

    response = await async_http_client.post(register_url, json=user.to_dict())

    assert response.status_code == 201
    assert_json_response(response)


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenLoginWithWrongPassword_ThenReturnsJsonError(async_http_client, url_builder):
    """Invalid input: wrong password yields JSON error structure."""
    helper = AsyncAuthHelper(async_http_client)
    user, _data = await helper.register_user()
    login_data = {"username": user.email, "password": "WrongPass123!"}
    login_url = url_builder.url_for("auth:jwt.login")

    response = await async_http_client.post(
        login_url, data=login_data, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert_json_error_response(response, 400)


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenMeEndpointCalled_ThenReturnsJsonForBothAuthStates(async_http_client, url_builder):
    """Boundary: /me returns JSON both for unauthorized and authorized calls."""
    me_url = url_builder.url_for("auth_get_current_user")

    unauth_response = await async_http_client.get(me_url)
    assert_json_error_response(unauth_response, 401)

    helper = AsyncAuthHelper(async_http_client)
    _user, token, headers = await helper.create_authenticated_user()
    auth_response = await async_http_client.get(me_url, headers=headers)
    assert auth_response.status_code == 200
    assert_json_response(auth_response)

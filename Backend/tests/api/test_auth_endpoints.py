"""Behavioral auth endpoint tests following the CDD/TDD policy.

Covers the 80/20 protective scenarios for the auth contract:
- Happy path registration + login
- Invalid input rejection
- Boundary protection for duplicate identities and malformed form data
"""

from __future__ import annotations

import pytest

from tests.assertion_helpers import assert_validation_error_response
from tests.helpers import AsyncAuthHelper


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenRegisterCalled_ThenCreatesActiveUser(async_http_client):
    """Happy path: registration returns a contract-compliant user payload."""
    helper = AsyncAuthHelper(async_http_client)
    user, data = await helper.register_user()

    assert data["username"] == user.username
    assert data["email"] == user.email
    assert isinstance(data["id"], int)
    assert data["is_active"] is True
    assert data["is_superuser"] is False


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenRegisterWithMissingEmail_ThenRejects(async_http_client, url_builder):
    """Invalid input: missing email triggers FastAPI validation 422 response."""
    helper = AsyncAuthHelper(async_http_client)
    user = helper.create_test_user()
    payload = {"username": user.username, "password": user.password}
    register_url = url_builder.url_for("register:register")

    response = await async_http_client.post(register_url, json=payload)

    assert_validation_error_response(response, "email")


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenRegisterWithDuplicateUsername_ThenPrevents(async_http_client, url_builder):
    """Boundary: duplicate username surfaces a 400 contract error."""
    helper = AsyncAuthHelper(async_http_client)
    user, _data = await helper.register_user()

    register_url = url_builder.url_for("register:register")
    second_response = await async_http_client.post(register_url, json=user.to_dict())
    assert second_response.status_code == 400


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenLoginCalled_ThenReturnsBearerToken(async_http_client):
    """Happy path login returns bearer token per contract."""
    helper = AsyncAuthHelper(async_http_client)
    user, _data = await helper.register_user()

    token, login_data = await helper.login_user(user)

    assert token
    assert login_data["token_type"].lower() == "bearer"
    assert isinstance(login_data["access_token"], str)
    assert login_data["access_token"]


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenLoginWithWrongPassword_ThenRejects(async_http_client):
    """Invalid input: wrong password returns the standard 400 failure."""
    helper = AsyncAuthHelper(async_http_client)
    user, _data = await helper.register_user()

    # Try login with wrong password - should fail
    login_data = {"username": user.email, "password": "TotallyWrong123!"}
    response = await async_http_client.post("/api/auth/login", data=login_data)

    assert response.status_code == 400


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenloginWithoutform_encoded_payload_ThenReturnsError(async_http_client, url_builder):
    """Boundary: JSON payload is rejected to guard contract expectations."""
    helper = AsyncAuthHelper(async_http_client)
    user, _data = await helper.register_user()
    login_url = url_builder.url_for("auth:jwt.login")

    response = await async_http_client.post(
        login_url,
        json={
            "username": user.email,
            "password": user.password,
        },
    )

    # FastAPI-Users expects form-encoded data, so JSON should return 422 validation error
    assert (
        response.status_code == 422
    ), f"Expected 422 (validation error for wrong content type), got {response.status_code}: {response.text}"


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenLogoutCalled_ThenRevokestoken(async_http_client):
    """Happy path logout removes bearer token access."""
    helper = AsyncAuthHelper(async_http_client)
    _user, token, _headers = await helper.create_authenticated_user()

    result = await helper.logout_user(token)

    assert result["success"] is True


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenlogoutWithoutvalid_token_ThenReturnsError(async_http_client, url_builder):
    """Invalid input: logout without a real token yields 401 unauthorized."""
    logout_url = url_builder.url_for("auth:jwt.logout")
    response = await async_http_client.post(logout_url, headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == 401


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenmeCalled_ThenReturnscurrent_user_profile(async_http_client):
    """Happy path query of /me returns the authenticated user contract payload."""
    helper = AsyncAuthHelper(async_http_client)
    user, token, _headers = await helper.create_authenticated_user()

    user_data = await helper.verify_token(token)

    assert user_data["username"] == user.username
    assert user_data["is_active"] is True
    assert user_data["is_superuser"] is False


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenmeWithoutauthentication_ThenReturnsError(async_http_client, url_builder):
    """Invalid input: /me without credentials returns contract 401."""
    me_url = url_builder.url_for("auth_get_current_user")
    response = await async_http_client.get(me_url)

    assert response.status_code == 401

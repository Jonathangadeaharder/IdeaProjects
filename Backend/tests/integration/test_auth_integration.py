"""
Integration tests for authentication flow
"""

import pytest
from httpx import AsyncClient

from tests.helpers import AsyncAuthHelper


class TestAuthenticationIntegration:
    """Integration tests for authentication functionality"""

    @pytest.mark.asyncio
    async def test_health_endpoint_reports_healthy(self, async_client: AsyncClient) -> None:
        response = await async_client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_register_and_login_returns_bearer_token(self, async_client: AsyncClient) -> None:
        helper = AsyncAuthHelper(async_client)
        _user, token, _headers = await helper.create_authenticated_user()

        # Verify token is valid by fetching auth response structure
        assert token
        assert isinstance(token, str)

    @pytest.mark.asyncio
    async def test_authenticated_user_profile_matches_registration(
        self, async_client: AsyncClient, url_builder
    ) -> None:
        helper = AsyncAuthHelper(async_client)
        user, _token, headers = await helper.create_authenticated_user()

        me_url = url_builder.url_for("auth_get_current_user")
        response = await async_client.get(me_url, headers=headers)
        assert response.status_code == 200, f"Token validation failed: {response.text}"

        me_data = response.json()
        assert me_data["email"] == user.email
        assert me_data["is_active"] is True

    @pytest.mark.asyncio
    async def test_login_rejects_username_credentials(self, async_client: AsyncClient, url_builder) -> None:
        login_url = url_builder.url_for("auth:jwt.login")
        response = await async_client.post(
            login_url,
            data={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 400, f"Expected 400 for invalid credentials, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_login_rejects_invalid_password(self, async_client: AsyncClient, url_builder) -> None:
        login_url = url_builder.url_for("auth:jwt.login")
        response = await async_client.post(
            login_url,
            data={"username": "admin@langplug.com", "password": "wrong_password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 400, f"Expected 400 for bad credentials, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_auth_me_requires_valid_token(self, async_client: AsyncClient, url_builder) -> None:
        me_url = url_builder.url_for("auth_get_current_user")
        response = await async_client.get(me_url)
        assert response.status_code == 401

        response = await async_client.get(me_url, headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401

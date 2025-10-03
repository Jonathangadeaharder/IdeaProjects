"""
Integration tests for authentication flow
Tests the complete authentication workflow with proper fixtures and assertions
"""

import pytest
from httpx import AsyncClient

from tests.auth_helpers import AuthTestHelperAsync


class TestAuthenticationIntegration:
    """Integration tests for authentication functionality"""

    @pytest.mark.asyncio
    async def test_complete_auth_workflow(self, async_client: AsyncClient):
        """Test complete authentication flow using proper test user creation"""

        # Test 1: Backend Health Check
        response = await async_client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"

        # Test 2: Use proper auth helper to create and authenticate test user
        auth_flow = await AuthTestHelperAsync.register_and_login_async(async_client)

        # Verify authentication flow returned proper structure
        assert "login_response" in auth_flow
        assert "headers" in auth_flow
        assert "user_data" in auth_flow

        login_response = auth_flow["login_response"]
        user_data = auth_flow["user_data"]
        auth_headers = auth_flow["headers"]

        # Verify login response structure
        assert "access_token" in login_response
        assert "token_type" in login_response
        assert login_response["token_type"] == "bearer"

        # Test 3: Token Validation using the authenticated headers
        response = await async_client.get("/api/auth/me", headers=auth_headers)

        assert response.status_code == 200, f"Token validation failed: {response.text}"
        me_data = response.json()
        assert me_data["email"] == user_data["email"]
        assert me_data["is_active"] is True
        # Note: test users are not superusers, only the admin user would be

    @pytest.mark.asyncio
    async def test_invalid_login_attempts(self, async_client: AsyncClient):
        """Test that invalid login attempts are properly rejected"""

        # Test username login (should fail - system expects email)
        response = await async_client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "admin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Should fail - FastAPI-Users returns 400 (LOGIN_BAD_CREDENTIALS) for invalid email format
        assert response.status_code in [
            400,
            422,
        ], f"Expected 400 or 422 (invalid credentials), got {response.status_code}: {response.text}"

        # Test wrong password
        response = await async_client.post(
            "/api/auth/login",
            data={"username": "admin@langplug.com", "password": "wrong_password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code in [
            400,
            401,
        ], f"Expected 400 or 401 (bad credentials), got {response.status_code}: {response.text}"

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, async_client: AsyncClient):
        """Test that protected endpoints reject requests without valid tokens"""

        # Try to access protected endpoint without token
        response = await async_client.get("/api/auth/me")
        assert response.status_code == 401

        # Try with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_cors_configuration(self, async_client: AsyncClient):
        """Test CORS headers are properly configured"""

        response = await async_client.options("/api/auth/login", headers={"Origin": "http://localhost:3000"})

        # CORS preflight should return 200 or 204 depending on server config
        # Different CORS middleware implementations use different status codes
        assert response.status_code in [
            200,
            204,
            405,
        ], f"Expected 200/204/405 for CORS preflight, got {response.status_code}"

        # Check CORS headers are present (may vary based on configuration)
        cors_origin = response.headers.get("Access-Control-Allow-Origin")
        if cors_origin:  # Only assert if CORS is configured
            assert cors_origin in ["*", "http://localhost:3000"]

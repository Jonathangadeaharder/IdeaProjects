"""
Improved authentication contract tests using proper test infrastructure.
These tests verify that the API contract is maintained with consistent expectations.
"""
import pytest
import uuid


@pytest.mark.asyncio
@pytest.mark.auth
class TestAuthContractImproved:
    """Improved authentication contract tests with proper fixtures."""

    async def test_register_endpoint_contract(self, async_client):
        """Test user registration endpoint contract with proper structure validation."""
        # Generate unique user data
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"testuser_{unique_id}",
            "email": f"testuser_{unique_id}@example.com",
            "password": "SecureTestPass123!"
        }

        response = await async_client.post("/api/auth/register", json=user_data)

        # Validate response structure and status
        assert response.status_code == 201

        response_data = response.json()
        
        # Validate response content
        assert response_data["username"] == user_data["username"]
        assert response_data["email"] == user_data["email"]
        assert isinstance(response_data["id"], str)  # UUID string
        assert response_data["is_active"] is True
        assert response_data["is_superuser"] is False

    async def test_login_endpoint_contract(self, async_client):
        """Test user login endpoint contract with proper database isolation."""
        # Generate unique user data
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"testuser_{unique_id}",
            "email": f"testuser_{unique_id}@example.com",
            "password": "SecureTestPass123!"
        }

        # Register user
        reg_response = await async_client.post("/api/auth/register", json=user_data)
        assert reg_response.status_code == 201

        # Login user (using form data as expected by FastAPI-Users)
        login_data = {
            "username": user_data["email"],  # FastAPI-Users expects email in username field
            "password": user_data["password"]
        }
        login_response = await async_client.post("/api/auth/login", data=login_data)
        
        # Validate login response structure
        assert login_response.status_code == 200
        
        login_data = login_response.json()
        
        # Validate token properties
        assert isinstance(login_data["access_token"], str)
        assert len(login_data["access_token"]) > 50  # JWT tokens are long
        assert login_data["token_type"] == "bearer"

    async def test_me_endpoint_contract(self, async_client):
        """Test /api/auth/me endpoint contract with proper authentication."""
        # Generate unique user data
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"testuser_{unique_id}",
            "email": f"testuser_{unique_id}@example.com",
            "password": "SecureTestPass123!"
        }

        # Register and login user
        reg_response = await async_client.post("/api/auth/register", json=user_data)
        assert reg_response.status_code == 201

        # Login user
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        login_response = await async_client.post("/api/auth/login", data=login_data)
        assert login_response.status_code == 200
        
        login_json = login_response.json()
        token = login_json["access_token"]
        
        # Test /api/auth/me endpoint
        headers = {"Authorization": f"Bearer {token}"}
        me_response = await async_client.get("/api/auth/me", headers=headers)
        
        assert me_response.status_code == 200
        user_info = me_response.json()
        
        # Validate user data matches registration
        assert user_info["username"] == user_data["username"]

    async def test_me_endpoint_unauthorized(self, async_client):
        """Test /api/auth/me without authentication returns 401."""
        response = await async_client.get("/api/auth/me")
        assert response.status_code == 401
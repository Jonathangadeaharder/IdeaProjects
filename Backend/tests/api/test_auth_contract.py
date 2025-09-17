"""Contract tests for authentication endpoints.

These tests verify that the API contract is maintained:
- Request/response schemas match expectations
- HTTP status codes are correct
- Required fields are present
- Data types are correct
"""
import uuid
import pytest
from api.models.auth import RegisterRequest, LoginRequest, UserResponse, AuthResponse


@pytest.mark.asyncio
class TestAuthContract:
    """Contract tests for authentication API endpoints."""

    async def test_register_endpoint_contract(self, client):
        """Test user registration endpoint contract."""
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "TestPass123"
        }
        
        response = client.post("/api/auth/register", json=payload)
        
        # Contract: Should return 201 for successful registration
        assert response.status_code == 201
        
        # Contract: Response should contain user data directly (UserResponse)
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "is_active" in data
        assert "is_superuser" in data
        assert "is_verified" in data
        
        # Contract: User data should match request
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert isinstance(data["id"], str)  # FastAPI-Users uses UUID strings
        assert isinstance(data["username"], str)
        assert isinstance(data["is_active"], bool)
        assert isinstance(data["is_superuser"], bool)
        assert isinstance(data["is_verified"], bool)

    async def test_register_validation_contract(self, client):
        """Test registration validation contract."""
        # Test cases for validation - these should fail at validation level, not database level
        test_cases = [
            # Missing username
            ({"email": "test@example.com", "password": "TestPass123"}, 422, "Missing username should return 422"),
            # Missing email
            ({"username": "testuser", "password": "TestPass123"}, 422, "Missing email should return 422"),
            # Missing password
            ({"username": "testuser", "email": "test@example.com"}, 422, "Missing password should return 422"),
            # Invalid email format
            ({"username": "testuser", "email": "invalid-email", "password": "TestPass123"}, 422, "Invalid email should return 422"),
            # Empty password
            ({"username": "testuser", "email": "test@example.com", "password": ""}, 422, "Empty password should return 422"),
        ]
        
        for payload, expected_status, description in test_cases:
            response = client.post("/api/auth/register", json=payload)
            assert response.status_code == expected_status, f"{description}: got {response.status_code}, response: {response.text}"
        
        # Test empty payload
        response = client.post("/api/auth/register", json={})
        assert response.status_code == 422

    async def test_login_endpoint_contract(self, client):
        """Test user login endpoint contract."""
        # First register a user (use unique email to avoid conflicts)
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        register_payload = {
            "username": f"logintest_{unique_id}",
            "email": f"logintest_{unique_id}@example.com",
            "password": "LoginPass123"
        }
        register_response = client.post("/api/auth/register", json=register_payload)
        assert register_response.status_code == 201, f"Registration failed: {register_response.status_code} {register_response.text}"
        
        # Now test login (FastAPI-Users expects email in username field and form data)
        login_payload = {
            "username": f"logintest_{unique_id}@example.com",  # FastAPI-Users expects email here
            "password": "LoginPass123"
        }

        response = client.post("/api/auth/login", data=login_payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        # Contract: Should return 200 for successful login
        assert response.status_code == 200
        
        # Contract: Response should contain access token and token type (FastAPI-Users Bearer format)
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data

        # Contract: Access token should be a string
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

        # Contract: Token type should be "bearer"
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials_contract(self, client):
        """Test login with invalid credentials contract."""
        # Test with non-existent user
        response = client.post("/api/auth/login", data={
            "username": "nonexistent@example.com",  # FastAPI-Users expects email here
            "password": "SecurePass123!"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert response.status_code == 400  # FastAPI-Users returns 400 for bad credentials
        
        # Register a user first
        client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "SecurePass123"
        })
        
        # Test with wrong password
        response = client.post("/api/auth/login", data={
            "username": "testuser@example.com",  # FastAPI-Users expects email here
            "password": "WrongPassword1"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert response.status_code == 400  # FastAPI-Users returns 400 for bad credentials

    async def test_logout_endpoint_contract(self, client):
        """Test /api/auth/logout endpoint contract."""
        # Register and login first to get a valid token
        client.post("/api/auth/register", json={
            "username": "logouttest",
            "email": "logouttest@example.com",
            "password": "SecurePass123"
        })

        login_response = client.post("/api/auth/login", data={
            "username": "logouttest@example.com",  # FastAPI-Users expects email here
            "password": "SecurePass123"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        # Ensure login was successful
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        
        # Test logout with valid token
        response = client.post("/api/auth/logout", headers={
            "Authorization": f"Bearer {token}"
        })
        
        # FastAPI-Users logout endpoint returns 204 (No Content) with empty response
        assert response.status_code == 204

    async def test_me_endpoint_contract(self, client):
        """Test /api/auth/me endpoint contract."""
        # Register and login first
        client.post("/api/auth/register", json={
            "username": "metest",
            "email": "metest@example.com",
            "password": "SecurePass123"
        })

        login_response = client.post("/api/auth/login", data={
            "username": "metest@example.com",  # FastAPI-Users expects email here
            "password": "SecurePass123"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        token = login_response.json()["access_token"]
        
        # Test /api/auth/me
        response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        # Contract assertions
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure matches UserResponse model
        assert "id" in data
        assert "username" in data
        assert "is_superuser" in data
        assert "is_active" in data
        assert "created_at" in data
        assert "last_login" in data
        
        # Verify data types (FastAPI-Users uses UUID)
        assert isinstance(data["id"], str)  # UUID as string
        assert isinstance(data["username"], str)
        assert isinstance(data["is_superuser"], bool)
        assert isinstance(data["is_active"], bool)
        assert isinstance(data["created_at"], str)
        
        assert data["username"] == "metest"

    async def test_me_endpoint_unauthorized_contract(self, client):
        """Test /api/auth/me endpoint without authentication."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401  # FastAPI-Users returns 401 for unauthorized
        
        # Test with invalid token
        response = client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalid_token"
        })
        assert response.status_code == 401

    async def test_auth_endpoints_content_type_contract(self, client):
        """Test that auth endpoints return JSON content type."""
        # Test register endpoint
        response = client.post("/api/auth/register", json={
            "username": "test",
            "email": "test@example.com",
            "password": "test123"
        })
        assert "application/json" in response.headers.get("content-type", "")
        
        # Test login endpoint (without database dependency)
        response = client.post("/api/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert "application/json" in response.headers.get("content-type", "")
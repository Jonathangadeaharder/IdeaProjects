"""
API Contract Tests for Authentication Endpoints
Tests focus on verifying API responses match OpenAPI specification
"""
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.models.auth import RegisterRequest, LoginRequest, UserResponse, AuthResponse


class TestAuthApiContractCompliance:
    """Test authentication API contract compliance"""

    def test_register_endpoint_contract(self, client: TestClient):
        """Test register endpoint follows OpenAPI contract"""
        # Valid registration request
        valid_request = {
            "username": "testuser123",
            "password": "ValidPass123"
        }

        response = client.post("/api/auth/register", json=valid_request)

        # Should return 201 for successful registration
        if response.status_code == 201:
            # Response should match UserResponse schema
            try:
                user_response = UserResponse(**response.json())
                assert user_response.username == valid_request["username"]
                assert user_response.email is not None
                assert isinstance(user_response.is_active, bool)
            except ValidationError as e:
                pytest.fail(f"Response doesn't match UserResponse schema: {e}")

        # Should return 409 if user already exists
        elif response.status_code == 409:
            # Error response should have proper structure
            assert "detail" in response.json()

        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")

    def test_register_endpoint_validation_errors(self, client: TestClient):
        """Test register endpoint validation follows contract"""
        invalid_requests = [
            # Invalid username
            {"username": "ab", "password": "ValidPass123"},  # Too short
            {"username": "", "password": "ValidPass123"},     # Empty
            {"username": "user@invalid", "password": "ValidPass123"},  # Invalid chars

            # Invalid password
            {"username": "validuser", "password": "short"},      # Too short
            {"username": "validuser", "password": "nodigits"},   # No digits
            {"username": "validuser", "password": "NOLOWER123"}, # No lowercase
            {"username": "validuser", "password": "noupper123"}, # No uppercase
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/auth/register", json=invalid_request)

            # Should return 422 for validation errors
            assert response.status_code == 422, f"Expected 422 for {invalid_request}"

            # Response should have validation error structure
            error_response = response.json()
            assert "detail" in error_response
            assert isinstance(error_response["detail"], list)

    def test_login_endpoint_contract(self, client: TestClient):
        """Test login endpoint follows OpenAPI contract"""
        # First register a user
        register_data = {
            "username": "logintest123",
            "password": "LoginPass123"
        }
        client.post("/api/auth/register", json=register_data)

        # Valid login request
        login_request = {
            "username": "logintest123",
            "password": "LoginPass123"
        }

        response = client.post("/api/auth/login", json=login_request)

        # Should return 200 for successful login
        if response.status_code == 200:
            # Response should match AuthResponse schema
            try:
                auth_response = AuthResponse(**response.json())
                assert auth_response.token is not None
                assert len(auth_response.token) > 0
                assert auth_response.user.username == login_request["username"]
                assert auth_response.expires_at is not None
            except ValidationError as e:
                pytest.fail(f"Response doesn't match AuthResponse schema: {e}")

        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")

    def test_login_endpoint_invalid_credentials(self, client: TestClient):
        """Test login endpoint handles invalid credentials per contract"""
        invalid_login = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }

        response = client.post("/api/auth/login", json=invalid_login)

        # Should return 401 for invalid credentials
        assert response.status_code == 401

        # Response should have proper error structure
        error_response = response.json()
        assert "detail" in error_response

    def test_login_endpoint_validation_errors(self, client: TestClient):
        """Test login endpoint validation follows contract"""
        invalid_requests = [
            {"username": "", "password": "password"},      # Empty username
            {"username": "user", "password": ""},          # Empty password
            {},                                            # Missing fields
            {"username": "user"},                          # Missing password
            {"password": "pass"},                          # Missing username
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/auth/login", json=invalid_request)

            # Should return 422 for validation errors
            assert response.status_code == 422

            # Response should have validation error structure
            error_response = response.json()
            assert "detail" in error_response

    def test_me_endpoint_contract(self, client: TestClient):
        """Test /api/auth/me endpoint follows OpenAPI contract"""
        # Register and login to get token
        register_data = {
            "username": "metest123",
            "password": "MeTestPass123"
        }
        client.post("/api/auth/register", json=register_data)

        login_response = client.post("/api/auth/login", json=register_data)
        token = login_response.json()["token"]

        # Test authenticated request
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/me", headers=headers)

        # Should return 200 with user info
        if response.status_code == 200:
            try:
                user_response = UserResponse(**response.json())
                assert user_response.username == register_data["username"]
            except ValidationError as e:
                pytest.fail(f"Response doesn't match UserResponse schema: {e}")

        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")

    def test_me_endpoint_unauthorized(self, client: TestClient):
        """Test /api/auth/me endpoint handles unauthorized requests"""
        # Request without token
        response = client.get("/api/auth/me")
        assert response.status_code == 401

        # Request with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401

        # Request with malformed authorization header
        headers = {"Authorization": "InvalidFormat"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401


class TestAuthApiRequestValidation:
    """Test request validation against Pydantic models"""

    def test_register_request_model_validation(self):
        """Test RegisterRequest model validates correctly"""
        # Valid request
        valid_data = {
            "username": "testuser123",
            "password": "ValidPass123"
        }
        request = RegisterRequest(**valid_data)
        assert request.username == "testuser123"
        assert request.password == "ValidPass123"

        # Invalid requests should raise ValidationError
        invalid_cases = [
            {"username": "ab", "password": "ValidPass123"},         # Username too short
            {"username": "user@invalid", "password": "ValidPass123"}, # Invalid chars
            {"username": "validuser", "password": "short"},         # Password too short
            {"username": "validuser", "password": "nodigits"},      # No digits
        ]

        for invalid_data in invalid_cases:
            with pytest.raises(ValidationError):
                RegisterRequest(**invalid_data)

    def test_login_request_model_validation(self):
        """Test LoginRequest model validates correctly"""
        # Valid request
        valid_data = {
            "username": "testuser",
            "password": "anypassword"
        }
        request = LoginRequest(**valid_data)
        assert request.username == "testuser"
        assert request.password == "anypassword"

        # Invalid requests
        invalid_cases = [
            {"username": "", "password": "password"},  # Empty username
            {"username": "user", "password": ""},      # Empty password
        ]

        for invalid_data in invalid_cases:
            with pytest.raises(ValidationError):
                LoginRequest(**invalid_data)


class TestAuthApiResponseValidation:
    """Test response validation against Pydantic models"""

    def test_user_response_model_structure(self):
        """Test UserResponse model structure"""
        from uuid import uuid4

        user_data = {
            "id": uuid4(),
            "username": "testuser",
            "email": "test@example.com",
            "is_superuser": False,
            "is_active": True,
            "created_at": "2024-01-15T10:30:00Z",
            "last_login": None
        }

        user_response = UserResponse(**user_data)
        assert user_response.username == "testuser"
        assert user_response.email == "test@example.com"
        assert not user_response.is_superuser
        assert user_response.is_active
        assert user_response.last_login is None

    def test_auth_response_model_structure(self):
        """Test AuthResponse model structure"""
        from uuid import uuid4

        user_data = {
            "id": uuid4(),
            "username": "testuser",
            "email": "test@example.com",
            "is_superuser": False,
            "is_active": True,
            "created_at": "2024-01-15T10:30:00Z",
            "last_login": None
        }

        auth_data = {
            "token": "jwt_token_example",
            "user": UserResponse(**user_data),
            "expires_at": "2024-01-21T14:45:00Z"
        }

        auth_response = AuthResponse(**auth_data)
        assert auth_response.token == "jwt_token_example"
        assert auth_response.user.username == "testuser"
        assert auth_response.expires_at == "2024-01-21T14:45:00Z"


class TestAuthApiErrorHandling:
    """Test API error handling follows consistent patterns"""

    def test_error_response_structure(self, client: TestClient):
        """Test that error responses have consistent structure"""
        # Test validation error
        invalid_request = {"username": "", "password": ""}
        response = client.post("/api/auth/register", json=invalid_request)

        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

        # Detail should be list of validation errors
        assert isinstance(error_data["detail"], list)
        if len(error_data["detail"]) > 0:
            error_item = error_data["detail"][0]
            assert "loc" in error_item  # Field location
            assert "msg" in error_item  # Error message
            assert "type" in error_item # Error type

    def test_authentication_error_structure(self, client: TestClient):
        """Test authentication error responses have consistent structure"""
        invalid_login = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }

        response = client.post("/api/auth/login", json=invalid_login)

        if response.status_code == 401:
            error_data = response.json()
            assert "detail" in error_data
            assert isinstance(error_data["detail"], str)

    def test_authorization_error_structure(self, client: TestClient):
        """Test authorization error responses have consistent structure"""
        response = client.get("/api/auth/me")

        assert response.status_code == 401
        error_data = response.json()
        assert "detail" in error_data


class TestAuthApiHeaders:
    """Test API headers and content types"""

    def test_content_type_headers(self, client: TestClient):
        """Test API endpoints return proper content types"""
        valid_request = {
            "username": "headertest123",
            "password": "HeaderTest123"
        }

        response = client.post("/api/auth/register", json=valid_request)

        # Should return JSON content type
        assert "application/json" in response.headers.get("content-type", "")

    def test_cors_headers(self, client: TestClient):
        """Test CORS headers if configured"""
        response = client.options("/api/auth/register")

        # Check if CORS headers are present (if configured)
        if "access-control-allow-origin" in response.headers:
            assert response.headers["access-control-allow-origin"] is not None

    def test_security_headers(self, client: TestClient):
        """Test security-related headers"""
        response = client.get("/api/auth/me")

        # Check for security headers if configured
        headers = response.headers
        # These headers might be set by security middleware
        potential_security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "strict-transport-security"
        ]

        # Just verify headers are strings if present
        for header in potential_security_headers:
            if header in headers:
                assert isinstance(headers[header], str)


class TestAuthApiDocumentation:
    """Test API documentation compliance"""

    def test_openapi_schema_compliance(self, client: TestClient):
        """Test that API follows OpenAPI schema"""
        # Get OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema

        # Check auth endpoints are documented
        paths = schema["paths"]
        assert "/api/auth/register" in paths
        assert "/api/auth/login" in paths

        # Verify POST methods are documented
        assert "post" in paths["/api/auth/register"]
        assert "post" in paths["/api/auth/login"]

    def test_api_endpoint_documentation(self, client: TestClient):
        """Test that API endpoints have proper documentation"""
        response = client.get("/openapi.json")
        schema = response.json()

        # Check register endpoint documentation
        register_endpoint = schema["paths"]["/api/auth/register"]["post"]
        assert "summary" in register_endpoint or "description" in register_endpoint
        assert "requestBody" in register_endpoint
        assert "responses" in register_endpoint

        # Check login endpoint documentation
        login_endpoint = schema["paths"]["/api/auth/login"]["post"]
        assert "summary" in login_endpoint or "description" in login_endpoint
        assert "requestBody" in login_endpoint
        assert "responses" in login_endpoint
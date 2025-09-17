"""
Simple implementation-agnostic auth tests.
These tests verify basic API functionality without relying on specific implementation details.
"""
import pytest


@pytest.mark.asyncio
async def test_auth_endpoints_exist(async_client):
    """Test that auth endpoints exist and return appropriate status codes."""
    # Test register endpoint exists
    register_response = await async_client.post("/api/auth/register", json={
        "username": "testuser_exist", 
        "password": "TestPass123", 
        "email": "testuser_exist@example.com"
    })
    assert register_response.status_code in [200, 201, 400, 409, 422], f"Register endpoint should exist, got {register_response.status_code}"
    
    # Test login endpoint exists
    login_response = await async_client.post("/api/auth/login", data={
        "username": "testuser_exist", 
        "password": "TestPass123"
    })
    assert login_response.status_code in [200, 400, 401, 422], f"Login endpoint should exist, got {login_response.status_code}"
    
    # Test me endpoint exists
    me_response = await async_client.get("/api/auth/me")
    assert me_response.status_code in [200, 401, 403], f"Me endpoint should exist, got {me_response.status_code}"


@pytest.mark.asyncio
async def test_auth_endpoints_return_json(async_client):
    """Test that auth endpoints return JSON content type."""
    # Test register endpoint
    register_response = await async_client.post("/api/auth/register", json={
        "username": "testuser_json", 
        "password": "TestPass123", 
        "email": "testuser_json@example.com"
    })
    assert "application/json" in register_response.headers.get("content-type", "")
    
    # Test login endpoint
    login_response = await async_client.post("/api/auth/login", data={
        "username": "testuser_json", 
        "password": "TestPass123"
    })
    assert "application/json" in login_response.headers.get("content-type", "")
    
    # Test me endpoint
    me_response = await async_client.get("/api/auth/me")
    assert "application/json" in me_response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_auth_validation_errors(async_client):
    """Test that auth endpoints return validation errors for malformed requests."""
    # Test register with missing fields
    response = await async_client.post("/api/auth/register", json={
        "username": "missing_fields"
        # Missing password and email
    })
    assert response.status_code == 422, f"Should return 422 for missing fields, got {response.status_code}"
    
    # Test login with missing fields
    response = await async_client.post("/api/auth/login", data={
        "username": "missing_password"
        # Missing password
    })
    assert response.status_code == 422, f"Should return 422 for missing login fields, got {response.status_code}"
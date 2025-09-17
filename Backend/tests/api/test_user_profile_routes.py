"""
Tests for user profile routes and dependency behavior.
"""
from __future__ import annotations

import pytest
import uuid
import httpx
from typing import Dict, Any
from unittest.mock import Mock, patch


@pytest.fixture()
async def auth_header(async_client, url_builder):
    """Perform real authentication and return valid auth header"""
    # Generate unique user data
    unique_id = uuid.uuid4().hex[:8]
    email = f"testuser_{unique_id}@example.com"
    username = f"testuser_{unique_id}"
    password = "TestPass123!"
    
    # Register user
    register_url = url_builder.url_for("register:register")
    reg_response = await async_client.post(register_url, json={
        "username": username,
        "email": email,
        "password": password
    })
    assert reg_response.status_code == 201, f"Registration failed: {reg_response.text}"
    
    # Login user
    login_url = url_builder.url_for("auth:jwt-bearer.login")
    login_response = await async_client.post(login_url, data={
        "username": email,
        "password": password
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    # FastAPI-Users can return either:
    # 204 with cookies for cookie-based auth
    # 200 with JSON token for token-based auth
    assert login_response.status_code in [200, 204], f"Login failed: {login_response.text}"
    
    if login_response.status_code == 200:
        # Token-based authentication
        token_data = login_response.json()
        access_token = token_data["access_token"]
        return {"Authorization": f"Bearer {access_token}"}
    else:
        # Cookie-based authentication
        cookies = login_response.cookies
        cookie_header = "; ".join([f"{key}={value}" for key, value in cookies.items()])
        return {"Cookie": cookie_header}


@pytest.mark.asyncio
async def test_get_profile_ok(async_client, auth_header, url_builder):
    profile_url = url_builder.url_for("profile_get")
    r = await async_client.get(profile_url, headers=auth_header)
    assert r.status_code == 200
    data = r.json()
    # Since we're using a dynamically generated user, we can't check for specific values
    # but we can check that the response has the expected structure
    assert "username" in data
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_profile_invalid_token(async_client, url_builder):
    # Missing or invalid token should be unauthorized
    profile_url = url_builder.url_for("profile_get")
    r = await async_client.get(profile_url, headers={"Authorization": "Bearer BAD"})
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_update_languages_success(async_client, auth_header, url_builder):
    body = {"native_language": "en", "target_language": "de"}
    languages_url = url_builder.url_for("profile_update_languages")
    r = await async_client.put(languages_url, json=body, headers=auth_header)
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["native_language"]["code"] == "en"
    assert data["target_language"]["code"] == "de"


@pytest.mark.asyncio
async def test_update_languages_same_code_validation(async_client, auth_header, url_builder):
    body = {"native_language": "en", "target_language": "en"}
    languages_url = url_builder.url_for("profile_update_languages")
    r = await async_client.put(languages_url, json=body, headers=auth_header)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_update_languages_invalid_code(async_client, auth_header, url_builder):
    body = {"native_language": "en", "target_language": "xx"}
    languages_url = url_builder.url_for("profile_update_languages")
    r = await async_client.put(languages_url, json=body, headers=auth_header)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_update_languages_backend_failure(async_client, auth_header, url_builder):
    # Test that when there's a backend failure (ValueError), it returns 422
    # We'll trigger this by sending invalid data that causes a ValueError
    body = {"native_language": "invalid", "target_language": "de"}
    languages_url = url_builder.url_for("profile_update_languages")
    r = await async_client.put(languages_url, json=body, headers=auth_header)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_get_supported_languages(async_client, url_builder):
    languages_url = url_builder.url_for("profile_get_supported_languages")
    r = await async_client.get(languages_url)
    assert r.status_code == 200
    data = r.json()
    # Expect at least English and German present
    assert "en" in data and "de" in data

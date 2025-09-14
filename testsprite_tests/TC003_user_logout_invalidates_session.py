import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_user_logout_invalidates_session():
    # First register a new user to ensure clean state
    register_url = f"{BASE_URL}/api/auth/register"
    login_url = f"{BASE_URL}/api/auth/login"
    logout_url = f"{BASE_URL}/api/auth/logout"
    me_url = f"{BASE_URL}/api/auth/me"

    username = "testuser_logout_tc003"
    password = "TestPassword123!"

    # Register user
    reg_payload = {
        "username": username,
        "password": password
    }
    try:
        reg_resp = requests.post(register_url, json=reg_payload, timeout=TIMEOUT)
        assert reg_resp.status_code == 201

        # Login user to get authentication token
        login_payload = {
            "username": username,
            "password": password
        }
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200
        login_data = login_resp.json()
        token = login_data.get("token")
        assert token and isinstance(token, str)

        headers_auth = {
            "Authorization": f"Bearer {token}"
        }

        # Verify user is authenticated by calling /api/auth/me
        me_resp = requests.get(me_url, headers=headers_auth, timeout=TIMEOUT)
        assert me_resp.status_code == 200
        user_data = me_resp.json()
        assert "username" in user_data
        assert user_data["username"] == username

        # Perform logout
        logout_resp = requests.post(logout_url, headers=headers_auth, timeout=TIMEOUT)
        assert logout_resp.status_code in (200, 204)

        # Verify token/session is invalidated by calling /api/auth/me again
        me_after_logout_resp = requests.get(me_url, headers=headers_auth, timeout=TIMEOUT)
        # Expect unauthorized or forbidden status (401/403) after logout
        assert me_after_logout_resp.status_code in (401, 403)

    finally:
        # Cleanup: If there's an endpoint to delete user, it would be called here.
        # Since no delete user API is specified, we skip cleanup.
        pass

test_user_logout_invalidates_session()

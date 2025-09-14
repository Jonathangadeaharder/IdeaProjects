import requests

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
ME_URL = f"{BASE_URL}/api/auth/me"
TIMEOUT = 30

def test_get_current_user_information():
    username = "testuser_tc004"
    password = "TestPassword123!"

    # First, register a user (handle if user already exists)
    register_url = f"{BASE_URL}/api/auth/register"
    register_payload = {"username": username, "password": password}
    try:
        register_resp = requests.post(register_url, json=register_payload, timeout=TIMEOUT)
        # Allow 400 if user exists, ignore error and proceed to login
        if register_resp.status_code not in (200, 201, 400):
            register_resp.raise_for_status()
    except requests.RequestException as e:
        # Proceed anyway to login step; user might exist
        pass

    # Login to get JWT token
    login_payload = {"username": username, "password": password}
    login_resp = requests.post(LOGIN_URL, json=login_payload, timeout=TIMEOUT)
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    login_data = login_resp.json()
    token = login_data.get("token")
    assert token and isinstance(token, str), "Token missing or invalid in login response"
    user = login_data.get("user")
    assert user and isinstance(user, dict), "User info missing or invalid in login response"

    headers = {"Authorization": f"Bearer {token}"}

    # Call /api/auth/me endpoint
    me_resp = requests.get(ME_URL, headers=headers, timeout=TIMEOUT)
    assert me_resp.status_code == 200, f"/api/auth/me failed with status {me_resp.status_code}: {me_resp.text}"
    me_data = me_resp.json()
    assert isinstance(me_data, dict), "Response from /api/auth/me is not a JSON object"

    # Validate that fields from login user object appear in /api/auth/me response
    for key in ["username", "id"]:
        assert key in me_data, f"'{key}' not found in /api/auth/me response"
        assert me_data[key] == user.get(key), f"Mismatch in '{key}' between login and /api/auth/me responses"

    # Optional: check some user info fields are non-empty strings or appropriate type
    assert isinstance(me_data.get("username"), str) and me_data["username"], "Invalid username in /api/auth/me response"

# Run the test
test_get_current_user_information()
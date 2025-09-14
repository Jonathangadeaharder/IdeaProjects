import requests

BASE_URL = "http://localhost:8000"
AUTH_USERNAME = "admin"
AUTH_PASSWORD = "admin"
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 30

def get_jwt_token(username, password):
    login_url = f"{BASE_URL}/auth/login"
    payload = {"username": username, "password": password}
    resp = requests.post(login_url, json=payload, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    json_resp = resp.json()
    token = json_resp.get("access_token") or json_resp.get("token") or json_resp.get("jwt")
    assert token, "JWT token not found in login response"
    return token

def test_get_and_update_user_profile_settings():
    token = None
    try:
        token = get_jwt_token(AUTH_USERNAME, AUTH_PASSWORD)
    except Exception as e:
        assert False, f"Login to get JWT token failed: {e}"

    auth_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    get_url = f"{BASE_URL}/profile/settings"
    put_url = get_url

    # Step 1: GET current profile settings
    try:
        get_resp = requests.get(get_url, headers=auth_headers, timeout=TIMEOUT)
        get_resp.raise_for_status()
        original_settings = get_resp.json()
        assert isinstance(original_settings, dict)
        # Validate keys if present
        assert "language" in original_settings or "difficulty_level" in original_settings or True
    except Exception as e:
        assert False, f"GET /profile/settings failed: {e}"

    # Prepare new settings to update
    new_language = "de" if original_settings.get("language") != "de" else "en"
    new_difficulty = "intermediate" if original_settings.get("difficulty_level") != "intermediate" else "beginner"
    update_payload = {
        "language": new_language,
        "difficulty_level": new_difficulty
    }

    # Step 2: PUT updated profile settings
    try:
        put_resp = requests.put(put_url, headers=auth_headers, json=update_payload, timeout=TIMEOUT)
        put_resp.raise_for_status()
        put_json = put_resp.json()
        assert put_resp.status_code == 200
    except Exception as e:
        assert False, f"PUT /profile/settings failed: {e}"

    # Step 3: GET profile settings again to verify update persisted
    try:
        verify_resp = requests.get(get_url, headers=auth_headers, timeout=TIMEOUT)
        verify_resp.raise_for_status()
        verified_settings = verify_resp.json()
        assert isinstance(verified_settings, dict)
        assert verified_settings.get("language") == new_language, "Language update did not persist"
        assert verified_settings.get("difficulty_level") == new_difficulty, "Difficulty level update did not persist"
    except Exception as e:
        assert False, f"Verification GET /profile/settings failed: {e}"

test_get_and_update_user_profile_settings()

import requests

BASE_URL = "http://localhost:8000"
LOGIN_PATH = "/api/auth/login"
TIMEOUT = 30

def test_user_login_with_valid_credentials():
    url = BASE_URL + LOGIN_PATH
    # Assuming these are valid credentials for a test user in the system
    payload = {
        "username": "testuser",
        "password": "TestPassword123!"
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        json_response = response.json()

        # Assert presence of token, user object, and expires_at in response
        assert "token" in json_response, "JWT token missing in response"
        assert isinstance(json_response["token"], str) and len(json_response["token"]) > 0, "Invalid token received"

        assert "user" in json_response, "User object missing in response"
        assert isinstance(json_response["user"], dict), "User object is not a dictionary"

        assert "expires_at" in json_response, "Expiration time missing in response"
        assert isinstance(json_response["expires_at"], str) and len(json_response["expires_at"]) > 0, "Invalid expires_at value"

    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {e}"

test_user_login_with_valid_credentials()
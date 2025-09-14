import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_user_login_with_correct_credentials():
    url = f"{BASE_URL}/auth/login"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "username": "admin",
        "password": "admin"
    }
    try:
        # Make POST request with basic token auth as per instructions
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT,
                                 auth=HTTPBasicAuth('admin', 'admin'))
        # Validate HTTP status
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
        # Validate response contains token
        response_json = response.json()
        assert isinstance(response_json, dict), "Response is not a JSON object"
        assert "token" in response_json or "access_token" in response_json, "JWT token key not found in response"
        token = response_json.get("token") or response_json.get("access_token")
        assert isinstance(token, str) and len(token) > 0, "JWT token is empty or invalid"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_user_login_with_correct_credentials()
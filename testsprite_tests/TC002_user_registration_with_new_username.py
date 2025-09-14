import requests
import string
import random

BASE_URL = "http://localhost:8000"
REGISTER_ENDPOINT = "/api/auth/register"
DELETE_USER_ENDPOINT = "/api/auth/delete"  # Not described in PRD, assume it doesn't exist; so no deletion via API


def test_user_registration_with_new_username():
    """
    Test the /api/auth/register endpoint to ensure a new user can register with a unique username and password,
    and receive a user object in response.
    """
    session = requests.Session()
    timeout = 30
    # Generate a unique username for testing
    random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    username = f"testuser_{random_suffix}"
    password = "TestPass123!"

    url = BASE_URL + REGISTER_ENDPOINT
    payload = {
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = session.post(url, json=payload, headers=headers, timeout=timeout)
        assert response.status_code == 200 or response.status_code == 201, f"Expected 200 or 201 but got {response.status_code}"
        data = response.json()
        # Validate that 'user' object is present in response
        assert "user" in data, "'user' key not found in response"
        user_obj = data["user"]
        # Minimal check to see user object has username and id or similar
        assert isinstance(user_obj, dict), "user object is not a dictionary"
        assert "username" in user_obj, "username missing in user object"
        assert user_obj["username"] == username, "Username in response does not match requested username"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"
    except ValueError:
        assert False, "Response is not valid JSON"


test_user_registration_with_new_username()
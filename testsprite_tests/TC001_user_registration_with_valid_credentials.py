import requests
from requests.auth import HTTPBasicAuth

def test_user_registration_with_valid_credentials():
    base_url = "http://localhost:8000"
    endpoint = "/auth/register"
    url = base_url + endpoint

    # Basic token auth as per instructions (will send as Basic Auth header)
    auth = HTTPBasicAuth("admin", "admin")
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "username": "new_test_user",
        "password": "ValidPass123!"
    }

    response = None
    try:
        response = requests.post(url, json=payload, headers=headers, auth=auth, timeout=30)
        response.raise_for_status()
        # Expecting HTTP 200 for successful registration
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        # Response confirmation check - could be empty or have json, just check text or json
        # Since no detailed response schema, check existence of some confirmation text or json
        if response.headers.get('Content-Type', '').startswith('application/json'):
            json_data = response.json()
            # In absence of detailed response schema, just verify json is dict and non-empty
            assert isinstance(json_data, dict), "Response JSON is not a dict"
        else:
            # If not json, check response text non-empty
            assert response.text, "Response text is empty"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_user_registration_with_valid_credentials()
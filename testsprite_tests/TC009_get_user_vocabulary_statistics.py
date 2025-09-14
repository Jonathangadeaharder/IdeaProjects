import requests

BASE_URL = "http://localhost:8000"
AUTH_USERNAME = "admin"
AUTH_PASSWORD = "admin"
TIMEOUT = 30

def test_get_user_vocabulary_statistics():
    try:
        # Step 1: Authenticate and get JWT token
        login_url = f"{BASE_URL}/auth/login"
        login_payload = {
            "username": AUTH_USERNAME,
            "password": AUTH_PASSWORD
        }
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed with status {login_resp.status_code}"
        login_data = login_resp.json()
        assert "token" in login_data, "Login response missing token"
        token = login_data["token"]

        # Step 2: Access /vocabulary/stats endpoint with Authorization header
        stats_url = f"{BASE_URL}/vocabulary/stats"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        stats_resp = requests.get(stats_url, headers=headers, timeout=TIMEOUT)
        assert stats_resp.status_code == 200, f"Vocabulary stats request failed with status {stats_resp.status_code}"
        stats_data = stats_resp.json()

        # Step 3: Validate the response includes required fields with proper types
        assert isinstance(stats_data, dict), "Stats response is not a JSON object"
        assert "total_words" in stats_data, "'total_words' missing in stats response"
        assert "known_words" in stats_data, "'known_words' missing in stats response"
        assert "learning_progress" in stats_data, "'learning_progress' missing in stats response"
        assert isinstance(stats_data["total_words"], (int, float)), "'total_words' should be a number"
        assert isinstance(stats_data["known_words"], (int, float)), "'known_words' should be a number"
        assert isinstance(stats_data["learning_progress"], (int, float)), "'learning_progress' should be a number"

        # Optional: logical checks
        assert stats_data["total_words"] >= stats_data["known_words"] >= 0, "Known words count invalid"
        assert 0.0 <= stats_data["learning_progress"] <= 1.0, "Learning progress should be between 0 and 1"

    except requests.RequestException as e:
        assert False, f"HTTP request failed: {e}"
    except AssertionError as e:
        raise
    except Exception as e:
        assert False, f"Unexpected error: {e}"

test_get_user_vocabulary_statistics()

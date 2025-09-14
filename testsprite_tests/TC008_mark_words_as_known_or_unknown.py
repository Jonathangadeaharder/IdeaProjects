import requests

BASE_URL = "http://localhost:8000"
AUTH = ("admin", "admin")
TIMEOUT = 30

def test_mark_words_as_known_or_unknown():
    # Sample word to mark known and unknown
    test_word = "Haus"

    headers = {
        "Content-Type": "application/json"
    }

    # Mark the word as known
    payload_known = {
        "word": test_word,
        "known": True
    }

    try:
        response_known = requests.post(
            f"{BASE_URL}/vocabulary/mark-known",
            auth=AUTH,
            headers=headers,
            json=payload_known,
            timeout=TIMEOUT
        )
        response_known.raise_for_status()
        assert response_known.status_code == 200
        json_resp_known = response_known.json()
        assert isinstance(json_resp_known, dict) or json_resp_known is None

        # Mark the word as unknown
        payload_unknown = {
            "word": test_word,
            "known": False
        }

        response_unknown = requests.post(
            f"{BASE_URL}/vocabulary/mark-known",
            auth=AUTH,
            headers=headers,
            json=payload_unknown,
            timeout=TIMEOUT
        )
        response_unknown.raise_for_status()
        assert response_unknown.status_code == 200
        json_resp_unknown = response_unknown.json()
        assert isinstance(json_resp_unknown, dict) or json_resp_unknown is None

    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {e}"

test_mark_words_as_known_or_unknown()
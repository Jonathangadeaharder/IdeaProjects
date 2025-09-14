import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"
AUTH_USERNAME = "admin"
AUTH_PASSWORD = "admin"
TIMEOUT = 30


def test_filter_subtitles_based_on_user_knowledge():
    """
    Test the /process/filter endpoint to ensure subtitles can be filtered according to user vocabulary knowledge
    and difficulty level, and the filtered subtitles are returned correctly.
    """

    url = f"{BASE_URL}/process/filter"
    auth = HTTPBasicAuth(AUTH_USERNAME, AUTH_PASSWORD)
    headers = {
        "Content-Type": "application/json",
    }

    # Sample subtitles text (a typical subtitles string for testing)
    sample_subtitles = (
        "1\n00:00:01,600 --> 00:00:04,200\nHallo, wie geht es dir?\n\n"
        "2\n00:00:05,900 --> 00:00:07,999\nIch lerne Deutsch.\n\n"
        "3\n00:00:08,000 --> 00:00:10,000\nDas ist ein Test.\n"
    )
    difficulty_level = "intermediate"

    payload = {
        "subtitles": sample_subtitles,
        "difficulty_level": difficulty_level
    }

    try:
        response = requests.post(url, auth=auth, headers=headers, json=payload, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to {url} failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # Validate the response contains filtered subtitles string
    assert isinstance(data, dict), "Response JSON should be a dictionary"
    assert "filtered_subtitles" in data, "Response JSON missing 'filtered_subtitles' key"
    filtered_subtitles = data["filtered_subtitles"]
    assert isinstance(filtered_subtitles, str), "'filtered_subtitles' should be a string"
    assert len(filtered_subtitles) > 0, "'filtered_subtitles' should not be empty"

    # Additional sanity check: filtered subtitles should be a substring or transformed version of input subtitles
    assert filtered_subtitles != sample_subtitles, "Filtered subtitles should differ from original subtitles"


test_filter_subtitles_based_on_user_knowledge()
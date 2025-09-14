import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_get_list_of_available_videos():
    url = f"{BASE_URL}/api/videos"
    headers = {
        "Accept": "application/json",
    }
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to GET /api/videos failed: {e}"

    json_response = response.json()
    assert isinstance(json_response, dict), f"Response is not a JSON object: {json_response}"
    assert "videos" in json_response, "'videos' key not in response"
    assert isinstance(json_response["videos"], list), "'videos' is not a list"

    for video in json_response["videos"]:
        assert isinstance(video, dict), "Video item is not a dictionary"
        # We do not have detailed schema, but must contain minimal video info keys
        # Common video info might include: id, title, series, episode, duration, url
        # We check for some plausible keys to ensure structure
        expected_keys = ["id", "title", "series", "episode", "duration"]
        has_any_key = any(key in video for key in expected_keys)
        assert has_any_key, f"Video item does not contain expected keys: {video}"

test_get_list_of_available_videos()
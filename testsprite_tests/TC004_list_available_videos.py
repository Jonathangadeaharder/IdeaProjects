import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_list_available_videos():
    url = f"{BASE_URL}/videos/list"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
        videos = response.json()
        assert isinstance(videos, list), "Response is not a list"
        for video in videos:
            assert isinstance(video, dict), "Video item is not a dictionary"
            assert "id" in video and isinstance(video["id"], str) and video["id"], "Video item missing valid 'id'"
            assert "title" in video and isinstance(video["title"], str) and video["title"], "Video item missing valid 'title'"
            assert "duration" in video and (isinstance(video["duration"], int) or isinstance(video["duration"], float)), "Video item missing valid 'duration'"
            assert video["duration"] >= 0, "Video 'duration' must be non-negative"
    except requests.RequestException as e:
        assert False, f"Request to list videos failed: {e}"

test_list_available_videos()
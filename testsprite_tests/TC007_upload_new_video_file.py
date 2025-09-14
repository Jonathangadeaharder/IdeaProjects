import requests
from requests.exceptions import RequestException

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_upload_new_video_file():
    url = f"{BASE_URL}/api/videos/upload"
    series_name = "TestSeriesUpload"
    video_content = b"FAKE_VIDEO_DATA"  # Simulated video file content for test
    video_filename = "test_video.mp4"
    files = {
        "video_file": (video_filename, video_content, "video/mp4"),
    }
    data = {
        "series": series_name
    }

    try:
        response = requests.post(url, data=data, files=files, timeout=TIMEOUT)
        # For success, expect 200 or 201 status code (not specified exactly)
        assert response.status_code in (200, 201), f"Unexpected status code: {response.status_code}"
        # Response could contain info about uploaded video, assume JSON
        json_response = response.json()
        # Validate that response confirms upload; expect at least series field or some confirmation
        assert isinstance(json_response, dict), "Response is not a JSON object"
        # Check presence of some key or assume success message or uploaded video id
        # Since schema doesn't specify response, just check for 'series' or similar or no error
        # If 'series' returned, it should match
        if "series" in json_response:
            assert json_response["series"] == series_name, "Series name in response mismatch"
        # If upload returns video id or url, ensure present (optional)
    except RequestException as e:
        assert False, f"Request failed: {e}"
    except ValueError:
        assert False, "Response was not JSON"

test_upload_new_video_file()
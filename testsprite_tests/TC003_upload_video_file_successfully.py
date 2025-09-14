import requests
from requests.auth import HTTPBasicAuth

def test_upload_video_file_successfully():
    base_url = "http://localhost:8000"
    upload_endpoint = f"{base_url}/videos/upload"
    auth = HTTPBasicAuth("admin", "admin")
    timeout = 30

    # Prepare a small sample video file content
    # Since no file path is provided, generate a minimal valid mp4 header for testing purpose
    # This is a minimal 'fake' mp4 to simulate the upload.
    video_content = (
        b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41'
        b'\x00\x00\x00\x08free\x00\x00\x02\x0cmdat\x00\x00\x02\x00'
    )

    files = {
        'file': ('test_video.mp4', video_content, 'video/mp4'),
    }

    try:
        response = requests.post(upload_endpoint, auth=auth, files=files, timeout=timeout)
        response.raise_for_status()
        json_response = response.json()
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        # The PRD states response indicates successful upload, typically message or similar
        # Since response schema is not detailed, we just ensure JSON response contains success indication
        # eg: message or success key
        assert isinstance(json_response, dict), "Response is not a JSON object"
        # Accept any typical keys that might indicate success
        success_keys = ['message', 'success', 'uploaded', 'id']
        assert any(key in json_response for key in success_keys), "Response JSON does not indicate successful upload"
    except requests.exceptions.RequestException as e:
        assert False, f"HTTP request failed: {e}"

test_upload_video_file_successfully()
import requests
from requests.auth import HTTPBasicAuth

def test_transcribe_audio_video_using_whisper_ai():
    base_url = "http://localhost:8000"
    auth = HTTPBasicAuth("admin", "admin")
    headers = {"Content-Type": "application/json"}
    timeout = 30

    # Since resource ID or file_path is not provided, upload a small sample video to get file_path first
    video_upload_url = f"{base_url}/videos/upload"
    try:
        # Prepare a minimal test video file content (empty or a small dummy content)
        # We use BytesIO to simulate a file in memory (e.g. a WAV file or MP4); for demo, just some bytes
        from io import BytesIO
        test_video_content = BytesIO(b"\x00\x00\x00\x18ftypmp42")  # minimal MP4 header bytes
        files = {'file': ('test_video.mp4', test_video_content, 'video/mp4')}
        upload_resp = requests.post(video_upload_url, auth=auth, files=files, timeout=timeout)
        upload_resp.raise_for_status()
        upload_data = upload_resp.json()
        # Expecting upload response 200 - confirm or find file_path/id from response if given
        # Assume the API returns a 'file_path' or 'id' in response on successful upload
        # If only file ID is returned, compose file_path accordingly or assume file_path is returned directly
        file_path = upload_data.get("file_path") or upload_data.get("id")
        if not file_path:
            raise ValueError("Upload response missing file_path or id for the uploaded video")

        # Prepare transcription payload
        transcribe_url = f"{base_url}/process/transcribe"
        payload = {
            "file_path": file_path,
            "model_size": "small"
        }

        resp = requests.post(transcribe_url, auth=auth, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()

        # Validate response contains transcription result or expected keys
        assert resp.status_code == 200, f"Expected status code 200, got {resp.status_code}"
        assert isinstance(data, dict), "Response JSON is not a dictionary"

        # Typical transcription response might contain "transcription" or "text"
        assert "transcription" in data or "text" in data, "Response does not contain transcription result"
        transcription_text = data.get("transcription") or data.get("text")
        assert isinstance(transcription_text, str), "Transcription result is not a string"
        assert len(transcription_text) > 0, "Transcription result is empty"

    finally:
        # Cleanup: delete the uploaded video to not pollute storage
        # Assuming there's an endpoint /videos/delete/{id} that accepts DELETE method
        # Only attempt if file_path contains something like id string
        if 'file_path' in locals() and file_path:
            delete_url = f"{base_url}/videos/delete/{file_path}"
            try:
                del_resp = requests.delete(delete_url, auth=auth, timeout=timeout)
                # It's okay if delete fails, just log or ignore
            except Exception:
                pass

test_transcribe_audio_video_using_whisper_ai()
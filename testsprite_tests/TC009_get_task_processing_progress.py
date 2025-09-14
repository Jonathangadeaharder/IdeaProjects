import requests
import time

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_get_task_processing_progress():
    # Step 1: Prepare a video episode for processing to obtain a valid task_id
    prepare_url = f"{BASE_URL}/api/videos/prepare"
    prepare_payload = {
        "video_path": "sample_series/sample_episode.mp4"
    }
    task_id = None

    try:
        prepare_response = requests.post(prepare_url, json=prepare_payload, timeout=TIMEOUT)
        assert prepare_response.status_code == 200, f"Unexpected status code {prepare_response.status_code} on prepare"
        prepare_data = prepare_response.json()
        assert "task_id" in prepare_data, "No task_id in prepare response"
        assert "status" in prepare_data, "No status in prepare response"
        task_id = prepare_data["task_id"]

        # Allow some time for task to start processing before checking progress
        time.sleep(2)

        # Step 2: Query the task progress using the task_id
        progress_url = f"{BASE_URL}/api/tasks/{task_id}/progress"
        progress_response = requests.get(progress_url, timeout=TIMEOUT)
        assert progress_response.status_code == 200, f"Unexpected status code {progress_response.status_code} on progress"

        progress_data = progress_response.json()
        # Validate required fields presence
        for field in ["status", "progress", "current_step", "message"]:
            assert field in progress_data, f"Missing '{field}' in progress response"

        # Validate field types and values
        assert progress_data["status"] in ["processing", "completed", "error"], "Invalid status value"
        assert isinstance(progress_data["progress"], (int, float)), "Progress should be a number"
        assert 0 <= progress_data["progress"] <= 100, "Progress out of valid range (0-100)"
        assert isinstance(progress_data["current_step"], str), "current_step should be string"
        assert isinstance(progress_data["message"], str), "message should be string"

    finally:
        # Cleanup: Optionally delete the task or video resource if API supports it
        # Since no delete endpoint provided for tasks, skipping cleanup
        pass


test_get_task_processing_progress()
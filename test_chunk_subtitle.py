#!/usr/bin/env python3
"""
Test chunk processing with subtitle path
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_chunk_processing():
    print("[INFO] Testing Chunk Processing with Subtitle Path")

    # Login
    token_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={"username": "test@example.com", "password": "TestPassword123!"}
    )

    if token_response.status_code == 200:
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[PASS] Authenticated")
    else:
        print("[FAIL] Authentication failed")
        return False

    # Use the test video that exists
    video_path = "episode1.mp4"

    # Process chunk
    chunk_response = requests.post(
        f"{BASE_URL}/api/process/chunk",
        headers=headers,
        json={"video_path": video_path, "start_time": 0, "end_time": 30}
    )

    print(f"[INFO] Chunk processing response: {chunk_response.status_code}")

    if chunk_response.status_code == 200:
        task_data = chunk_response.json()
        task_id = task_data.get("task_id")
        print(f"[INFO] Task started: {task_id}")

        # Poll for progress
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)

            progress_response = requests.get(
                f"{BASE_URL}/api/processing/progress/{task_id}",
                headers=headers
            )

            if progress_response.status_code == 200:
                progress = progress_response.json()
                status = progress.get("status")
                progress_pct = progress.get("progress", 0)

                print(f"[INFO] Status: {status}, Progress: {progress_pct}%")

                if "subtitle_path" in progress:
                    print(f"[PASS] Subtitle path found: {progress['subtitle_path']}")

                if status == "completed":
                    print("[INFO] Processing completed")
                    print(f"[INFO] Final data: {json.dumps(progress, indent=2)}")

                    if "subtitle_path" in progress:
                        print(f"[PASS] Subtitle path is set: {progress['subtitle_path']}")
                        return True
                    else:
                        print("[FAIL] Subtitle path not found in completed task")
                        return False

                elif status == "error":
                    print(f"[FAIL] Processing failed: {progress.get('message')}")
                    return False
            else:
                print(f"[WARN] Could not get progress: {progress_response.status_code}")

    else:
        print(f"[FAIL] Could not start chunk processing: {chunk_response.text[:200]}")
        return False

    print("[FAIL] Processing timed out")
    return False

if __name__ == "__main__":
    test_chunk_processing()
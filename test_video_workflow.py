#!/usr/bin/env python3
"""
Test video processing workflow
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_video_workflow():
    print("[INFO] Testing Video Processing Workflow")

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

    # Get available videos
    videos_response = requests.get(f"{BASE_URL}/api/videos", headers=headers)
    print(f"[INFO] Videos response: {videos_response.status_code}")

    if videos_response.status_code == 200:
        videos = videos_response.json()
        print(f"[INFO] Available videos: {len(videos)} videos")
        for video in videos[:3]:
            print(f"  - {video.get('series')}/{video.get('episode')}: {video.get('title')}")

    # Use an actual video from the list if available
    if videos_response.status_code == 200 and videos:
        # Try to find a Superstore video or use the first available one
        superstore_video = next((v for v in videos if v.get("series") == "Superstore"), None)
        if superstore_video:
            series = superstore_video.get("series", "Superstore")
            episode = superstore_video.get("episode", "1")
        else:
            # Use the first video from the list
            first_video = videos[0]
            series = first_video.get("series", "Default")
            episode = first_video.get("episode", "test_video")
    else:
        # Fallback values
        series = "Superstore"
        episode = "1"

    stream_url = f"{BASE_URL}/api/videos/{series}/{episode}"

    try:
        stream_response = requests.head(stream_url, headers=headers, timeout=5)
        print(f"[INFO] Video stream test ({series}/{episode}): {stream_response.status_code}")

        if stream_response.status_code in [200, 206]:
            print("[PASS] Video streaming endpoint works")
        else:
            print(f"[WARN] Video streaming returned: {stream_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[WARN] Video streaming test failed: {e}")

    # Test chunk processing endpoint
    try:
        chunk_response = requests.post(
            f"{BASE_URL}/api/process/chunk",
            headers=headers,
            json={"video_path": f"{series}/{episode}.mp4", "start_time": 0, "end_time": 30}
        )
        print(f"[INFO] Chunk processing response: {chunk_response.status_code}")

        if chunk_response.status_code == 200:
            task_data = chunk_response.json()
            task_id = task_data.get("task_id")
            print(f"[INFO] Task started: {task_id}")

            # Wait a bit and check progress
            time.sleep(3)

            # Get task progress
            progress_response = requests.get(
                f"{BASE_URL}/api/processing/progress/{task_id}",
                headers=headers
            )

            if progress_response.status_code == 200:
                progress = progress_response.json()
                print(f"[INFO] Task progress: {progress.get('progress', 0)}%")
                print(f"[INFO] Task status: {progress.get('status')}")

                if "subtitle_path" in progress:
                    print(f"[PASS] Subtitle path set: {progress['subtitle_path']}")
                else:
                    print("[WARN] Subtitle path not yet set in progress")
            else:
                print(f"[WARN] Could not get progress: {progress_response.status_code}")
        else:
            print(f"[WARN] Chunk processing failed: {chunk_response.text[:200]}")
    except Exception as e:
        print(f"[ERROR] Chunk processing test failed: {e}")

    return True

if __name__ == "__main__":
    test_video_workflow()
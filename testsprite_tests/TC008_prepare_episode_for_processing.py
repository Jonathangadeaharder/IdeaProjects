import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_prepare_episode_for_processing():
    url_prepare = f"{BASE_URL}/api/videos/prepare"
    # Since preparing an episode requires a video_path and no specific video_path is provided,
    # first get list of available videos to find a valid video_path.
    url_videos = f"{BASE_URL}/api/videos"
    task_id = None

    try:
        # Get available videos to find a video_path to prepare
        resp_videos = requests.get(url_videos, timeout=TIMEOUT)
        resp_videos.raise_for_status()
        videos_data = resp_videos.json()
        videos = videos_data.get("videos", [])

        assert isinstance(videos, list), "Videos should be a list"
        assert len(videos) > 0, "No available videos to test with"

        # Use first video's video_path if available, otherwise construct from available fields
        # The PRD doesn't define the exact format of video_path in the videos list,
        # so fallback to using series and episode in the path if available.
        video_path = None

        first_video = videos[0]
        # The details of video object structure is not provided, guessing keys:
        # Try keys: "video_path" or a combination of series+episode or an url
        if isinstance(first_video, dict):
            if "video_path" in first_video:
                video_path = first_video["video_path"]
            elif "series" in first_video and "episode" in first_video:
                video_path = f"{first_video['series']}/{first_video['episode']}"
            elif "path" in first_video:
                video_path = first_video["path"]

        assert video_path is not None, "Could not determine a valid video_path for preparation"

        payload = {"video_path": video_path}
        headers = {"Content-Type": "application/json"}

        resp = requests.post(url_prepare, json=payload, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        assert "task_id" in data, "Response missing 'task_id'"
        assert isinstance(data["task_id"], str) and data["task_id"], "'task_id' should be non-empty string"
        assert "status" in data, "Response missing 'status'"
        assert isinstance(data["status"], str) and data["status"], "'status' should be non-empty string"

        # Save task_id for cleanup if desired (no delete endpoint specified in PRD)
        task_id = data["task_id"]

    except requests.RequestException as e:
        assert False, f"HTTP request failed: {e}"

    except AssertionError as e:
        assert False, f"Assertion failed: {e}"


test_prepare_episode_for_processing()
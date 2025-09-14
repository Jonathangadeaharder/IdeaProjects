import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_stream_video_content_by_series_and_episode():
    # First, get a list of available videos to get a valid series and episode
    try:
        videos_resp = requests.get(f"{BASE_URL}/api/videos", timeout=TIMEOUT)
        assert videos_resp.status_code == 200, f"Expected 200 OK from /api/videos but got {videos_resp.status_code}"
        videos_data = videos_resp.json()
        assert "videos" in videos_data and isinstance(videos_data["videos"], list), "Missing or invalid videos list"
        assert len(videos_data["videos"]) > 0, "No videos available to test streaming"

        # From the videos list, select the first series with episodes if available
        # Assuming each video object structure is unknown, try to extract series and episode info:
        # The PRD doesn't specify the schema for /api/videos response items; 
        # We assume each video has keys 'series' and 'episodes' or 'episode' for simplification.
        # We'll try to find the first valid series and episode to stream.

        selected_series = None
        selected_episode = None

        for video in videos_data["videos"]:
            # Try possible keys for series and episode
            if "series" in video and "episodes" in video and isinstance(video["episodes"], list) and len(video["episodes"]) > 0:
                selected_series = video["series"]
                selected_episode = video["episodes"][0]
                break
            # fallback if video itself is a single episode with series and episode keys
            elif "series" in video and "episode" in video:
                selected_series = video["series"]
                selected_episode = video["episode"]
                break
        
        # If no appropriate structure found, fallback to example strings (best effort)
        if selected_series is None or selected_episode is None:
            selected_series = "defaultSeries"
            selected_episode = "1"

        # Stream the video content for the selected series and episode
        stream_url = f"{BASE_URL}/api/videos/stream/{selected_series}/{selected_episode}"
        stream_resp = requests.get(stream_url, timeout=TIMEOUT, stream=True)
        assert stream_resp.status_code == 200, f"Expected 200 OK streaming video but got {stream_resp.status_code}"
        content_type = stream_resp.headers.get("Content-Type", "")
        assert content_type.startswith("video/"), f"Expected video content-type but got {content_type}"

        # Check that some content is returned in the stream (at least some bytes)
        content_iter = stream_resp.iter_content(chunk_size=1024)
        first_chunk = next(content_iter, None)
        assert first_chunk is not None and len(first_chunk) > 0, "Streamed video content is empty"

    except requests.RequestException as e:
        assert False, f"Request to video streaming endpoint failed: {e}"

test_stream_video_content_by_series_and_episode()
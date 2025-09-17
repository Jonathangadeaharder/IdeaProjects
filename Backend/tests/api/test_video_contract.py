"""Contract tests for video endpoints.

These tests verify that the video API contract is maintained:
- Request/response schemas match expectations
- HTTP status codes are correct
- Required fields are present
- Data types are correct
"""
import pytest
from unittest.mock import patch, mock_open
from api.models.video import VideoInfo


@pytest.mark.asyncio
class TestVideoContract:
    """Contract tests for video API endpoints."""

    def test_get_videos_endpoint_contract(self, client):
        """Test /videos endpoint contract."""
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=['test_series']), \
             patch('os.path.isdir', return_value=True), \
             patch('glob.glob', return_value=['test_series/S01E01.mp4']):
            
            response = client.get("/videos")
            
            # Contract assertions
            assert response.status_code == 200
            data = response.json()
            
            # Should return a list
            assert isinstance(data, list)
            
            # If videos exist, verify structure
            if data:
                video = data[0]
                # Verify response structure matches VideoInfo model
                assert "series" in video
                assert "season" in video
                assert "episode" in video
                assert "title" in video
                assert "path" in video
                assert "has_subtitles" in video
                assert "duration" in video
                
                # Verify data types
                assert isinstance(video["series"], str)
                assert isinstance(video["season"], str)
                assert isinstance(video["episode"], str)
                assert isinstance(video["title"], str)
                assert isinstance(video["path"], str)
                assert isinstance(video["has_subtitles"], bool)
                assert video["duration"] is None or isinstance(video["duration"], (int, float))

    def test_stream_video_endpoint_contract(self, client):
        """Test /videos/{series}/{episode} endpoint contract."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=b'fake video data')):
            
            response = client.get("/videos/test_series/S01E01")
            
            # Should return video content or appropriate error
            # The exact status depends on implementation, but should be consistent
            assert response.status_code in [200, 404, 416]  # OK, Not Found, or Range Not Satisfiable
            
            if response.status_code == 200:
                # Should have appropriate headers for video streaming
                assert "content-type" in response.headers

    def test_stream_video_not_found_contract(self, client):
        """Test video streaming with non-existent video."""
        with patch('os.path.exists', return_value=False):
            response = client.get("/videos/nonexistent/S01E01")
            assert response.status_code == 404

    def test_get_subtitles_endpoint_contract(self, client):
        """Test /videos/subtitles/{subtitle_path} endpoint contract."""
        subtitle_content = "1\n00:00:01,000 --> 00:00:02,000\nTest subtitle\n"
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=subtitle_content)):
            
            response = client.get("/videos/subtitles/test.srt")
            
            # Contract assertions
            assert response.status_code == 200
            # Should return subtitle content
            assert len(response.content) > 0

    def test_get_subtitles_not_found_contract(self, client):
        """Test subtitle retrieval with non-existent file."""
        with patch('os.path.exists', return_value=False):
            response = client.get("/videos/subtitles/nonexistent.srt")
            assert response.status_code == 404

    def test_upload_video_endpoint_contract(self, client):
        """Test /videos/upload/{series} endpoint contract."""
        # Create a mock video file
        video_content = b"fake video content"
        files = {"video_file": ("test.mp4", video_content, "video/mp4")}
        
        with patch('os.makedirs'), \
             patch('builtins.open', mock_open()), \
             patch('os.path.exists', return_value=False):
            
            response = client.post("/videos/upload/test_series", files=files)
            
            # Contract assertions - should either succeed or fail with validation error
            assert response.status_code in [200, 422, 400]
            
            # Should return JSON
            assert "application/json" in response.headers.get("content-type", "")

    def test_upload_video_validation_contract(self, client):
        """Test video upload validation contract."""
        # Test without file
        response = client.post("/videos/upload/test_series")
        assert response.status_code == 422
        
        # Test with invalid file type
        files = {"video_file": ("test.txt", b"not a video", "text/plain")}
        response = client.post("/videos/upload/test_series", files=files)
        assert response.status_code in [422, 400]  # Should reject non-video files

    def test_upload_subtitle_endpoint_contract(self, client):
        """Test /videos/subtitle/upload endpoint contract."""
        subtitle_content = "1\n00:00:01,000 --> 00:00:02,000\nTest subtitle\n"
        files = {"subtitle_file": ("test.srt", subtitle_content.encode(), "text/plain")}
        params = {"video_path": "test_series/S01E01.mp4"}
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open()), \
             patch('os.makedirs'):
            
            response = client.post("/videos/subtitle/upload", files=files, params=params)
            
            # Contract assertions
            assert response.status_code in [200, 422, 400]
            
            # Should return JSON
            assert "application/json" in response.headers.get("content-type", "")

    def test_upload_subtitle_validation_contract(self, client):
        """Test subtitle upload validation contract."""
        # Test without file
        params = {"video_path": "test_series/S01E01.mp4"}
        response = client.post("/videos/subtitle/upload", params=params)
        assert response.status_code == 422
        
        # Test without video_path parameter
        files = {"subtitle_file": ("test.srt", b"subtitle content", "text/plain")}
        response = client.post("/videos/subtitle/upload", files=files)
        assert response.status_code == 422

    @pytest.mark.parametrize("endpoint,method,expected_content_type", [
        ("/videos", "get", "application/json"),
        ("/videos/test/S01E01", "get", None),  # Video streaming may have different content type
        ("/videos/subtitles/test.srt", "get", None),  # Subtitle files may have different content type
    ])
    def test_video_endpoints_content_type_contract(self, client, endpoint, method, expected_content_type):
        """Test that video endpoints return appropriate content types."""
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=[]), \
             patch('builtins.open', mock_open(read_data=b'test content')):
            
            if method == "get":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)
            
            if expected_content_type:
                assert expected_content_type in response.headers.get("content-type", "")
            
            # Should have some content-type header
            assert "content-type" in response.headers

    def test_video_path_validation_contract(self, client):
        """Test that video paths are properly validated."""
        # Test with invalid characters in series name
        invalid_series = "../../../etc/passwd"
        response = client.get(f"/videos/{invalid_series}/S01E01")
        # Should either sanitize or reject dangerous paths
        assert response.status_code in [400, 404, 422]
        
        # Test with invalid episode format
        response = client.get("/videos/test_series/invalid_episode")
        # Should handle gracefully
        assert response.status_code in [400, 404, 422]

    def test_video_authentication_contract(self, client):
        """Test video endpoints authentication requirements."""
        # Some video endpoints might require authentication
        # Test with token parameter
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=b'test content')):
            
            # Test without token (should work for public access or return 401)
            response = client.get("/videos/test_series/S01E01")
            assert response.status_code in [200, 401, 404]
            
            # Test with token parameter
            response = client.get("/videos/test_series/S01E01?token=test_token")
            assert response.status_code in [200, 401, 404]
"""Improved contract tests for video endpoints using async patterns.

These tests verify that the video API contract is maintained with proper async patterns.
"""
import pytest
from unittest.mock import patch, mock_open


@pytest.mark.asyncio
@pytest.mark.api
class TestVideoContractImproved:
    """Improved contract tests for video API endpoints with async patterns."""

    async def setup_authenticated_client(self, async_client):
        """Helper to create an authenticated client."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f"videotest_{unique_id}@example.com"

        # Register with proper format
        await async_client.post("/api/auth/register", json={
            "username": f"videotest_{unique_id}",
            "email": email,
            "password": "SecurePass123!"
        })

        # Login with proper format (form data, email in username field)
        login_response = await async_client.post("/api/auth/login", data={
            "username": email,  # FastAPI-Users expects email here
            "password": "SecurePass123!"
        })
        token = login_response.json()["access_token"]  # FastAPI-Users returns access_token
        return {"Authorization": f"Bearer {token}"}

    async def test_get_videos_endpoint_contract(self, async_client):
        """Test /videos endpoint contract."""
        headers = await self.setup_authenticated_client(async_client)
        
        with patch('os.path.exists', return_value=True):
            with patch('os.listdir', return_value=['test_series']):
                with patch('os.path.isdir', return_value=True):
                    with patch('glob.glob', return_value=['test_series/S01E01.mp4']):
                        response = await async_client.get("/api/videos", headers=headers)
                        
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
"""Improved contract tests for processing endpoints using async patterns.

These tests verify that the processing API contract is maintained with proper async patterns.
"""
import pytest
import uuid
from pathlib import Path
from unittest.mock import patch, Mock


@pytest.mark.asyncio
@pytest.mark.api
class TestProcessingContractImproved:
    """Improved contract tests for processing API endpoints with async patterns."""

    async def setup_authenticated_client(self, async_client):
        """Helper to create an authenticated client."""
        unique_id = str(uuid.uuid4())[:8]
        email = f"processtest_{unique_id}@example.com"

        # Register with proper format
        await async_client.post("/api/auth/register", json={
            "username": f"processtest_{unique_id}",
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

    async def test_transcribe_video_endpoint_contract(self, async_client):
        """Test /process/transcribe endpoint contract."""
        headers = await self.setup_authenticated_client(async_client)

        payload = {
            "video_path": "test_series/S01E01.mp4"
        }

        # Create a mock settings object
        from core.config import Settings
        mock_settings = Mock(spec=Settings)
        mock_settings.get_videos_path.return_value = Path('/fake/videos')
        mock_settings.default_language = "de"

        # Using a single patch context to avoid syntax issues
        with patch('pathlib.Path.exists', return_value=True):
            with patch('api.routes.processing.get_transcription_service') as mock_get_service:
                with patch('api.routes.processing.settings', mock_settings):
                    mock_service = Mock()
                    mock_service.transcribe.return_value = "task_123"
                    mock_get_service.return_value = mock_service

                    response = await async_client.post("/api/process/transcribe", json=payload, headers=headers)

                    # Contract assertions
                    assert response.status_code in [200, 202]  # OK or Accepted for async processing
                    data = response.json()

                    # Should return task information
                    assert isinstance(data, dict)
                    # Common response patterns for async tasks
                    expected_fields = ["task_id", "status", "message"]
                    assert any(field in data for field in expected_fields)
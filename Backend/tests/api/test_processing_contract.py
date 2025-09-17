"""Contract tests for processing endpoints.

These tests verify that the processing API contract is maintained:
- Request/response schemas match expectations
- HTTP status codes are correct
- Required fields are present
- Data types are correct
"""
import pytest
from pathlib import Path
from unittest.mock import patch, Mock
from api.models.processing import (
    TranscribeRequest, ProcessingStatus, FilterRequest,
    TranslateRequest, ChunkProcessingRequest
)


@pytest.mark.asyncio
class TestProcessingContract:
    """Contract tests for processing API endpoints."""

    def setup_authenticated_client(self, client):
        """Helper to create an authenticated client."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f"processtest_{unique_id}@example.com"

        # Register with proper format
        client.post("/api/auth/register", json={
            "username": f"processtest_{unique_id}",
            "email": email,
            "password": "SecurePass123!"
        })

        # Login with proper format (form data, email in username field)
        login_response = client.post("/api/auth/login", data={
            "username": email,  # FastAPI-Users expects email here
            "password": "SecurePass123!"
        })
        token = login_response.json()["access_token"]  # FastAPI-Users returns access_token
        return {"Authorization": f"Bearer {token}"}

    def test_transcribe_video_endpoint_contract(self, client):
        """Test /process/transcribe endpoint contract."""
        headers = self.setup_authenticated_client(client)

        payload = {
            "video_path": "test_series/S01E01.mp4"
        }

        # Create a mock settings object
        from core.config import Settings
        mock_settings = Mock(spec=Settings)
        mock_settings.get_videos_path.return_value = Path('/fake/videos')
        mock_settings.default_language = "de"

        with patch('pathlib.Path.exists', return_value=True), \
             patch('api.routes.processing.get_transcription_service') as mock_get_service, \
             patch('api.routes.processing.settings', mock_settings):

            mock_service = Mock()
            mock_service.transcribe.return_value = "task_123"
            mock_get_service.return_value = mock_service

            response = client.post("/api/process/transcribe", json=payload, headers=headers)

            # Contract assertions
            assert response.status_code in [200, 202]  # OK or Accepted for async processing
            data = response.json()

            # Should return task information
            assert isinstance(data, dict)
            # Common response patterns for async tasks
            expected_fields = ["task_id", "status", "message"]
            assert any(field in data for field in expected_fields)

    def test_transcribe_video_validation_contract(self, client):
        """Test transcribe video validation contract."""
        headers = self.setup_authenticated_client(client)
        
        # Test without video_path
        response = client.post("/api/process/transcribe", json={}, headers=headers)
        assert response.status_code == 422
        
        # Test with empty video_path
        response = client.post("/api/process/transcribe", json={"video_path": ""}, headers=headers)
        assert response.status_code == 422
        
        # Test with invalid video_path (non-video extension)
        response = client.post("/api/process/transcribe", json={"video_path": "test.txt"}, headers=headers)
        assert response.status_code == 422

    def test_process_chunk_endpoint_contract(self, client):
        """Test /process/chunk endpoint contract."""
        headers = self.setup_authenticated_client(client)
        
        payload = {
            "video_path": "test_series/S01E01.mp4",
            "start_time": 10.5,
            "end_time": 30.0
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            response = client.post("/api/process/chunk", json=payload, headers=headers)
            
            # Contract assertions
            assert response.status_code in [200, 202, 404]  # OK, Accepted, or Not Found
            
            if response.status_code in [200, 202]:
                data = response.json()
                assert isinstance(data, dict)

    def test_process_chunk_validation_contract(self, client):
        """Test process chunk validation contract."""
        headers = self.setup_authenticated_client(client)
        
        # Test without required fields
        response = client.post("/api/process/chunk", json={}, headers=headers)
        assert response.status_code == 422
        
        # Test with invalid time range (start > end)
        response = client.post("/api/process/chunk", json={
            "video_path": "test_series/S01E01.mp4",
            "start_time": 30.0,
            "end_time": 10.0
        }, headers=headers)
        assert response.status_code == 422
        
        # Test with negative times
        response = client.post("/api/process/chunk", json={
            "video_path": "test_series/S01E01.mp4",
            "start_time": -5.0,
            "end_time": 10.0
        }, headers=headers)
        assert response.status_code == 422

    def test_filter_subtitles_endpoint_contract(self, client):
        """Test /process/filter-subtitles endpoint contract."""
        headers = self.setup_authenticated_client(client)

        payload = {
            "video_path": "test_series/S01E01.mp4"
        }

        # Create a mock settings object
        from core.config import Settings
        mock_settings = Mock(spec=Settings)
        mock_settings.get_videos_path.return_value = Path('/fake/videos')
        mock_settings.default_language = "de"

        with patch('pathlib.Path.exists', return_value=True), \
             patch('api.routes.processing.settings', mock_settings):
            response = client.post("/api/process/filter-subtitles", json=payload, headers=headers)

            # Contract assertions
            assert response.status_code in [200, 202, 404]  # OK, Accepted, or Not Found

            if response.status_code in [200, 202]:
                data = response.json()
                assert isinstance(data, dict)

    def test_filter_subtitles_validation_contract(self, client):
        """Test filter subtitles validation contract."""
        headers = self.setup_authenticated_client(client)

        # Test without video_path
        response = client.post("/api/process/filter-subtitles", json={}, headers=headers)
        assert response.status_code == 422

        # Test with empty video_path
        response = client.post("/api/process/filter-subtitles", json={"video_path": ""}, headers=headers)
        assert response.status_code == 422

    def test_translate_subtitles_endpoint_contract(self, client):
        """Test /process/translate-subtitles endpoint contract."""
        headers = self.setup_authenticated_client(client)
        
        payload = {
            "video_path": "test_series/S01E01.mp4",
            "source_lang": "en",
            "target_lang": "es"
        }
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('services.translationservice.factory.TranslationServiceFactory.create_service') as mock_factory:
            
            mock_service = Mock()
            mock_service.translate.return_value = "task_456"
            mock_factory.return_value = mock_service
            
            response = client.post("/api/process/translate-subtitles", json=payload, headers=headers)
            
            # Contract assertions
            assert response.status_code in [200, 202, 404]  # OK, Accepted, or Not Found
            
            if response.status_code in [200, 202]:
                data = response.json()
                assert isinstance(data, dict)

    def test_translate_subtitles_validation_contract(self, client):
        """Test translate subtitles validation contract."""
        headers = self.setup_authenticated_client(client)

        # Create a mock settings object
        from core.config import Settings
        mock_settings = Mock(spec=Settings)
        mock_settings.get_videos_path.return_value = Path('/fake/videos')
        mock_settings.default_language = "de"

        with patch('pathlib.Path.exists', return_value=True), \
             patch('api.routes.processing.settings', mock_settings):

            # Test without required fields
            response = client.post("/api/process/translate-subtitles", json={}, headers=headers)
            assert response.status_code == 422

            # Test with invalid language codes
            response = client.post("/api/process/translate-subtitles", json={
                "video_path": "test_series/S01E01.mp4",
                "source_lang": "invalid",
                "target_lang": "es"
            }, headers=headers)
            assert response.status_code == 422

            # Test with same source and target language
            response = client.post("/api/process/translate-subtitles", json={
                "video_path": "test_series/S01E01.mp4",
                "source_lang": "en",
                "target_lang": "en"
            }, headers=headers)
            assert response.status_code == 422

    def test_prepare_episode_endpoint_contract(self, client):
        """Test /process/prepare-episode endpoint contract."""
        headers = self.setup_authenticated_client(client)
        
        payload = {
            "video_path": "test_series/S01E01.mp4"
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            response = client.post("/api/process/prepare-episode", json=payload, headers=headers)
            
            # Contract assertions
            assert response.status_code in [200, 202, 404]  # OK, Accepted, or Not Found
            
            if response.status_code in [200, 202]:
                data = response.json()
                assert isinstance(data, dict)

    def test_full_pipeline_endpoint_contract(self, client):
        """Test /process/full-pipeline endpoint contract."""
        headers = self.setup_authenticated_client(client)

        payload = {
            "video_path": "test_series/S01E01.mp4",
            "source_lang": "en",
            "target_lang": "es"
        }

        with patch('pathlib.Path.exists', return_value=True):
            response = client.post("/api/process/full-pipeline", json=payload, headers=headers)

            # Contract assertions
            assert response.status_code in [200, 202, 404]  # OK, Accepted, or Not Found

            if response.status_code in [200, 202]:
                data = response.json()
                assert isinstance(data, dict)
                # Should contain task or pipeline information
                expected_fields = ["task_id", "pipeline_id", "status", "message"]
                assert any(field in data for field in expected_fields)

    def test_full_pipeline_validation_contract(self, client):
        """Test full pipeline validation contract."""
        headers = self.setup_authenticated_client(client)

        # Test without video_path
        response = client.post("/api/process/full-pipeline", json={}, headers=headers)
        assert response.status_code == 422

        # Test with invalid language codes
        response = client.post("/api/process/full-pipeline", json={
            "video_path": "test_series/S01E01.mp4",
            "source_lang": "invalid",
            "target_lang": "es"
        }, headers=headers)
        assert response.status_code == 422

    def test_get_task_progress_endpoint_contract(self, client):
        """Test /process/progress/{task_id} endpoint contract."""
        headers = self.setup_authenticated_client(client)
        
        task_id = "test_task_123"
        
        with patch('core.database.get_async_session'):
            response = client.get(f"/api/process/progress/{task_id}", headers=headers)
            
            # Contract assertions
            assert response.status_code in [200, 404]  # OK or Not Found
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, dict)
                
                # Should contain progress information
                expected_fields = ["task_id", "status", "progress", "message", "result"]
                assert any(field in data for field in expected_fields)
                
                # If status is present, should be valid
                if "status" in data:
                    valid_statuses = ["pending", "running", "completed", "failed", "cancelled"]
                    assert data["status"] in valid_statuses

    def test_get_task_progress_validation_contract(self, client):
        """Test task progress validation contract."""
        headers = self.setup_authenticated_client(client)
        
        # Test with empty task_id
        response = client.get("/api/process/progress/", headers=headers)
        assert response.status_code == 404  # Should be treated as missing path
        
        # Test with invalid task_id format
        response = client.get("/api/process/progress/invalid-task-id-format", headers=headers)
        assert response.status_code in [400, 404]  # Bad Request or Not Found

    def test_processing_endpoints_authentication_contract(self, client):
        """Test that processing endpoints require authentication."""
        # Test without authentication
        endpoints_methods = [
            ("/api/process/transcribe", "post"),
            ("/api/process/chunk", "post"),
            ("/api/process/filter-subtitles", "post"),
            ("/api/process/translate-subtitles", "post"),
            ("/api/process/prepare-episode", "post"),
            ("/api/process/full-pipeline", "post"),
            ("/api/process/progress/test_task", "get"),
        ]
        
        for endpoint, method in endpoints_methods:
            if method == "get":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            # Should require authentication (401 for missing auth header with FastAPI-Users)
            assert response.status_code == 401

    @pytest.mark.parametrize("endpoint,method", [
        ("/api/process/transcribe", "post"),
        ("/api/process/chunk", "post"),
        ("/api/process/filter-subtitles", "post"),
        ("/api/process/translate-subtitles", "post"),
        ("/api/process/prepare-episode", "post"),
        ("/api/process/full-pipeline", "post"),
        ("/api/process/progress/test_task", "get"),
    ])
    def test_processing_endpoints_content_type_contract(self, client, endpoint, method):
        """Test that processing endpoints return JSON content type."""
        headers = self.setup_authenticated_client(client)
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('services.transcriptionservice.factory.TranscriptionServiceFactory.create_service') as mock_factory, \
             patch('services.translationservice.factory.TranslationServiceFactory.create_service') as mock_trans_factory, \
             patch('core.database.get_async_session'):
            
            mock_service = Mock()
            mock_service.transcribe.return_value = "task_123"
            mock_service.translate.return_value = "task_456"
            mock_factory.return_value = mock_service
            mock_trans_factory.return_value = mock_service
            
            if method == "get":
                response = client.get(endpoint, headers=headers)
            else:
                if "transcribe" in endpoint or "prepare-episode" in endpoint:
                    response = client.post(endpoint, json={"video_path": "test.mp4"}, headers=headers)
                elif "chunk" in endpoint:
                    response = client.post(endpoint, json={
                        "video_path": "test.mp4",
                        "start_time": 0,
                        "end_time": 10
                    }, headers=headers)
                elif "translate" in endpoint:
                    response = client.post(endpoint, json={
                        "video_path": "test.mp4",
                        "source_lang": "en",
                        "target_lang": "es"
                    }, headers=headers)
                elif "full-pipeline" in endpoint:
                    response = client.post(endpoint, json={
                        "video_path": "test.mp4",
                        "source_lang": "en",
                        "target_lang": "es"
                    }, headers=headers)
                else:
                    response = client.post(endpoint, json={"video_path": "test.mp4"}, headers=headers)
            
            # Should return JSON content type (even for errors)
            assert "application/json" in response.headers.get("content-type", "")

    def test_processing_async_task_patterns_contract(self, client):
        """Test that processing endpoints follow async task patterns."""
        headers = self.setup_authenticated_client(client)
        
        # Test that long-running operations return task information
        with patch('pathlib.Path.exists', return_value=True), \
             patch('services.transcriptionservice.factory.TranscriptionServiceFactory.create_service') as mock_factory:
            
            mock_service = Mock()
            mock_service.transcribe.return_value = "task_123"
            mock_factory.return_value = mock_service
            
            response = client.post("/api/process/transcribe", json={
                "video_path": "test_series/S01E01.mp4"
            }, headers=headers)
            
            if response.status_code in [200, 202]:
                data = response.json()
                # Should provide a way to track the task
                task_tracking_fields = ["task_id", "id", "tracking_id"]
                assert any(field in data for field in task_tracking_fields)
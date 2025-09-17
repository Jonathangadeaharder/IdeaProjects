"""Integration tests for video processing pipeline"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import os
from pathlib import Path


class TestVideoProcessingIntegration:
    """Integration tests for video processing workflow"""
    
    @pytest.fixture
    def sample_video_file(self):
        """Create a temporary video file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            # Write minimal video file content (just for testing)
            f.write(b'fake video content')
            yield f.name
        os.unlink(f.name)
    
    @pytest.fixture
    def mock_transcription_result(self):
        """Mock transcription service result"""
        from services.transcriptionservice.interface import TranscriptionResult, TranscriptionSegment
        
        segments = [
            TranscriptionSegment(
                start_time=0.0,
                end_time=2.5,
                text="Hello world, this is a test."
            ),
            TranscriptionSegment(
                start_time=2.5,
                end_time=5.0,
                text="We are testing the transcription service."
            )
        ]
        
        return TranscriptionResult(
            full_text="Hello world, this is a test. We are testing the transcription service.",
            segments=segments,
            language="en"
        )
    
    @pytest.mark.asyncio
    async def test_video_upload_and_processing(self, async_client, sample_video_file, mock_transcription_result):
        """Test complete video upload and processing workflow"""
        # First, authenticate
        await async_client.post("/api/auth/register", json={"username": "videouser", "password": "TestPass123"})
        login_resp = await async_client.post("/api/auth/login", json={"username": "videouser", "password": "TestPass123"})
        token = login_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Mock the transcription service
        with patch('services.transcriptionservice.transcription_service.TranscriptionService.transcribe_video') as mock_transcribe:
            mock_transcribe.return_value = mock_transcription_result
            
            # Upload video file
            with open(sample_video_file, 'rb') as f:
                files = {'file': ('test_video.mp4', f, 'video/mp4')}
                response = await async_client.post(
                    "/api/videos/upload",
                    files=files,
                    headers=headers
                )
        
        # Assert upload success
        assert response.status_code == 200
        video_data = response.json()
        assert 'id' in video_data
        assert video_data['filename'] == 'test_video.mp4'
        assert video_data['status'] == 'uploaded'
    
    @pytest.mark.asyncio
    async def test_video_transcription_endpoint(self, async_client, mock_transcription_result):
        """Test video transcription endpoint"""
        # Authenticate
        await async_client.post("/api/auth/register", json={"username": "transcribeuser", "password": "TestPass123"})
        login_resp = await async_client.post("/api/auth/login", json={"username": "transcribeuser", "password": "TestPass123"})
        token = login_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Mock transcription service
        with patch('services.transcriptionservice.transcription_service.TranscriptionService.transcribe_video') as mock_transcribe:
            mock_transcribe.return_value = mock_transcription_result
            
            # Request transcription
            response = await async_client.post(
                "/api/videos/1/transcribe",
                headers=headers
            )
        
        # Assert transcription success
        assert response.status_code == 200
        transcription_data = response.json()
        assert 'segments' in transcription_data
        assert len(transcription_data['segments']) == 2
        assert transcription_data['language'] == 'en'
    
    @pytest.mark.asyncio
    async def test_subtitle_generation(self, async_client, mock_transcription_result):
        """Test SRT subtitle generation"""
        # Authenticate
        await async_client.post("/api/auth/register", json={"username": "subtitleuser", "password": "TestPass123"})
        login_resp = await async_client.post("/api/auth/login", json={"username": "subtitleuser", "password": "TestPass123"})
        token = login_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Mock transcription service
        with patch('services.transcriptionservice.transcription_service.TranscriptionService.transcribe_video') as mock_transcribe:
            mock_transcribe.return_value = mock_transcription_result
            
            # Request subtitle generation
            response = await async_client.post(
                "/api/videos/1/subtitles",
                json={"format": "srt"},
                headers=headers
            )
        
        # Assert subtitle generation success
        assert response.status_code == 200
        subtitle_data = response.json()
        assert 'content' in subtitle_data
        assert 'format' in subtitle_data
        assert subtitle_data['format'] == 'srt'
        
        # Verify SRT format
        srt_content = subtitle_data['content']
        assert '1' in srt_content  # Subtitle number
        assert '00:00:00,000 --> 00:00:02,500' in srt_content  # Timestamp
        assert 'Hello world, this is a test.' in srt_content  # Text
    
    @pytest.mark.asyncio
    async def test_vocabulary_filtering(self, async_client, mock_transcription_result):
        """Test vocabulary filtering from transcription"""
        # Authenticate
        await async_client.post("/api/auth/register", json={"username": "filteruser", "password": "TestPass123"})
        login_resp = await async_client.post("/api/auth/login", json={"username": "filteruser", "password": "TestPass123"})
        token = login_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Mock services
        with patch('services.transcriptionservice.transcription_service.TranscriptionService.transcribe_video') as mock_transcribe:
            with patch('services.filterservice.filter_service.FilterService.filter_vocabulary') as mock_filter:
                mock_transcribe.return_value = mock_transcription_result
                mock_filter.return_value = {
                    'unknown_words': ['hello', 'world', 'testing'],
                    'known_words': ['this', 'is', 'a', 'the'],
                    'difficulty_levels': {'A1': 2, 'A2': 1, 'B1': 0, 'B2': 0}
                }
                
                # Request vocabulary filtering
                response = await async_client.post(
                    "/api/videos/1/vocabulary",
                    json={"user_level": "A2"},
                    headers=headers
                )
        
        # Assert filtering success
        assert response.status_code == 200
        vocab_data = response.json()
        assert 'unknown_words' in vocab_data
        assert 'known_words' in vocab_data
        assert 'difficulty_levels' in vocab_data
        assert len(vocab_data['unknown_words']) == 3
    
    @pytest.mark.asyncio
    async def test_translation_service(self, async_client, mock_transcription_result):
        """Test translation service integration"""
        # Authenticate
        await async_client.post("/api/auth/register", json={"username": "translateuser", "password": "TestPass123"})
        login_resp = await async_client.post("/api/auth/login", json={"username": "translateuser", "password": "TestPass123"})
        token = login_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Mock translation service
        with patch('services.translationservice.translation_service.TranslationService.translate_text') as mock_translate:
            mock_translate.return_value = {
                'translated_text': 'Hallo Welt, das ist ein Test.',
                'source_language': 'en',
                'target_language': 'de',
                'confidence': 0.98
            }
            
            # Request translation
            response = await async_client.post(
                "/api/translate",
                json={
                    "text": "Hello world, this is a test.",
                    "target_language": "de"
                },
                headers=headers
            )
        
        # Assert translation success
        assert response.status_code == 200
        translation_data = response.json()
        assert 'translated_text' in translation_data
        assert translation_data['translated_text'] == 'Hallo Welt, das ist ein Test.'
        assert translation_data['target_language'] == 'de'
    
    @pytest.mark.asyncio
    async def test_video_list_endpoint(self, async_client):
        """Test video listing endpoint"""
        # Authenticate
        await async_client.post("/api/auth/register", json={"username": "listuser", "password": "TestPass123"})
        login_resp = await async_client.post("/api/auth/login", json={"username": "listuser", "password": "TestPass123"})
        token = login_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Request video list
        response = await async_client.get("/api/videos", headers=headers)
        
        # Assert list success
        assert response.status_code == 200
        videos_data = response.json()
        assert isinstance(videos_data, list)
    
    @pytest.mark.asyncio
    async def test_video_processing_error_handling(self, async_client, sample_video_file):
        """Test error handling in video processing"""
        # Authenticate
        await async_client.post("/api/auth/register", json={"username": "erroruser", "password": "TestPass123"})
        login_resp = await async_client.post("/api/auth/login", json={"username": "erroruser", "password": "TestPass123"})
        token = login_resp.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Mock transcription service to raise an error
        with patch('services.transcriptionservice.transcription_service.TranscriptionService.transcribe_video') as mock_transcribe:
            mock_transcribe.side_effect = Exception("Transcription failed")
            
            # Request transcription that should fail
            response = await async_client.post(
                "/api/videos/1/transcribe",
                headers=headers
            )
        
        # Assert error handling
        assert response.status_code == 500
        error_data = response.json()
        assert 'detail' in error_data
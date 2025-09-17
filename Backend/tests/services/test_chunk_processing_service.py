"""
Unit tests for ChunkProcessingService
Tests the refactored chunk processing business logic
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import asyncio
from pathlib import Path
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from services.processing.chunk_processor import ChunkProcessingService, ChunkProcessingError
from api.models.processing import ProcessingStatus
from database.models import User


@pytest.mark.asyncio
class TestChunkProcessingService:
    """Test suite for ChunkProcessingService"""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock all external dependencies"""
        with patch('services.processing.chunk_processor.get_transcription_service') as mock_transcription, \
             patch('services.processing.chunk_processor.get_user_filter_chain') as mock_filter_chain, \
             patch('services.processing.chunk_processor.get_auth_service') as mock_auth_service, \
             patch('services.processing.chunk_processor.settings') as mock_settings:
            
            # Mock settings
            mock_settings.get_videos_path.return_value = Path("/test/videos")
            
            # Mock transcription service
            mock_transcription_instance = Mock()
            mock_transcription_instance.is_initialized = True
            mock_transcription.return_value = mock_transcription_instance
            
            # Mock auth service
            mock_auth_service_instance = Mock()
            mock_auth_service.return_value = mock_auth_service_instance
            
            # Mock database connection
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1, "testuser", "test@example.com")
            mock_auth_service_instance.db_manager.get_connection.return_value.__enter__.return_value = mock_conn
            
            # Mock session validation
            mock_auth_service_instance.validate_session.return_value = True
            
            # Mock filter chain
            mock_chain = Mock()
            mock_filter_chain.return_value = mock_chain
            
            yield {
                'transcription': mock_transcription,
                'filter_chain': mock_filter_chain,
                'auth_service': mock_auth_service,
                'settings': mock_settings,
                'transcription_instance': mock_transcription_instance,
                'auth_service_instance': mock_auth_service_instance,
                'chain': mock_chain
            }
    
    @pytest.fixture
    def service(self):
        """Create ChunkProcessingService instance"""
        return ChunkProcessingService()
    
    @pytest.fixture
    def sample_task_progress(self):
        """Sample task progress dictionary"""
        return {}
    
    
    async def test_process_chunk_happy_path(self, service, mock_dependencies, sample_task_progress):
        """Test successful chunk processing"""
        # Setup test data
        video_path = "test_video.mp4"
        start_time = 0.0
        end_time = 30.0
        user_id = 1
        task_id = "test_task_123"
        
        # Mock file system
        with patch('services.processing.chunk_processor.Path') as mock_path:
            mock_video_file = Mock()
            mock_video_file.is_absolute.return_value = False
            mock_video_file.exists.return_value = True
            mock_video_file.parent = Path("/test/videos")
            mock_video_file.stem = "test_video"
            mock_path.return_value = mock_video_file
            
            # Mock SRT files discovery
            mock_srt_file = Mock()
            mock_srt_file.name = "test_video.srt"
            mock_srt_file.stem = "test_video"
            mock_srt_file.stat.return_value.st_size = 1024
            mock_video_file.parent.glob.return_value = [mock_srt_file]
            
            # Mock filter chain result
            mock_dependencies['chain'].process_file.return_value = {
                'blocking_words': [Mock(word='schwierig'), Mock(word='kompliziert')],
                'learning_subtitles': [],
                'statistics': {'segments_parsed': 10, 'total_words': 50}
            }
            
            # Mock SRT parser
            with patch('services.processing.chunk_processor.SRTParser') as mock_srt_parser:
                mock_parser = Mock()
                mock_srt_parser.return_value = mock_parser
                mock_parser.parse_file.return_value = []
                mock_parser.save_segments.return_value = None
                
                # Execute
                await service.process_chunk(
                    video_path=video_path,
                    start_time=start_time,
                    end_time=end_time,
                    user_id=user_id,
                    task_id=task_id,
                    task_progress=sample_task_progress
                )
        
        # Verify task completion
        assert task_id in sample_task_progress
        assert sample_task_progress[task_id].status == "completed"
        assert sample_task_progress[task_id].progress == 100.0
        assert len(sample_task_progress[task_id].vocabulary) == 2
    
    
    async def test_process_chunk_user_not_found(self, service, mock_dependencies, sample_task_progress):
        """Test chunk processing when user not found"""
        # Mock user not found
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # User not found
        mock_dependencies['auth_service_instance'].db_manager.get_connection.return_value.__enter__.return_value = mock_conn
        
        with patch('services.processing.chunk_processor.Path'):
            with pytest.raises(Exception, match="User with ID 999 not found"):
                await service.process_chunk(
                    video_path="test.mp4",
                    start_time=0.0,
                    end_time=30.0,
                    user_id=999,
                    task_id="test_task",
                    task_progress=sample_task_progress
                )
    
    
    async def test_process_chunk_invalid_session(self, service, mock_dependencies, sample_task_progress):
        """Test chunk processing with invalid session token"""
        # Mock invalid session
        mock_dependencies['auth_service_instance'].validate_session.side_effect = Exception("Invalid session")
        
        with patch('services.processing.chunk_processor.Path'):
            with pytest.raises(Exception, match="Authentication failed"):
                await service.process_chunk(
                    video_path="test.mp4",
                    start_time=0.0,
                    end_time=30.0,
                    user_id=1,
                    task_id="test_task",
                    task_progress=sample_task_progress,
                    session_token="invalid_token"
                )
    
    
    async def test_process_chunk_missing_srt_file(self, service, mock_dependencies, sample_task_progress):
        """Test chunk processing when SRT file is missing"""
        with patch('services.processing.chunk_processor.Path') as mock_path:
            mock_video_file = Mock()
            mock_video_file.is_absolute.return_value = False
            mock_video_file.exists.return_value = True
            mock_video_file.parent = Path("/test/videos")
            mock_video_file.stem = "test_video"
            mock_path.return_value = mock_video_file
            
            # Mock no SRT files found
            mock_video_file.parent.glob.return_value = []
            
            with pytest.raises(Exception, match="No original SRT file found"):
                await service.process_chunk(
                    video_path="test_video.mp4",
                    start_time=0.0,
                    end_time=30.0,
                    user_id=1,
                    task_id="test_task",
                    task_progress=sample_task_progress
                )
    
    
    async def test_process_chunk_filter_error(self, service, mock_dependencies, sample_task_progress):
        """Test chunk processing when filter chain fails"""
        with patch('services.processing.chunk_processor.Path') as mock_path:
            mock_video_file = Mock()
            mock_video_file.is_absolute.return_value = False
            mock_video_file.exists.return_value = True
            mock_video_file.parent = Path("/test/videos")
            mock_video_file.stem = "test_video"
            mock_path.return_value = mock_video_file
            
            # Mock SRT file exists
            mock_srt_file = Mock()
            mock_srt_file.name = "test_video.srt"
            mock_srt_file.stem = "test_video"
            mock_video_file.parent.glob.return_value = [mock_srt_file]
            
            # Mock filter chain error
            mock_dependencies['chain'].process_file.return_value = {
                'statistics': {'error': 'Filter processing failed'}
            }
            
            with pytest.raises(Exception, match="Filter processing failed"):
                await service.process_chunk(
                    video_path="test_video.mp4",
                    start_time=0.0,
                    end_time=30.0,
                    user_id=1,
                    task_id="test_task",
                    task_progress=sample_task_progress
                )
    
    def test_srt_file_selection_exact_match(self, service):
        """Test SRT file selection logic with exact filename match"""
        video_stem = "episode_01"
        srt_files = [
            Mock(stem="episode_01", stat=Mock(return_value=Mock(st_size=1024))),
            Mock(stem="episode_02", stat=Mock(return_value=Mock(st_size=2048))),
            Mock(stem="full_season", stat=Mock(return_value=Mock(st_size=5000)))
        ]
        
        best_srt = service._select_best_srt_file(srt_files, video_stem)
        assert best_srt.stem == "episode_01"
    
    def test_srt_file_selection_partial_match(self, service):
        """Test SRT file selection logic with partial filename match"""
        video_stem = "S01E01_episode_name"
        srt_files = [
            Mock(stem="S01E01", stat=Mock(return_value=Mock(st_size=1024))),
            Mock(stem="episode_name", stat=Mock(return_value=Mock(st_size=2048))),
            Mock(stem="full_season", stat=Mock(return_value=Mock(st_size=5000)))
        ]
        
        best_srt = service._select_best_srt_file(srt_files, video_stem)
        # Should prefer the longer matching stem
        assert best_srt.stem == "episode_name"
    
    def test_srt_file_selection_fallback_largest(self, service):
        """Test SRT file selection fallback to largest file"""
        video_stem = "unknown_video"
        srt_files = [
            Mock(stem="episode_01", stat=Mock(return_value=Mock(st_size=1024))),
            Mock(stem="episode_02", stat=Mock(return_value=Mock(st_size=2048))),
            Mock(stem="full_season", stat=Mock(return_value=Mock(st_size=5000)))
        ]
        
        best_srt = service._select_best_srt_file(srt_files, video_stem)
        # Should fallback to largest file
        assert best_srt.stem == "full_season"
    
    
    async def test_process_chunk_transcription_service_unavailable(self, service, mock_dependencies, sample_task_progress):
        """Test chunk processing when transcription service is unavailable"""
        # Mock transcription service not available
        mock_dependencies['transcription'].return_value = None
        
        with patch('services.processing.chunk_processor.Path') as mock_path:
            mock_video_file = Mock()
            mock_video_file.is_absolute.return_value = False
            mock_video_file.exists.return_value = True
            mock_path.return_value = mock_video_file
            
            await service.process_chunk(
                video_path="test.mp4",
                start_time=0.0,
                end_time=30.0,
                user_id=1,
                task_id="test_task",
                task_progress=sample_task_progress
            )
        
        # Should set error status
        assert sample_task_progress["test_task"].status == "error"
        assert "Transcription service is not available" in sample_task_progress["test_task"].message

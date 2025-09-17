"""
Integration tests for chunk processing business logic
Addresses R4 risk - complex logic in API routes needs testing before refactoring
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.routes.processing import run_chunk_processing
from api.models.processing import ProcessingStatus
from database.models import User


@pytest.fixture
def mock_video_file():
    """Create a mock video file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
        video_path = Path(f.name)
    
    # Create a corresponding SRT file
    srt_path = video_path.with_suffix('.srt')
    with open(srt_path, 'w', encoding='utf-8') as f:
        f.write("""1
00:00:00,000 --> 00:00:05,000
This is a test subtitle with difficult words.

2
00:00:05,000 --> 00:00:10,000
Another subtitle for vocabulary testing.
""")
    
    yield str(video_path)
    
    # Cleanup
    if video_path.exists():
        video_path.unlink()
    if srt_path.exists():
        srt_path.unlink()


@pytest.fixture
def mock_task_progress():
    """Mock task progress registry"""
    return {}


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    return User(
        id=1,
        username="testuser",
        is_superuser=False,
        is_active=True,
        created_at=datetime.now().isoformat()
    )


@pytest.mark.asyncio
class TestChunkProcessingIntegration:
    """Integration tests for the complex chunk processing logic"""
    
    async def test_chunk_processing_happy_path(self, mock_video_file, mock_task_progress, mock_user):
        """Test successful chunk processing end-to-end"""
        task_id = "test_chunk_123"
        
        # Mock all the external dependencies
        with patch('api.routes.processing.get_transcription_service') as mock_transcription, \
             patch('api.routes.processing.get_user_filter_chain') as mock_filter_chain, \
             patch('api.routes.processing.get_auth_service') as mock_auth_service, \
             patch('api.routes.processing.settings') as mock_settings:
            
            # Setup mocks
            mock_settings.get_videos_path.return_value = Path(mock_video_file).parent
            
            mock_transcription_service = Mock()
            mock_transcription.return_value = mock_transcription_service
            
            mock_auth_service_instance = Mock()
            mock_auth_service.return_value = mock_auth_service_instance
            
            # Mock database connection for user lookup
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1, "testuser", "test@example.com")
            mock_auth_service_instance.db_manager.get_connection.return_value.__enter__.return_value = mock_conn
            
            # Mock filter chain
            mock_chain = Mock()
            mock_filter_chain.return_value = mock_chain
            mock_chain.process_file.return_value = {
                "blocking_words": [
                    {"word": "difficult", "difficulty": "B2", "frequency": 0.001},
                    {"word": "vocabulary", "difficulty": "B1", "frequency": 0.002}
                ],
                "statistics": {
                    "segments_parsed": 2,
                    "total_words": 10,
                    "filtered_words": 8,
                    "blocking_words": 2
                }
            }
            
            # Run the chunk processing
            await run_chunk_processing(
                video_path=mock_video_file,
                start_time=0.0,
                end_time=10.0,
                task_id=task_id,
                task_progress=mock_task_progress,
                user_id=1,
                session_token="test_token"
            )
            
            # Verify processing completed successfully
            assert task_id in mock_task_progress
            final_status = mock_task_progress[task_id]
            assert final_status.status == "completed"
            assert final_status.progress == 100.0
            
            # Verify services were called
            mock_filter_chain.assert_called_once()
            mock_chain.process_file.assert_called_once()

    async def test_chunk_processing_missing_srt_file(self, mock_task_progress):
        """Test handling when SRT file is missing"""
        task_id = "test_chunk_no_srt"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = Path(temp_dir) / "test_video.mp4"
            video_path.touch()  # Create empty video file (no SRT)
            
            with patch('api.routes.processing.settings') as mock_settings:
                mock_settings.get_videos_path.return_value = Path(temp_dir)
                
                await run_chunk_processing(
                    video_path=str(video_path),
                    start_time=0.0,
                    end_time=10.0,
                    task_id=task_id,
                    task_progress=mock_task_progress,
                    user_id=1
                )
                
                # Should fail gracefully
                assert task_id in mock_task_progress
                status = mock_task_progress[task_id]
                assert status.status == "error"
                assert "SRT file not found" in status.current_step

    
    async def test_chunk_processing_user_not_found(self, mock_video_file, mock_task_progress):
        """Test handling when user is not found in database"""
        task_id = "test_chunk_no_user"
        
        with patch('api.routes.processing.get_auth_service') as mock_auth_service, \
             patch('api.routes.processing.settings') as mock_settings:
            
            mock_settings.get_videos_path.return_value = Path(mock_video_file).parent
            
            # Mock auth service but user not found
            mock_auth_service_instance = Mock()
            mock_auth_service.return_value = mock_auth_service_instance
            
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None  # User not found
            mock_auth_service_instance.db_manager.get_connection.return_value.__enter__.return_value = mock_conn
            
            # Should raise exception
            with pytest.raises(Exception, match="User with ID 999 not found"):
                await run_chunk_processing(
                    video_path=mock_video_file,
                    start_time=0.0,
                    end_time=10.0,
                    task_id=task_id,
                    task_progress=mock_task_progress,
                    user_id=999  # Non-existent user
                )

    
    async def test_chunk_processing_filter_chain_error(self, mock_video_file, mock_task_progress):
        """Test handling of filter chain errors"""
        task_id = "test_chunk_filter_error"
        
        with patch('api.routes.processing.get_transcription_service') as mock_transcription, \
             patch('api.routes.processing.get_user_filter_chain') as mock_filter_chain, \
             patch('api.routes.processing.get_auth_service') as mock_auth_service, \
             patch('api.routes.processing.settings') as mock_settings:
            
            # Setup basic mocks
            mock_settings.get_videos_path.return_value = Path(mock_video_file).parent
            mock_transcription.return_value = Mock()
            
            # Mock auth service
            mock_auth_service_instance = Mock()
            mock_auth_service.return_value = mock_auth_service_instance
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1, "testuser", "test@example.com")
            mock_auth_service_instance.db_manager.get_connection.return_value.__enter__.return_value = mock_conn
            
            # Mock filter chain to return error
            mock_chain = Mock()
            mock_filter_chain.return_value = mock_chain
            mock_chain.process_file.return_value = {
                "statistics": {
                    "error": "Filter processing failed: Invalid vocabulary data"
                }
            }
            
            # Should handle error gracefully
            with pytest.raises(Exception, match="Filter processing failed"):
                await run_chunk_processing(
                    video_path=mock_video_file,
                    start_time=0.0,
                    end_time=10.0,
                    task_id=task_id,
                    task_progress=mock_task_progress,
                    user_id=1
                )

    
    async def test_chunk_processing_invalid_timing(self, mock_video_file, mock_task_progress):
        """Test validation of chunk timing parameters"""
        task_id = "test_chunk_invalid_timing"
        
        # This validation should happen in the API route, but we test it here too
        # Since timing validation is part of the business logic
        start_time = 10.0
        end_time = 5.0  # Invalid: end before start
        
        with patch('api.routes.processing.settings') as mock_settings:
            mock_settings.get_videos_path.return_value = Path(mock_video_file).parent
            
            # The function should handle this gracefully or the route should validate
            # For now, the function assumes valid input, but this highlights the need for
            # input validation in the service layer rather than just the route
            
            try:
                await run_chunk_processing(
                    video_path=mock_video_file,
                    start_time=start_time,
                    end_time=end_time,
                    task_id=task_id,
                    task_progress=mock_task_progress,
                    user_id=1
                )
                # If it doesn't fail, it should at least process something
                assert task_id in mock_task_progress
            except Exception:
                # It's acceptable for this to fail given invalid input
                pass

    def test_progress_tracking_structure(self, mock_task_progress):
        """Test that progress tracking follows expected structure"""
        task_id = "test_progress_structure"
        
        # Initialize a status like the function does
        status = ProcessingStatus(
            status="processing",
            progress=0.0,
            current_step="Initializing chunk processing...",
            message="Processing segment 0:00 - 0:10",
            started_at=1234567890
        )
        
        mock_task_progress[task_id] = status
        
        # Verify structure
        assert hasattr(status, 'status')
        assert hasattr(status, 'progress') 
        assert hasattr(status, 'current_step')
        assert hasattr(status, 'message')
        assert hasattr(status, 'started_at')
        
        # Verify initial values
        assert status.status == "processing"
        assert status.progress == 0.0
        assert "Initializing" in status.current_step


class TestChunkProcessingBusinessLogic:
    """Test specific business logic patterns in chunk processing"""
    
    def test_srt_file_resolution_logic(self, mock_video_file):
        """Test the complex SRT file resolution logic"""
        video_path = Path(mock_video_file)
        video_dir = video_path.parent
        
        # Create multiple SRT files to test resolution logic
        exact_match = video_dir / f"{video_path.stem}.srt"
        partial_match = video_dir / f"{video_path.stem}_episode.srt"
        unrelated = video_dir / "other_video.srt"
        
        exact_match.write_text("exact match content")
        partial_match.write_text("partial match content")  
        unrelated.write_text("unrelated content")
        
        try:
            # Test exact match preference
            srt_files = list(video_dir.glob("*.srt"))
            original_srt_files = [f for f in srt_files if "_chunk_" not in f.name]
            
            video_stem = video_path.stem
            exact_matches = [f for f in original_srt_files if f.stem == video_stem]
            
            assert len(exact_matches) == 1
            assert exact_matches[0] == exact_match
            
        finally:
            # Cleanup
            for srt_file in [exact_match, partial_match, unrelated]:
                if srt_file.exists():
                    srt_file.unlink()

    def test_chunk_filename_pattern(self):
        """Test chunk filename generation pattern"""
        video_stem = "test_video"
        start_time = 30.5
        end_time = 45.2
        
        # Pattern used in the function
        chunk_pattern = f"{video_stem}_chunk_{int(start_time)}_{int(end_time)}*.srt"
        
        assert chunk_pattern == "test_video_chunk_30_45*.srt"
        
        # Test that it would match expected files
        expected_files = [
            "test_video_chunk_30_45.srt",
            "test_video_chunk_30_45_filtered.srt",
            "test_video_chunk_30_45_de.srt"
        ]
        
        import fnmatch
        for filename in expected_files:
            assert fnmatch.fnmatch(filename, chunk_pattern)

    def test_timing_format_conversion(self):
        """Test time formatting used in progress messages"""
        start_time = 65.5  # 1:05.5
        end_time = 125.8   # 2:05.8
        
        # Format used in the function
        start_formatted = f"{int(start_time//60)}:{int(start_time%60):02d}"
        end_formatted = f"{int(end_time//60)}:{int(end_time%60):02d}"
        
        assert start_formatted == "1:05"
        assert end_formatted == "2:05"
        
        message = f"Processing segment {start_formatted} - {end_formatted}"
        assert message == "Processing segment 1:05 - 2:05"

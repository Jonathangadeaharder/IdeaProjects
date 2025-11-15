"""Unit tests for VocabularyService - Clean lemma-based implementation"""

from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from services.vocabulary.vocabulary_service import VocabularyService


class TestVocabularyServiceGetWordInfo:
    """Tests for VocabularyService.get_word_info"""

    @pytest.mark.asyncio
    async def test_When_word_found_in_database_Then_returns_word_info(self):
        """Happy path: word exists in database - facade delegation test"""
        # Arrange
        service = VocabularyService()
        mock_db = AsyncMock(spec=AsyncSession)

        expected_result = {
            "id": uuid4(),
            "word": "Haus",
            "lemma": "haus",
            "language": "de",
            "difficulty_level": "A1",
            "part_of_speech": "noun",
            "gender": "neuter",
            "translation_en": "house",
            "pronunciation": "haus",
            "notes": None,
            "found": True,
        }

        # Act - Mock facade delegation to query_service
        with patch.object(service.query_service, "get_word_info", new_callable=AsyncMock, return_value=expected_result):
            result = await service.get_word_info("Haus", "de", mock_db)

        # Assert
        assert result["found"] is True
        assert result["word"] == "Haus"
        assert result["lemma"] == "haus"
        assert result["language"] == "de"
        assert result["difficulty_level"] == "A1"
        assert result["translation_en"] == "house"
        assert "id" in result

    @pytest.mark.asyncio
    async def test_When_word_not_found_Then_returns_not_found_info(self):
        """Boundary: word doesn't exist in database - facade delegation test"""
        # Arrange
        service = VocabularyService()
        mock_db = AsyncMock(spec=AsyncSession)

        expected_result = {
            "word": "xyz",
            "lemma": "xyz",
            "language": "de",
            "found": False,
            "message": "Word not in vocabulary database",
        }

        # Act - Mock facade delegation to query_service
        with patch.object(service.query_service, "get_word_info", new_callable=AsyncMock, return_value=expected_result):
            result = await service.get_word_info("xyz", "de", mock_db)

        # Assert
        assert result["found"] is False
        assert result["word"] == "xyz"
        assert result["lemma"] == "xyz"
        assert result["language"] == "de"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_When_word_not_found_Then_tracks_unknown_word(self):
        """Behavior: unknown words are tracked - facade delegation test"""
        # Arrange
        service = VocabularyService()
        mock_db = AsyncMock(spec=AsyncSession)

        expected_result = {
            "word": "unknown",
            "lemma": "unknown",
            "language": "de",
            "found": False,
            "message": "Word not in vocabulary database",
        }

        # Act - Mock facade delegation to query_service (which handles tracking internally)
        with patch.object(
            service.query_service, "get_word_info", new_callable=AsyncMock, return_value=expected_result
        ) as mock_get_word:
            await service.get_word_info("unknown", "de", mock_db)

        # Assert - verify delegation occurred (tracking is handled by query_service)
        mock_get_word.assert_called_once_with("unknown", "de", mock_db)


class TestVocabularyServiceMarkWordKnown:
    """Tests for VocabularyService.mark_word_known"""

    @pytest.mark.asyncio
    async def test_When_marking_known_word_for_first_time_Then_creates_progress(self):
        """Happy path: first time marking word as known - facade delegation test"""
        # Arrange
        service = VocabularyService()
        mock_db = AsyncMock(spec=AsyncSession)
        user_id = 1
        uuid4()

        expected_result = {
            "success": True,
            "word": "Hund",
            "lemma": "hund",
            "is_known": True,
            "confidence_level": 1,
            "level": "A1",
        }

        # Act - Mock facade delegation to progress_service
        with patch.object(
            service.progress_service, "mark_word_known", new_callable=AsyncMock, return_value=expected_result
        ):
            result = await service.mark_word_known(user_id, "Hund", "de", True, mock_db)

        # Assert
        assert result["success"] is True
        assert result["word"] == "Hund"
        assert result["is_known"] is True
        assert result["confidence_level"] == 1

    @pytest.mark.asyncio
    async def test_When_marking_word_not_in_database_Then_returns_failure(self):
        """Error: cannot mark word that doesn't exist - facade delegation test"""
        # Arrange
        service = VocabularyService()
        mock_db = AsyncMock(spec=AsyncSession)
        user_id = 1

        expected_result = {
            "success": False,
            "word": "xyz",
            "lemma": "xyz",
            "message": "Word not in vocabulary database",
        }

        # Act - Mock facade delegation to progress_service
        with patch.object(
            service.progress_service, "mark_word_known", new_callable=AsyncMock, return_value=expected_result
        ):
            result = await service.mark_word_known(user_id, "xyz", "de", True, mock_db)

        # Assert
        assert result["success"] is False
        assert "message" in result

    @pytest.mark.asyncio
    async def test_When_updating_existing_progress_as_known_Then_increases_confidence(self):
        """Happy path: updating existing progress increases confidence - facade delegation test"""
        # Arrange
        service = VocabularyService()
        mock_db = AsyncMock(spec=AsyncSession)
        user_id = 1
        uuid4()

        expected_result = {
            "success": True,
            "word": "Katze",
            "lemma": "katze",
            "is_known": True,
            "confidence_level": 3,  # Increased from 2 to 3
            "review_count": 2,  # Increased from 1 to 2
            "level": "A1",
        }

        # Act - Mock facade delegation to progress_service
        with patch.object(
            service.progress_service, "mark_word_known", new_callable=AsyncMock, return_value=expected_result
        ):
            result = await service.mark_word_known(user_id, "Katze", "de", True, mock_db)

        # Assert
        assert result["success"] is True
        assert result["confidence_level"] == 3  # Increased from 2 to 3
        assert result["review_count"] == 2  # Increased from 1 to 2


class TestVocabularyServiceGetUserStats:
    """Tests for VocabularyService.get_user_vocabulary_stats"""

    @pytest.mark.asyncio
    async def test_When_getting_stats_Then_returns_total_and_known_counts(self):
        """Happy path: retrieve user vocabulary statistics"""
        # Arrange
        service = VocabularyService()
        mock_db = AsyncMock(spec=AsyncSession)
        user_id = 1
        language = "de"

        # Mock total words count
        mock_total_result = Mock()
        mock_total_result.scalar.return_value = 1000

        # Mock known words count
        mock_known_result = Mock()
        mock_known_result.scalar.return_value = 150

        # Mock level breakdown - needs to be iterable with tuple unpacking
        # The code does: level, total, known = row
        mock_level_result = Mock()
        mock_level_result.__iter__ = Mock(return_value=iter([("A1", 300, 100), ("A2", 400, 50), ("B1", 300, 0)]))

        # Configure execute to return different results
        mock_db.execute.side_effect = [mock_total_result, mock_known_result, mock_level_result]

        # Act
        result = await service.get_user_vocabulary_stats(user_id, language, mock_db)

        # Assert
        assert "total_words" in result
        assert "total_known" in result
        assert result["total_words"] == 1000
        assert result["total_known"] == 150

    @pytest.mark.asyncio
    async def test_When_user_has_no_progress_Then_returns_zero_known(self):
        """Boundary: user with no progress returns 0 known words"""
        # Arrange
        service = VocabularyService()
        mock_db = AsyncMock(spec=AsyncSession)
        user_id = 999
        language = "de"

        # Mock total words count
        mock_total_result = Mock()
        mock_total_result.scalar.return_value = 1000

        # Mock zero known words
        mock_known_result = Mock()
        mock_known_result.scalar.return_value = 0

        # Mock empty level breakdown - needs to be iterable
        mock_level_result = Mock()
        mock_level_result.__iter__ = Mock(return_value=iter([]))

        mock_db.execute.side_effect = [mock_total_result, mock_known_result, mock_level_result]

        # Act
        result = await service.get_user_vocabulary_stats(user_id, language, mock_db)

        # Assert
        assert result["total_known"] == 0


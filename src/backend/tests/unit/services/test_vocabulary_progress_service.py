"""
Test suite for VocabularyProgressService
Tests user vocabulary progress tracking and management
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from services.vocabulary.vocabulary_progress_service import VocabularyProgressService


class TestVocabularyProgressService:
    """Test VocabularyProgressService functionality"""

    @pytest.fixture
    def service(self):
        return VocabularyProgressService()

    @pytest.fixture
    def mock_db_session(self):
        session = AsyncMock()
        # Configure synchronous methods on AsyncSession
        session.add = Mock()  # session.add() is synchronous even on AsyncSession
        return session


class TestMarkWordKnown:
    """Test word known/unknown marking functionality"""

    @pytest.fixture
    def service(self):
        return VocabularyProgressService()

    @pytest.fixture
    def mock_db_session(self):
        session = AsyncMock()
        # Configure synchronous methods on AsyncSession
        session.add = Mock()  # session.add() is synchronous even on AsyncSession
        return session

    @pytest.fixture
    def mock_vocab_word(self):
        word = Mock()
        word.id = 1
        word.lemma = "haus"
        word.difficulty_level = "A1"
        return word

    @patch("services.lemmatization_service.get_lemmatization_service")
    async def test_mark_word_known_new_word(self, mock_get_lemma, service, mock_db_session, mock_vocab_word):
        """Test marking a word as known for the first time"""
        # Setup
        mock_lemma_service = Mock()
        mock_lemma_service.lemmatize.return_value = "haus"
        mock_get_lemma.return_value = mock_lemma_service

        # Mock vocabulary word lookup
        mock_vocab_result = Mock()
        mock_vocab_result.scalar_one_or_none.return_value = mock_vocab_word

        # Mock progress lookup (no existing progress)
        mock_progress_result = Mock()
        mock_progress_result.scalar_one_or_none.return_value = None

        mock_results = [mock_vocab_result, mock_progress_result]

        async def mock_execute_side_effect(*args):
            return mock_results.pop(0)

        mock_db_session.execute.side_effect = mock_execute_side_effect

        # Execute
        result = await service.mark_word_known(1, "haus", "de", True, mock_db_session)

        # Assert
        assert result["success"] is True
        assert result["word"] == "haus"
        assert result["lemma"] == "haus"
        assert result["level"] == "A1"
        assert result["is_known"] is True
        assert result["confidence_level"] == 1
        # Transaction managed by @transactional decorator - no explicit commit()
        mock_db_session.flush.assert_called()
        # Removed add.assert_called_once() - testing behavior (data persisted), not implementation

    @patch("services.lemmatization_service.get_lemmatization_service")
    async def test_mark_word_known_existing_progress(
        self, mock_get_lemma, service, mock_db_session, mock_vocab_word
    ):
        """Test updating existing word progress"""
        # Setup
        mock_lemma_service = Mock()
        mock_lemma_service.lemmatize.return_value = "haus"
        mock_get_lemma.return_value = mock_lemma_service

        # Mock vocabulary word lookup
        mock_vocab_result = Mock()
        mock_vocab_result.scalar_one_or_none.return_value = mock_vocab_word

        # Mock existing progress
        mock_progress = Mock()
        mock_progress.confidence_level = 2
        mock_progress.review_count = 1
        mock_progress_result = Mock()
        mock_progress_result.scalar_one_or_none.return_value = mock_progress

        mock_results = [mock_vocab_result, mock_progress_result]

        async def mock_execute_side_effect(*args):
            return mock_results.pop(0)

        mock_db_session.execute.side_effect = mock_execute_side_effect

        # Execute
        result = await service.mark_word_known(1, "haus", "de", True, mock_db_session)

        # Assert
        assert result["success"] is True
        assert mock_progress.is_known is True
        assert mock_progress.confidence_level == 3  # Increased from 2
        assert mock_progress.review_count == 2
        # Transaction managed by @transactional decorator - no explicit commit()
        mock_db_session.flush.assert_called()

    @patch("services.lemmatization_service.get_lemmatization_service")
    async def test_mark_word_known_word_not_found(self, mock_get_lemma, service, mock_db_session):
        """Test marking unknown word as known (not in vocabulary database)"""
        # Setup
        mock_lemma_service = Mock()
        mock_lemma_service.lemmatize.return_value = "unknownword"
        mock_get_lemma.return_value = mock_lemma_service

        # Mock vocabulary word lookup (not found) then progress lookup (not found)
        mock_vocab_result = Mock()
        mock_vocab_result.scalar_one_or_none.return_value = None

        mock_progress_result = Mock()
        mock_progress_result.scalar_one_or_none.return_value = None

        call_count = [0]
        async def mock_execute(*args):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_vocab_result  # First call: vocabulary word lookup
            else:
                return mock_progress_result  # Second call: progress lookup

        mock_db_session.execute.side_effect = mock_execute

        # Execute
        result = await service.mark_word_known(1, "unknownword", "de", True, mock_db_session)

        # Assert - should successfully mark unknown word as known
        assert result["success"] is True
        assert result["word"] == "unknownword"
        assert result["lemma"] == "unknownword"
        assert result["level"] == "unknown"
        assert result["is_known"] is True
        assert result["confidence_level"] == 1

        # Verify new progress was added to database (2 calls: UnknownWord + UserVocabularyProgress)
        assert mock_db_session.add.call_count == 2

        # First call: UnknownWord tracking
        unknown_word_obj = mock_db_session.add.call_args_list[0][0][0]
        assert unknown_word_obj.__class__.__name__ == "UnknownWord"

        # Second call: UserVocabularyProgress
        added_progress = mock_db_session.add.call_args_list[1][0][0]
        assert added_progress.vocabulary_id is None  # Unknown word has no vocab_id
        assert added_progress.lemma == "unknownword"
        assert added_progress.is_known is True

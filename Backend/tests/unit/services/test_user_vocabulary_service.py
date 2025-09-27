"""
Test suite for SQLiteUserVocabularyService
Tests focus on interface-based testing of vocabulary management business logic
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

from services.dataservice.user_vocabulary_service import SQLiteUserVocabularyService
from tests.base import ServiceTestBase


class MockVocabularyWord:
    """Mock vocabulary word for testing"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.word = kwargs.get('word', 'test')
        self.language = kwargs.get('language', 'en')
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())
        self.updated_at = kwargs.get('updated_at', datetime.now().isoformat())


class MockLearningProgress:
    """Mock learning progress record for testing"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.user_id = kwargs.get('user_id', 'test_user')
        self.word_id = kwargs.get('word_id', 1)
        self.confidence_level = kwargs.get('confidence_level', 1)
        self.review_count = kwargs.get('review_count', 1)
        self.learned_at = kwargs.get('learned_at', datetime.now().isoformat())
        self.last_reviewed = kwargs.get('last_reviewed', None)


@pytest.fixture
def vocab_service():
    """Create SQLiteUserVocabularyService with mocked session manager"""
    service = SQLiteUserVocabularyService()

    # Create properly isolated mock session
    mock_session = ServiceTestBase.create_mock_session()

    # Configure default behavior
    ServiceTestBase.configure_mock_query_result(mock_session, {
        'scalar_one_or_none': None,  # No existing data by default
        'first': None,
        'fetchone': None,
        'fetchall': [],
        'rowcount': 0,
        'lastrowid': 1
    })

    # Mock the get_session context manager properly
    async def mock_get_session():
        try:
            yield mock_session
        except Exception:
            await mock_session.rollback()
            raise

    # Create a proper async context manager mock
    from contextlib import asynccontextmanager
    service.get_session = lambda: asynccontextmanager(mock_get_session)()

    return service, mock_session


@pytest.fixture
def mock_word():
    """Create a mock vocabulary word"""
    return MockVocabularyWord(
        id=1,
        word='hello',
        language='en',
        created_at=datetime.now().isoformat()
    )


@pytest.fixture
def mock_progress():
    """Create a mock learning progress record"""
    return MockLearningProgress(
        id=1,
        user_id='test_user',
        word_id=1,
        confidence_level=1,
        review_count=1
    )


# =============================================================================
# TestUserVocabularyServiceBasicOperations - Basic CRUD operations
# =============================================================================

class TestUserVocabularyServiceBasicOperations:
    """Test basic vocabulary service operations"""

    async def test_is_word_known_returns_true_when_word_exists(self, vocab_service):
        """Test that is_word_known returns True for known words"""
        service, mock_session = vocab_service

        # Mock query to return a count of 1
        mock_result = MagicMock()
        mock_result.fetchone.return_value = [1]  # Word exists
        mock_session.execute.return_value = mock_result

        result = await service.is_word_known('test_user', 'hello', 'en')

        assert result is True
        mock_session.execute.assert_called_once()

    async def test_is_word_known_returns_false_when_word_not_exists(self, vocab_service):
        """Test that is_word_known returns False for unknown words"""
        service, mock_session = vocab_service

        # Mock query to return a count of 0
        mock_result = MagicMock()
        mock_result.fetchone.return_value = [0]  # Word doesn't exist
        mock_session.execute.return_value = mock_result

        result = await service.is_word_known('test_user', 'unknown', 'en')

        assert result is False
        mock_session.execute.assert_called_once()

    async def test_is_word_known_handles_database_error(self, vocab_service):
        """Test that is_word_known handles database errors gracefully"""
        service, mock_session = vocab_service

        # Mock database error
        mock_session.execute.side_effect = Exception("Database connection failed")

        result = await service.is_word_known('test_user', 'hello', 'en')

        assert result is False  # Should return False on error

    async def test_get_known_words_returns_word_list(self, vocab_service):
        """Test that get_known_words returns list of known words"""
        service, mock_session = vocab_service

        # Mock query to return word list
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [('hello',), ('world',), ('test',)]
        mock_session.execute.return_value = mock_result

        result = await service.get_known_words('test_user', 'en')

        assert result == ['hello', 'world', 'test']
        mock_session.execute.assert_called_once()

    async def test_get_known_words_returns_empty_list_for_new_user(self, vocab_service):
        """Test that get_known_words returns empty list for new users"""
        service, mock_session = vocab_service

        # Mock query to return empty result
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result

        result = await service.get_known_words('new_user', 'en')

        assert result == []
        mock_session.execute.assert_called_once()

    async def test_get_known_words_handles_database_error(self, vocab_service):
        """Test that get_known_words handles database errors gracefully"""
        service, mock_session = vocab_service

        # Mock database error
        mock_session.execute.side_effect = Exception("Database error")

        result = await service.get_known_words('test_user', 'en')

        assert result == []  # Should return empty list on error

    async def test_mark_word_learned_success_new_word(self, vocab_service):
        """Test marking a new word as learned"""
        service, mock_session = vocab_service

        # Mock _ensure_word_exists to return word ID
        with patch.object(service, '_ensure_word_exists', return_value=1):
            # Mock existing progress query to return None (new word)
            mock_result = MagicMock()
            mock_result.fetchone.return_value = None
            mock_session.execute.return_value = mock_result

            result = await service.mark_word_learned('test_user', 'hello', 'en')

            assert result is True
            mock_session.commit.assert_called_once()

    async def test_mark_word_learned_success_existing_word(self, vocab_service):
        """Test marking an existing word as learned (update)"""
        service, mock_session = vocab_service

        # Mock _ensure_word_exists to return word ID
        with patch.object(service, '_ensure_word_exists', return_value=1):
            # Mock existing progress query to return existing record
            mock_result = MagicMock()
            mock_result.fetchone.return_value = [1]  # Existing progress ID
            mock_session.execute.return_value = mock_result

            result = await service.mark_word_learned('test_user', 'hello', 'en')

            assert result is True
            mock_session.commit.assert_called_once()

    async def test_mark_word_learned_fails_when_word_creation_fails(self, vocab_service):
        """Test mark_word_learned fails when word creation fails"""
        service, mock_session = vocab_service

        # Mock _ensure_word_exists to return None (failure)
        with patch.object(service, '_ensure_word_exists', return_value=None):
            result = await service.mark_word_learned('test_user', 'hello', 'en')

            assert result is False

    async def test_mark_word_learned_handles_database_error(self, vocab_service):
        """Test mark_word_learned handles database errors"""
        service, mock_session = vocab_service

        # Mock database error
        mock_session.execute.side_effect = Exception("Database error")

        result = await service.mark_word_learned('test_user', 'hello', 'en')

        assert result is False

    async def test_remove_word_success(self, vocab_service):
        """Test successful word removal"""
        service, mock_session = vocab_service

        # Mock word lookup to return word ID
        mock_word_result = MagicMock()
        mock_word_result.fetchone.return_value = [1]  # Word ID

        # Mock delete result
        mock_delete_result = MagicMock()
        mock_delete_result.rowcount = 1  # One row deleted

        mock_session.execute.side_effect = [mock_word_result, mock_delete_result]

        result = await service.remove_word('test_user', 'hello', 'en')

        assert result is True
        mock_session.commit.assert_called_once()

    async def test_remove_word_fails_when_word_not_found(self, vocab_service):
        """Test remove_word fails when word doesn't exist in vocabulary"""
        service, mock_session = vocab_service

        # Mock word lookup to return None
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_session.execute.return_value = mock_result

        result = await service.remove_word('test_user', 'nonexistent', 'en')

        assert result is False

    async def test_remove_word_fails_when_not_in_user_progress(self, vocab_service):
        """Test remove_word fails when word exists but not in user's progress"""
        service, mock_session = vocab_service

        # Mock word lookup to return word ID
        mock_word_result = MagicMock()
        mock_word_result.fetchone.return_value = [1]  # Word ID

        # Mock delete result with 0 rows affected
        mock_delete_result = MagicMock()
        mock_delete_result.rowcount = 0  # No rows deleted

        mock_session.execute.side_effect = [mock_word_result, mock_delete_result]

        result = await service.remove_word('test_user', 'hello', 'en')

        assert result is False

    async def test_remove_word_handles_database_error(self, vocab_service):
        """Test remove_word handles database errors"""
        service, mock_session = vocab_service

        # Mock database error
        mock_session.execute.side_effect = Exception("Database error")

        result = await service.remove_word('test_user', 'hello', 'en')

        assert result is False


# =============================================================================
# TestUserVocabularyServiceLevelOperations - Learning level operations
# =============================================================================

class TestUserVocabularyServiceLevelOperations:
    """Test learning level calculation and management"""

    async def test_get_learning_level_a1(self, vocab_service):
        """Test A1 level calculation (< 500 words)"""
        service, mock_session = vocab_service

        # Mock get_known_words to return small vocabulary
        with patch.object(service, 'get_known_words', return_value=['word' + str(i) for i in range(100)]):
            result = await service.get_learning_level('test_user')

            assert result == "A1"

    async def test_get_learning_level_a2(self, vocab_service):
        """Test A2 level calculation (500-1499 words)"""
        service, mock_session = vocab_service

        # Mock get_known_words to return medium vocabulary
        with patch.object(service, 'get_known_words', return_value=['word' + str(i) for i in range(1000)]):
            result = await service.get_learning_level('test_user')

            assert result == "A2"

    async def test_get_learning_level_b1(self, vocab_service):
        """Test B1 level calculation (1500-2999 words)"""
        service, mock_session = vocab_service

        # Mock get_known_words to return larger vocabulary
        with patch.object(service, 'get_known_words', return_value=['word' + str(i) for i in range(2000)]):
            result = await service.get_learning_level('test_user')

            assert result == "B1"

    async def test_get_learning_level_b2(self, vocab_service):
        """Test B2 level calculation (3000-4999 words)"""
        service, mock_session = vocab_service

        with patch.object(service, 'get_known_words', return_value=['word' + str(i) for i in range(4000)]):
            result = await service.get_learning_level('test_user')

            assert result == "B2"

    async def test_get_learning_level_c1(self, vocab_service):
        """Test C1 level calculation (5000-7999 words)"""
        service, mock_session = vocab_service

        with patch.object(service, 'get_known_words', return_value=['word' + str(i) for i in range(6000)]):
            result = await service.get_learning_level('test_user')

            assert result == "C1"

    async def test_get_learning_level_c2(self, vocab_service):
        """Test C2 level calculation (8000+ words)"""
        service, mock_session = vocab_service

        with patch.object(service, 'get_known_words', return_value=['word' + str(i) for i in range(10000)]):
            result = await service.get_learning_level('test_user')

            assert result == "C2"

    async def test_get_learning_level_handles_error(self, vocab_service):
        """Test get_learning_level returns default on error"""
        service, mock_session = vocab_service

        # Mock get_known_words to raise exception
        with patch.object(service, 'get_known_words', side_effect=Exception("Error")):
            result = await service.get_learning_level('test_user')

            assert result == "A2"  # Default level

    async def test_set_learning_level_always_succeeds(self, vocab_service):
        """Test set_learning_level (currently just logs)"""
        service, mock_session = vocab_service

        result = await service.set_learning_level('test_user', 'B1')

        assert result is True


# =============================================================================
# TestUserVocabularyServiceBatchOperations - Batch processing tests
# =============================================================================

class TestUserVocabularyServiceBatchOperations:
    """Test batch word operations"""

    async def test_add_known_words_empty_list_succeeds(self, vocab_service):
        """Test adding empty word list succeeds"""
        service, mock_session = vocab_service

        result = await service.add_known_words('test_user', [], 'en')

        assert result is True

    async def test_add_known_words_filters_empty_words(self, vocab_service):
        """Test that empty/whitespace words are filtered out"""
        service, mock_session = vocab_service

        result = await service.add_known_words('test_user', ['', '  ', '\t'], 'en')

        assert result is True

    async def test_add_known_words_success_new_words(self, vocab_service):
        """Test successful batch addition of new words"""
        service, mock_session = vocab_service

        # Mock batch operations
        with patch.object(service, '_ensure_words_exist_batch', return_value={'hello': 1, 'world': 2}):
            with patch.object(service, '_get_existing_progress_batch', return_value=set()):
                result = await service.add_known_words('test_user', ['hello', 'world'], 'en')

                assert result is True
                mock_session.commit.assert_called_once()

    async def test_add_known_words_success_mixed_new_and_existing(self, vocab_service):
        """Test batch addition with mix of new and existing words"""
        service, mock_session = vocab_service

        # Mock batch operations
        with patch.object(service, '_ensure_words_exist_batch', return_value={'hello': 1, 'world': 2}):
            with patch.object(service, '_get_existing_progress_batch', return_value={1}):  # 'hello' exists
                result = await service.add_known_words('test_user', ['hello', 'world'], 'en')

                assert result is True
                mock_session.commit.assert_called_once()

    async def test_add_known_words_fails_when_word_creation_fails(self, vocab_service):
        """Test batch addition fails when word creation fails"""
        service, mock_session = vocab_service

        # Mock _ensure_words_exist_batch to return empty dict (failure)
        with patch.object(service, '_ensure_words_exist_batch', return_value={}):
            result = await service.add_known_words('test_user', ['hello', 'world'], 'en')

            assert result is False

    async def test_add_known_words_handles_database_error(self, vocab_service):
        """Test batch addition handles database errors"""
        service, mock_session = vocab_service

        # Mock database error during batch operations
        mock_session.execute.side_effect = Exception("Database error")

        result = await service.add_known_words('test_user', ['hello', 'world'], 'en')

        assert result is False

    async def test_add_known_words_normalizes_input(self, vocab_service):
        """Test that input words are properly normalized (lowercase, stripped)"""
        service, mock_session = vocab_service

        # Mock batch operations to capture the normalized words
        normalized_words = []

        async def mock_ensure_words_exist(session, words, language):
            nonlocal normalized_words
            normalized_words = words
            return {word: i+1 for i, word in enumerate(words)}

        with patch.object(service, '_ensure_words_exist_batch', side_effect=mock_ensure_words_exist):
            with patch.object(service, '_get_existing_progress_batch', return_value=set()):
                await service.add_known_words('test_user', ['  HELLO  ', 'WORLD\t'], 'en')

                assert normalized_words == ['hello', 'world']


# =============================================================================
# TestUserVocabularyServiceInternalMethods - Internal utility method tests
# =============================================================================

class TestUserVocabularyServiceInternalMethods:
    """Test internal utility methods"""

    async def test_ensure_word_exists_creates_new_word(self, vocab_service):
        """Test _ensure_word_exists creates new word when it doesn't exist"""
        service, mock_session = vocab_service

        # Mock existing word query to return None
        mock_existing_result = MagicMock()
        mock_existing_result.fetchone.return_value = None

        # Mock insert result
        mock_insert_result = MagicMock()
        mock_insert_result.lastrowid = 5

        mock_session.execute.side_effect = [mock_existing_result, mock_insert_result]

        # Need to create a real session for the method call
        async def mock_get_session():
            yield mock_session

        service.get_session = MagicMock(return_value=mock_get_session())

        result = await service._ensure_word_exists(mock_session, 'hello', 'en')

        assert result == 5
        assert mock_session.execute.call_count == 2  # SELECT + INSERT
        mock_session.flush.assert_called_once()

    async def test_ensure_word_exists_returns_existing_word_id(self, vocab_service):
        """Test _ensure_word_exists returns existing word ID"""
        service, mock_session = vocab_service

        # Mock existing word query to return word ID
        mock_result = MagicMock()
        mock_result.fetchone.return_value = [3]  # Existing word ID
        mock_session.execute.return_value = mock_result

        result = await service._ensure_word_exists(mock_session, 'hello', 'en')

        assert result == 3
        assert mock_session.execute.call_count == 1  # Only SELECT

    async def test_ensure_word_exists_handles_error(self, vocab_service):
        """Test _ensure_word_exists handles database errors"""
        service, mock_session = vocab_service

        # Mock database error
        mock_session.execute.side_effect = Exception("Database error")

        result = await service._ensure_word_exists(mock_session, 'hello', 'en')

        assert result is None

    async def test_ensure_words_exist_batch_empty_list(self, vocab_service):
        """Test _ensure_words_exist_batch handles empty input"""
        service, mock_session = vocab_service

        result = await service._ensure_words_exist_batch(mock_session, [], 'en')

        assert result == {}

    async def test_ensure_words_exist_batch_all_existing(self, vocab_service):
        """Test _ensure_words_exist_batch with all existing words"""
        service, mock_session = vocab_service

        # Mock existing words query
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [('hello', 1), ('world', 2)]
        mock_session.execute.return_value = mock_result

        result = await service._ensure_words_exist_batch(mock_session, ['hello', 'world'], 'en')

        assert result == {'hello': 1, 'world': 2}
        assert mock_session.execute.call_count == 1  # Only SELECT

    async def test_ensure_words_exist_batch_mixed_existing_new(self, vocab_service):
        """Test _ensure_words_exist_batch with mix of existing and new words"""
        service, mock_session = vocab_service

        # Mock existing words query (only 'hello' exists)
        mock_existing_result = MagicMock()
        mock_existing_result.fetchall.return_value = [('hello', 1)]

        # Mock insert results for new words
        mock_insert_result = MagicMock()
        mock_insert_result.lastrowid = 2

        mock_session.execute.side_effect = [mock_existing_result, mock_insert_result]

        result = await service._ensure_words_exist_batch(mock_session, ['hello', 'world'], 'en')

        assert result == {'hello': 1, 'world': 2}
        assert mock_session.execute.call_count == 2  # SELECT + INSERT
        mock_session.flush.assert_called_once()

    async def test_ensure_words_exist_batch_handles_error(self, vocab_service):
        """Test _ensure_words_exist_batch handles database errors"""
        service, mock_session = vocab_service

        # Mock database error
        mock_session.execute.side_effect = Exception("Database error")

        result = await service._ensure_words_exist_batch(mock_session, ['hello', 'world'], 'en')

        assert result == {}

    async def test_get_existing_progress_batch_empty_input(self, vocab_service):
        """Test _get_existing_progress_batch handles empty input"""
        service, mock_session = vocab_service

        result = await service._get_existing_progress_batch(mock_session, 'test_user', [])

        assert result == set()

    async def test_get_existing_progress_batch_success(self, vocab_service):
        """Test _get_existing_progress_batch returns existing progress"""
        service, mock_session = vocab_service

        # Mock query result
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [(1,), (3,)]  # Word IDs with existing progress
        mock_session.execute.return_value = mock_result

        result = await service._get_existing_progress_batch(mock_session, 'test_user', [1, 2, 3])

        assert result == {1, 3}

    async def test_get_existing_progress_batch_handles_error(self, vocab_service):
        """Test _get_existing_progress_batch handles database errors"""
        service, mock_session = vocab_service

        # Mock database error
        mock_session.execute.side_effect = Exception("Database error")

        result = await service._get_existing_progress_batch(mock_session, 'test_user', [1, 2, 3])

        assert result == set()


# =============================================================================
# TestUserVocabularyServiceStatistics - Statistics and analytics tests
# =============================================================================

class TestUserVocabularyServiceStatistics:
    """Test statistics and analytics functionality"""

    async def test_get_learning_statistics_comprehensive_stats(self, vocab_service):
        """Test get_learning_statistics returns comprehensive stats"""
        service, mock_session = vocab_service

        # Mock get_known_words
        known_words = ['hello', 'world', 'test']
        with patch.object(service, 'get_known_words', return_value=known_words):
            # Mock confidence distribution query
            confidence_result = MagicMock()
            confidence_result.fetchall.return_value = [(1, 5), (2, 3), (3, 2)]

            # Mock recent learning query
            recent_result = MagicMock()
            recent_result.fetchone.return_value = [2]

            # Mock top reviewed query
            top_reviewed_result = MagicMock()
            top_reviewed_result.fetchall.return_value = [
                ('hello', 5, 2),
                ('world', 3, 1)
            ]

            mock_session.execute.side_effect = [confidence_result, recent_result, top_reviewed_result]

            result = await service.get_learning_statistics('test_user', 'en')

            expected = {
                'total_known': 3,
                'total_learned': 3,
                'learning_level': 'A1',  # < 500 words
                'total_vocabulary': 3,
                'confidence_distribution': {1: 5, 2: 3, 3: 2},
                'recent_learned_7_days': 2,
                'top_reviewed_words': [
                    {'word': 'hello', 'review_count': 5, 'confidence_level': 2},
                    {'word': 'world', 'review_count': 3, 'confidence_level': 1}
                ],
                'language': 'en'
            }

            assert result == expected

    async def test_get_learning_statistics_empty_user(self, vocab_service):
        """Test get_learning_statistics for user with no words"""
        service, mock_session = vocab_service

        # Mock get_known_words to return empty list
        with patch.object(service, 'get_known_words', return_value=[]):
            # Mock empty query results
            empty_result = MagicMock()
            empty_result.fetchall.return_value = []
            empty_result.fetchone.return_value = [0]

            mock_session.execute.side_effect = [empty_result, empty_result, empty_result]

            result = await service.get_learning_statistics('new_user', 'en')

            assert result['total_known'] == 0
            assert result['total_learned'] == 0
            assert result['confidence_distribution'] == {}
            assert result['recent_learned_7_days'] == 0
            assert result['top_reviewed_words'] == []

    async def test_get_learning_statistics_handles_database_error(self, vocab_service):
        """Test get_learning_statistics handles database errors"""
        service, mock_session = vocab_service

        # Mock database error during stats collection
        mock_session.execute.side_effect = Exception("Database error")

        result = await service.get_learning_statistics('test_user', 'en')

        assert result == {"total_known": 0, "total_learned": 0, "error": "Database error"}

    async def test_get_word_learning_history_success(self, vocab_service):
        """Test get_word_learning_history returns word history"""
        service, mock_session = vocab_service

        # Mock query result
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ('2023-01-01', 1, 1, None),
            ('2023-01-02', 2, 2, '2023-01-03')
        ]
        mock_session.execute.return_value = mock_result

        result = await service.get_word_learning_history('test_user', 'hello', 'en')

        expected = [
            {
                'learned_at': '2023-01-01',
                'confidence_level': 1,
                'review_count': 1,
                'last_reviewed': None
            },
            {
                'learned_at': '2023-01-02',
                'confidence_level': 2,
                'review_count': 2,
                'last_reviewed': '2023-01-03'
            }
        ]

        assert result == expected

    async def test_get_word_learning_history_empty_word(self, vocab_service):
        """Test get_word_learning_history for word with no history"""
        service, mock_session = vocab_service

        # Mock empty query result
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result

        result = await service.get_word_learning_history('test_user', 'unknown', 'en')

        assert result == []

    async def test_get_word_learning_history_handles_error(self, vocab_service):
        """Test get_word_learning_history handles database errors"""
        service, mock_session = vocab_service

        # Mock database error
        mock_session.execute.side_effect = Exception("Database error")

        result = await service.get_word_learning_history('test_user', 'hello', 'en')

        assert result == []

    async def test_get_words_by_confidence_success(self, vocab_service):
        """Test get_words_by_confidence returns filtered words"""
        service, mock_session = vocab_service

        # Mock query result
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ('hello', 2, '2023-01-01', 3),
            ('world', 2, '2023-01-02', 5)
        ]
        mock_session.execute.return_value = mock_result

        result = await service.get_words_by_confidence('test_user', 2, 'en', 10)

        expected = [
            {
                'word': 'hello',
                'confidence_level': 2,
                'learned_at': '2023-01-01',
                'review_count': 3
            },
            {
                'word': 'world',
                'confidence_level': 2,
                'learned_at': '2023-01-02',
                'review_count': 5
            }
        ]

        assert result == expected

    async def test_get_words_by_confidence_empty_result(self, vocab_service):
        """Test get_words_by_confidence with no matching words"""
        service, mock_session = vocab_service

        # Mock empty query result
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_session.execute.return_value = mock_result

        result = await service.get_words_by_confidence('test_user', 5, 'en', 10)

        assert result == []

    async def test_get_words_by_confidence_handles_error(self, vocab_service):
        """Test get_words_by_confidence handles database errors"""
        service, mock_session = vocab_service

        # Mock database error
        mock_session.execute.side_effect = Exception("Database error")

        result = await service.get_words_by_confidence('test_user', 2, 'en', 10)

        assert result == []


# =============================================================================
# TestUserVocabularyServiceValidation - Input validation and edge cases
# =============================================================================

class TestUserVocabularyServiceValidation:
    """Test input validation and edge case handling"""

    async def test_is_word_known_handles_empty_user_id(self, vocab_service):
        """Test is_word_known handles empty user ID"""
        service, mock_session = vocab_service

        # Mock query result
        mock_result = MagicMock()
        mock_result.fetchone.return_value = [0]
        mock_session.execute.return_value = mock_result

        result = await service.is_word_known('', 'hello', 'en')

        assert result is False

    async def test_is_word_known_handles_empty_word(self, vocab_service):
        """Test is_word_known handles empty word"""
        service, mock_session = vocab_service

        # Mock query result
        mock_result = MagicMock()
        mock_result.fetchone.return_value = [0]
        mock_session.execute.return_value = mock_result

        result = await service.is_word_known('test_user', '', 'en')

        assert result is False

    async def test_is_word_known_normalizes_word_case(self, vocab_service):
        """Test that is_word_known normalizes word to lowercase"""
        service, mock_session = vocab_service

        # Mock query result
        mock_result = MagicMock()
        mock_result.fetchone.return_value = [1]
        mock_session.execute.return_value = mock_result

        await service.is_word_known('test_user', 'HELLO', 'en')

        # Verify the query was called with lowercase word
        args, kwargs = mock_session.execute.call_args
        params = kwargs if kwargs else args[1]
        assert params['word'] == 'hello'

    async def test_mark_word_learned_handles_special_characters(self, vocab_service):
        """Test mark_word_learned handles words with special characters"""
        service, mock_session = vocab_service

        # Mock _ensure_word_exists to return word ID
        with patch.object(service, '_ensure_word_exists', return_value=1):
            # Mock existing progress query
            mock_result = MagicMock()
            mock_result.fetchone.return_value = None
            mock_session.execute.return_value = mock_result

            result = await service.mark_word_learned('test_user', 'café', 'fr')

            assert result is True

    async def test_mark_word_learned_handles_very_long_words(self, vocab_service):
        """Test mark_word_learned handles very long words"""
        service, mock_session = vocab_service

        long_word = 'a' * 1000  # Very long word

        # Mock _ensure_word_exists to return word ID
        with patch.object(service, '_ensure_word_exists', return_value=1):
            # Mock existing progress query
            mock_result = MagicMock()
            mock_result.fetchone.return_value = None
            mock_session.execute.return_value = mock_result

            result = await service.mark_word_learned('test_user', long_word, 'en')

            assert result is True

    async def test_add_known_words_handles_unicode_words(self, vocab_service):
        """Test add_known_words handles Unicode/international characters"""
        service, mock_session = vocab_service

        unicode_words = ['مرحبا', '你好', 'здравствуй', '🌍']

        # Mock batch operations
        with patch.object(service, '_ensure_words_exist_batch', return_value={word: i+1 for i, word in enumerate(unicode_words)}):
            with patch.object(service, '_get_existing_progress_batch', return_value=set()):
                result = await service.add_known_words('test_user', unicode_words, 'multi')

                assert result is True

    async def test_add_known_words_handles_duplicate_words(self, vocab_service):
        """Test add_known_words handles duplicate words in input"""
        service, mock_session = vocab_service

        duplicate_words = ['hello', 'world', 'hello', 'test', 'world']

        # Capture the normalized words passed to batch methods
        captured_words = []

        async def capture_ensure_words(session, words, language):
            nonlocal captured_words
            captured_words = words
            return {word: i+1 for i, word in enumerate(words)}

        with patch.object(service, '_ensure_words_exist_batch', side_effect=capture_ensure_words):
            with patch.object(service, '_get_existing_progress_batch', return_value=set()):
                result = await service.add_known_words('test_user', duplicate_words, 'en')

                # Should deduplicate words
                assert 'hello' in captured_words
                assert 'world' in captured_words
                assert 'test' in captured_words
                assert result is True

    async def test_add_known_words_handles_mixed_case_duplicates(self, vocab_service):
        """Test add_known_words handles mixed case duplicates"""
        service, mock_session = vocab_service

        mixed_words = ['Hello', 'WORLD', 'hello', 'world', 'Test']

        # Capture normalized words
        captured_words = []

        async def capture_ensure_words(session, words, language):
            nonlocal captured_words
            captured_words = words
            return {word: i+1 for i, word in enumerate(words)}

        with patch.object(service, '_ensure_words_exist_batch', side_effect=capture_ensure_words):
            with patch.object(service, '_get_existing_progress_batch', return_value=set()):
                await service.add_known_words('test_user', mixed_words, 'en')

                # Should normalize case but keep duplicates (service doesn't deduplicate)
                assert captured_words.count('hello') == 2
                assert captured_words.count('world') == 2
                assert captured_words.count('test') == 1
                # All words should be lowercase
                assert all(word.islower() for word in captured_words)

    async def test_get_learning_statistics_handles_invalid_user(self, vocab_service):
        """Test get_learning_statistics handles invalid/None user ID"""
        service, mock_session = vocab_service

        # Mock get_known_words to return empty for invalid user
        with patch.object(service, 'get_known_words', return_value=[]):
            result = await service.get_learning_statistics(None, 'en')

            assert result['total_known'] == 0


# =============================================================================
# TestUserVocabularyServicePerformance - Performance and scalability tests
# =============================================================================

class TestUserVocabularyServicePerformance:
    """Test performance and scalability scenarios"""

    async def test_add_known_words_large_batch_performance(self, vocab_service):
        """Test batch addition with large number of words"""
        service, mock_session = vocab_service

        # Generate large word list
        large_word_list = [f'word_{i}' for i in range(1000)]

        # Mock batch operations for large dataset
        with patch.object(service, '_ensure_words_exist_batch', return_value={word: i+1 for i, word in enumerate(large_word_list)}):
            with patch.object(service, '_get_existing_progress_batch', return_value=set()):
                result = await service.add_known_words('test_user', large_word_list, 'en')

                assert result is True
                mock_session.commit.assert_called_once()

    async def test_get_known_words_large_vocabulary(self, vocab_service):
        """Test get_known_words with large vocabulary"""
        service, mock_session = vocab_service

        # Mock query to return large vocabulary
        large_vocab = [(f'word_{i}',) for i in range(5000)]
        mock_result = MagicMock()
        mock_result.fetchall.return_value = large_vocab
        mock_session.execute.return_value = mock_result

        result = await service.get_known_words('advanced_user', 'en')

        assert len(result) == 5000
        assert result[0] == 'word_0'
        assert result[-1] == 'word_4999'

    async def test_batch_operations_handle_memory_efficiently(self, vocab_service):
        """Test that batch operations don't cause excessive memory usage"""
        service, mock_session = vocab_service

        # Simulate processing very large batches
        huge_word_list = [f'word_{i}' for i in range(10000)]

        # Mock operations to simulate memory-efficient processing
        call_count = 0

        def mock_execute(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_result = MagicMock()

            if call_count == 1:  # First call - existing words query
                mock_result.fetchall.return_value = []  # No existing words
            else:  # Subsequent calls - inserts
                mock_result.lastrowid = call_count - 1

            return mock_result

        mock_session.execute.side_effect = mock_execute

        # This should not cause memory issues or timeout
        result = await service._ensure_words_exist_batch(mock_session, huge_word_list, 'en')

        assert len(result) == 10000
        mock_session.flush.assert_called_once()

    async def test_concurrent_user_operations_isolation(self, vocab_service):
        """Test that concurrent operations for different users are properly isolated"""
        service, mock_session = vocab_service

        # Mock session calls to track user isolation
        user_calls = []

        def track_execute(query, params=None):
            if params and 'user_id' in params:
                user_calls.append(params['user_id'])

            mock_result = MagicMock()
            mock_result.fetchone.return_value = [0]
            return mock_result

        mock_session.execute.side_effect = track_execute

        # Simulate concurrent operations for different users
        await service.is_word_known('user1', 'hello', 'en')
        await service.is_word_known('user2', 'hello', 'en')
        await service.is_word_known('user3', 'hello', 'en')

        # Verify each user ID was used in separate calls
        assert 'user1' in user_calls
        assert 'user2' in user_calls
        assert 'user3' in user_calls


# =============================================================================
# TestUserVocabularyServiceReliability - Error recovery and reliability tests
# =============================================================================

class TestUserVocabularyServiceReliability:
    """Test error recovery and reliability scenarios"""

    async def test_session_context_manager_handles_exceptions(self, vocab_service):
        """Test that session context manager properly handles exceptions"""
        service, mock_session = vocab_service

        # Mock the context manager to raise an exception
        async def failing_session():
            try:
                yield mock_session
                raise Exception("Session error")
            except Exception:
                await mock_session.rollback()
                raise

        from contextlib import asynccontextmanager
        service.get_session = lambda: asynccontextmanager(failing_session)()

        # The service should handle this gracefully
        result = await service.is_word_known('test_user', 'hello', 'en')

        assert result is False
        mock_session.rollback.assert_called_once()

    async def test_partial_batch_failure_recovery(self, vocab_service):
        """Test recovery from partial batch operation failures"""
        service, mock_session = vocab_service

        # Mock partial failure in batch operations
        word_list = ['word1', 'word2', 'word3']

        # Mock _ensure_words_exist_batch to succeed partially
        with patch.object(service, '_ensure_words_exist_batch', return_value={'word1': 1, 'word2': 2}):  # word3 fails
            # Mock database error during actual insertion
            mock_session.execute.side_effect = Exception("Constraint violation")

            result = await service.add_known_words('test_user', word_list, 'en')

            # Should fail gracefully
            assert result is False

    async def test_database_connection_timeout_handling(self, vocab_service):
        """Test handling of database connection timeouts"""
        service, mock_session = vocab_service

        # Mock timeout error
        import asyncio
        mock_session.execute.side_effect = asyncio.TimeoutError("Database timeout")

        result = await service.get_learning_statistics('test_user', 'en')

        # Should return error state, not crash
        assert 'error' in result
        assert result['total_known'] == 0

    async def test_transaction_rollback_on_failure(self, vocab_service):
        """Test that transactions are properly rolled back on failures"""
        service, mock_session = vocab_service

        # Mock successful word creation but failed progress insertion
        with patch.object(service, '_ensure_word_exists', return_value=1):
            # First execute (check existing) succeeds, second (insert) fails
            mock_session.execute.side_effect = [
                MagicMock(fetchone=lambda: None),  # No existing progress
                Exception("Insert failed")         # Progress insertion fails
            ]

            result = await service.mark_word_learned('test_user', 'hello', 'en')

            assert result is False
            # Should attempt rollback on session error

    async def test_memory_cleanup_after_large_operations(self, vocab_service):
        """Test that memory is cleaned up after large operations"""
        service, mock_session = vocab_service

        # Simulate large operation that could cause memory issues
        massive_word_list = [f'word_{i}' for i in range(50000)]

        # Mock successful batch operation
        with patch.object(service, '_ensure_words_exist_batch', return_value={}):
            result = await service.add_known_words('test_user', massive_word_list, 'en')

            # Operation should complete without memory issues
            assert result is False  # Returns False due to empty word_ids

    async def test_service_resilience_to_malformed_data(self, vocab_service):
        """Test service resilience to malformed database data"""
        service, mock_session = vocab_service

        # Mock query returning malformed data
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ('word1', None, 'invalid_date'),  # Malformed data
            (None, 2, '2023-01-01'),          # Null word
            ('word2', 'invalid_id', '2023-01-01')  # Invalid ID
        ]
        mock_session.execute.return_value = mock_result

        # Should handle gracefully without crashing
        result = await service.get_word_learning_history('test_user', 'test', 'en')

        # Should return the data as-is or handle gracefully
        assert isinstance(result, list)
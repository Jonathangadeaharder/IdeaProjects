"""
Comprehensive test suite for VocabularyService
Tests multilingual vocabulary operations, user progress tracking, and database interactions
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID, uuid4

from services.vocabulary_service import VocabularyService, get_vocabulary_service
from database.models import VocabularyConcept, VocabularyTranslation, Language, UserLearningProgress


class TestVocabularyService:
    """Test VocabularyService initialization and basic functionality"""

    def test_initialization(self):
        """Test service initialization"""
        service = VocabularyService()
        assert service is not None

    def test_get_vocabulary_service_utility(self):
        """Test utility function for service creation"""
        service = get_vocabulary_service()
        assert isinstance(service, VocabularyService)


class TestGetSupportedLanguages:
    """Test supported languages functionality"""

    @pytest.fixture
    def service(self):
        return VocabularyService()

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_get_supported_languages_success(self, mock_session_local, service):
        """Test successful retrieval of supported languages"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        # Mock language objects
        mock_lang_en = Mock()
        mock_lang_en.code = 'en'
        mock_lang_en.name = 'English'
        mock_lang_en.native_name = 'English'
        mock_lang_en.is_active = True

        mock_lang_de = Mock()
        mock_lang_de.code = 'de'
        mock_lang_de.name = 'German'
        mock_lang_de.native_name = 'Deutsch'
        mock_lang_de.is_active = True

        mock_lang_es = Mock()
        mock_lang_es.code = 'es'
        mock_lang_es.name = 'Spanish'
        mock_lang_es.native_name = 'Español'
        mock_lang_es.is_active = True

        mock_languages = [mock_lang_en, mock_lang_de, mock_lang_es]
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_languages
        mock_session.execute.return_value = mock_result

        result = await service.get_supported_languages()

        # Verify result structure
        assert len(result) == 3
        assert result[0]['code'] == 'en'
        assert result[0]['name'] == 'English'
        assert result[0]['native_name'] == 'English'
        assert result[0]['is_active'] is True

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_get_supported_languages_empty(self, mock_session_local, service):
        """Test retrieval when no languages are active"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        result = await service.get_supported_languages()

        assert result == []

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_get_supported_languages_database_error(self, mock_session_local, service):
        """Test database error handling"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session
        mock_session.execute.side_effect = Exception("Database connection error")

        with pytest.raises(Exception, match="Database connection error"):
            await service.get_supported_languages()


class TestGetVocabularyStats:
    """Test vocabulary statistics functionality"""

    @pytest.fixture
    def service(self):
        return VocabularyService()

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_get_vocabulary_stats_without_user(self, mock_session_local, service):
        """Test vocabulary stats without specific user"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        # Mock level counts - simulate different counts for each level
        level_counts = {"A1": 100, "A2": 150, "B1": 200, "B2": 250, "C1": 180, "C2": 120}

        def mock_execute_side_effect(query):
            mock_result = Mock()
            # Determine which level is being queried based on call order
            call_count = mock_session.execute.call_count
            level_keys = list(level_counts.keys())
            if call_count <= len(level_keys):
                level = level_keys[call_count - 1]
                mock_result.scalar.return_value = level_counts[level]
            else:
                mock_result.scalar.return_value = 0
            return mock_result

        mock_session.execute.side_effect = mock_execute_side_effect

        result = await service.get_vocabulary_stats(target_language="de")

        # Verify result structure
        assert "levels" in result
        assert "target_language" in result
        assert result["target_language"] == "de"
        assert "total_words" in result
        assert "total_known" in result

        # Verify all levels are present
        for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
            assert level in result["levels"]
            assert "total_words" in result["levels"][level]
            assert "user_known" in result["levels"][level]

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_get_vocabulary_stats_with_user(self, mock_session_local, service):
        """Test vocabulary stats with specific user"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        # Mock alternating calls for level counts and known counts
        call_results = [100, 25, 150, 30, 200, 40, 250, 50, 180, 35, 120, 20]  # total, known for each level
        call_index = 0

        def mock_execute_side_effect(query):
            nonlocal call_index
            mock_result = Mock()
            mock_result.scalar.return_value = call_results[call_index] if call_index < len(call_results) else 0
            call_index += 1
            return mock_result

        mock_session.execute.side_effect = mock_execute_side_effect

        result = await service.get_vocabulary_stats(target_language="de", user_id=123)

        # Verify result includes user data
        assert result["total_known"] > 0

        # Check that some levels have known words
        has_known_words = any(result["levels"][level]["user_known"] > 0 for level in result["levels"])
        assert has_known_words

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_get_vocabulary_stats_database_error(self, mock_session_local, service):
        """Test database error handling in stats"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await service.get_vocabulary_stats()

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_get_vocabulary_level_success(self, mock_session_local, service):
        """Test successful vocabulary level retrieval"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        # Mock vocabulary concepts with translations
        concept_id = str(uuid4())
        mock_concept = Mock()
        mock_concept.id = concept_id
        mock_concept.difficulty_level = "A1"
        mock_concept.semantic_category = "noun"
        mock_concept.domain = "general"

        # Mock translations
        target_translation = Mock()
        target_translation.language_code = "de"
        target_translation.word = "Hund"
        target_translation.lemma = "Hund"
        target_translation.gender = "der"
        target_translation.plural_form = "Hunde"
        target_translation.pronunciation = "/hʊnt/"
        target_translation.notes = "Common animal"

        spanish_translation = Mock()
        spanish_translation.language_code = "es"
        spanish_translation.word = "perro"

        mock_concept.translations = [target_translation, spanish_translation]

        # Use flexible mock that doesn't depend on call order
        mock_concepts = [mock_concept]
        user_progress = {}  # User doesn't know any words

        def mock_execute(query):
            result = Mock()
            # Mock the scalars().all() chain for VocabularyConcept queries
            scalars_mock = Mock()
            scalars_mock.all.return_value = mock_concepts  # Return the list directly
            result.scalars.return_value = scalars_mock

            # Mock fetchall() for user progress queries
            result.fetchall.return_value = list(user_progress.items())
            return result

        mock_session.execute.side_effect = mock_execute

        result = await service.get_vocabulary_level("A1", target_language="de", translation_language="es", user_id=123)

        # Verify result structure
        assert result["level"] == "A1"
        assert result["target_language"] == "de"
        assert result["translation_language"] == "es"
        assert len(result["words"]) == 1

        word = result["words"][0]
        assert word["concept_id"] == concept_id
        assert word["word"] == "Hund"
        assert word["translation"] == "perro"
        assert word["gender"] == "der"
        assert word["known"] is False

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_get_vocabulary_level_with_known_words_updated(self, mock_session_local, service):
        """Test vocabulary level retrieval with user's known words"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        concept_id = str(uuid4())
        mock_concept = Mock()
        mock_concept.id = concept_id
        mock_concept.difficulty_level = "A1"

        target_translation = Mock()
        target_translation.language_code = "de"
        target_translation.word = "Katze"
        mock_concept.translations = [target_translation]

        concepts_result = Mock()
        concepts_result.scalars.return_value.all.return_value = [mock_concept]

        # User knows this concept
        user_known_result = Mock()
        user_known_result.fetchall.return_value = [(concept_id,)]

        mock_session.execute.side_effect = [concepts_result, user_known_result]

        result = await service.get_vocabulary_level("A1", user_id=123)

        assert result["known_count"] == 1
        assert result["words"][0]["known"] is True

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_get_vocabulary_level_no_target_translation(self, mock_session_local, service):
        """Test filtering out concepts without target language translation"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        # Concept with only Spanish translation, no German
        mock_concept = Mock()
        mock_concept.id = str(uuid4())
        spanish_translation = Mock()
        spanish_translation.language_code = "es"
        spanish_translation.word = "gato"
        mock_concept.translations = [spanish_translation]

        concepts_result = Mock()
        concepts_result.scalars.return_value.all.return_value = [mock_concept]

        user_known_result = Mock()
        user_known_result.fetchall.return_value = []

        mock_session.execute.side_effect = [concepts_result, user_known_result]

        result = await service.get_vocabulary_level("A1", target_language="de")

        # Should be filtered out due to no German translation
        assert len(result["words"]) == 0

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_get_vocabulary_level_database_error(self, mock_session_local, service):
        """Test database error handling"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await service.get_vocabulary_level("A1")


# Module-level fixtures
@pytest.fixture
def service():
    """Service fixture available to all test classes"""
    return VocabularyService()

@pytest.fixture
async def mock_session_with_vocab_data():
    """Fixture providing mock session with vocabulary test data"""
    mock_session = AsyncMock()

    # Create sample vocabulary concepts
    mock_concepts = []
    concept_id = str(uuid4())
    mock_concept = Mock()
    mock_concept.id = concept_id
    mock_concept.difficulty_level = "A1"

    # Mock translations
    target_translation = Mock()
    target_translation.language_code = "de"
    target_translation.word = "Hund"
    target_translation.gender = "der"

    spanish_translation = Mock()
    spanish_translation.language_code = "es"
    spanish_translation.word = "perro"

    mock_concept.translations = [target_translation, spanish_translation]
    mock_concepts.append(mock_concept)

    # Track user progress (concept_id -> known status)
    user_progress = {}

    # Flexible mock execute that handles different query types
    def mock_execute(query):
        result = Mock()
        query_str = str(query)
        if 'vocabulary_concepts' in query_str and 'user_learning_progress' not in query_str:
            # Concept query - need proper scalars().all() chain
            scalars_mock = Mock()
            # Return current contents of mock_concepts list (allowing dynamic modification)
            current_concepts = list(mock_concepts)
            scalars_mock.all.return_value = current_concepts
            result.scalars.return_value = scalars_mock
        else:
            # User progress query
            result.fetchall.return_value = [(cid, True) for cid, known in user_progress.items() if known]
        return result

    mock_session.execute.side_effect = mock_execute

    with patch('services.vocabulary_service.AsyncSessionLocal') as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = mock_session
        yield mock_session, mock_concepts, user_progress


class TestMarkConceptKnown:
    """Test marking concepts as known/unknown"""

    @pytest.fixture
    def service(self):
        return VocabularyService()

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_mark_concept_known_new_progress(self, mock_session_local, service):
        """Test marking concept as known for first time"""
        mock_session = AsyncMock()
        # session.add should be synchronous, not async
        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        concept_id = str(uuid4())

        # No existing progress
        existing_result = Mock()
        existing_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = existing_result

        result = await service.mark_concept_known(123, concept_id, True)

        # Verify new progress was added
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

        assert result["success"] is True
        assert result["concept_id"] == concept_id
        assert result["known"] is True

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_mark_concept_unknown_existing_progress(self, mock_session_local, service):
        """Test marking concept as unknown (removing progress)"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        concept_id = str(uuid4())

        # Existing progress
        mock_progress = Mock()
        existing_result = Mock()
        existing_result.scalar_one_or_none.return_value = mock_progress
        mock_session.execute.return_value = existing_result

        result = await service.mark_concept_known(123, concept_id, False)

        # Verify progress was deleted
        mock_session.delete.assert_called_once_with(mock_progress)
        mock_session.commit.assert_called_once()

        assert result["success"] is True
        assert result["known"] is False

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_mark_concept_known_already_exists(self, mock_session_local, service):
        """Test marking concept as known when already exists"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        concept_id = str(uuid4())

        # Existing progress
        mock_progress = Mock()
        existing_result = Mock()
        existing_result.scalar_one_or_none.return_value = mock_progress
        mock_session.execute.return_value = existing_result

        result = await service.mark_concept_known(123, concept_id, True)

        # Should not add new progress since it already exists
        mock_session.add.assert_not_called()
        mock_session.commit.assert_called_once()

        assert result["success"] is True

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_mark_concept_known_database_error(self, mock_session_local, service):
        """Test database error handling"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session
        mock_session.execute.side_effect = Exception("Database error")

        concept_id = str(uuid4())

        with pytest.raises(Exception, match="Database error"):
            await service.mark_concept_known(123, concept_id, True)


class TestBulkMarkLevel:
    """Test bulk marking level functionality"""

    @pytest.fixture
    def service(self):
        return VocabularyService()

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_bulk_mark_level_known(self, mock_session_local, service):
        """Test bulk marking level as known"""
        mock_session = AsyncMock()
        # session.add should be synchronous, not async
        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        # Mock concept IDs for the level
        concept_ids = [str(uuid4()), str(uuid4()), str(uuid4())]

        # Mock getting concept IDs
        concepts_result = Mock()
        concepts_result.fetchall.return_value = [(cid,) for cid in concept_ids]

        # Mock checking existing progress (none exist)
        existing_results = [Mock() for _ in concept_ids]
        for result in existing_results:
            result.scalar_one_or_none.return_value = None

        mock_session.execute.side_effect = [concepts_result] + existing_results

        result = await service.bulk_mark_level(123, "A1", "de", True)

        # Should add 3 new progress records
        assert mock_session.add.call_count == 3
        mock_session.commit.assert_called_once()

        assert result["success"] is True
        assert result["level"] == "A1"
        assert result["known"] is True
        assert result["word_count"] == 3

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_bulk_mark_level_unknown(self, mock_session_local, service):
        """Test bulk marking level as unknown"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        concept_ids = [str(uuid4()), str(uuid4())]

        # Mock getting concept IDs
        concepts_result = Mock()
        concepts_result.fetchall.return_value = [(cid,) for cid in concept_ids]

        # Mock existing progress records
        mock_progress_1 = Mock()
        mock_progress_2 = Mock()
        existing_results = [Mock(), Mock()]
        existing_results[0].scalar_one_or_none.return_value = mock_progress_1
        existing_results[1].scalar_one_or_none.return_value = mock_progress_2

        mock_session.execute.side_effect = [concepts_result] + existing_results

        result = await service.bulk_mark_level(123, "A1", "de", False)

        # Should delete 2 progress records
        mock_session.delete.assert_any_call(mock_progress_1)
        mock_session.delete.assert_any_call(mock_progress_2)
        assert mock_session.delete.call_count == 2

        assert result["success"] is True
        assert result["known"] is False
        assert result["word_count"] == 2

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_bulk_mark_level_mixed_existing(self, mock_session_local, service):
        """Test bulk marking with mixed existing progress"""
        mock_session = AsyncMock()
        # session.add should be synchronous, not async
        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        concept_ids = [str(uuid4()), str(uuid4())]

        concepts_result = Mock()
        concepts_result.fetchall.return_value = [(cid,) for cid in concept_ids]

        # First concept has no progress, second has existing progress
        existing_results = [Mock(), Mock()]
        existing_results[0].scalar_one_or_none.return_value = None
        existing_results[1].scalar_one_or_none.return_value = Mock()

        mock_session.execute.side_effect = [concepts_result] + existing_results

        result = await service.bulk_mark_level(123, "A1", "de", True)

        # Should only add 1 new progress (first concept)
        assert mock_session.add.call_count == 1
        assert result["word_count"] == 1

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_bulk_mark_level_database_error(self, mock_session_local, service):
        """Test database error handling"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session
        mock_session.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await service.bulk_mark_level(123, "A1", "de", True)


class TestGetUserKnownConcepts:
    """Test internal method for getting user's known concepts"""

    @pytest.fixture
    def service(self):
        return VocabularyService()

    async def test_get_vocabulary_level_with_known_words(self, service, mock_session_with_vocab_data):
        """Test vocabulary level retrieval shows known words correctly"""
        # Setup: User knows some concepts
        mock_session, mock_concepts, user_progress = mock_session_with_vocab_data
        known_concept_id = str(uuid4())
        user_progress[known_concept_id] = True  # User knows this concept

        # Add known concept to mock data
        known_concept = Mock()
        known_concept.id = known_concept_id
        known_concept.difficulty_level = "A1"
        known_concept.translations = [Mock(language_code="de", word="Test", gender="der"),
                                      Mock(language_code="es", word="Prueba")]
        mock_concepts.append(known_concept)

        result = await service.get_vocabulary_level("A1", target_language="de",
                                                   translation_language="es", user_id=123)

        # Verify business logic: known words are marked correctly
        known_words = [w for w in result["words"] if w["known"] is True]
        assert len(known_words) >= 1
        assert any(w["concept_id"] == known_concept_id for w in known_words)

    async def test_get_vocabulary_level_with_no_known_words(self, service, mock_session_with_vocab_data):
        """Test vocabulary level retrieval when user knows no words"""
        mock_session, mock_concepts, user_progress = mock_session_with_vocab_data
        # user_progress is empty = no known words

        result = await service.get_vocabulary_level("A1", target_language="de",
                                                   translation_language="es", user_id=123)

        # Verify business logic: no words marked as known
        assert all(word["known"] is False for word in result["words"])
        assert result["level"] == "A1"
        assert result["target_language"] == "de"
        assert result["translation_language"] == "es"

    async def test_get_vocabulary_level_empty_level(self, service, mock_session_with_vocab_data):
        """Test vocabulary level retrieval for level with no vocabulary"""
        mock_session, mock_concepts, user_progress = mock_session_with_vocab_data
        mock_concepts.clear()  # No concepts for this level

        result = await service.get_vocabulary_level("C2", target_language="de",
                                                   translation_language="es", user_id=123)

        # Verify business logic: empty results handled gracefully
        assert result["words"] == []
        assert result["level"] == "C2"


class TestSessionManagement:
    """Test session management functionality"""

    @pytest.fixture
    def service(self):
        return VocabularyService()

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_session_context_manager(self, mock_session_local, service):
        """Test session context manager"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session
        mock_session_local.return_value.__aexit__ = AsyncMock()

        async with service._get_session() as session:
            assert session is mock_session

        # Verify session was properly managed
        mock_session_local.assert_called_once()


class TestEdgeCases:
    """Test edge cases and error scenarios"""

    @pytest.fixture
    def service(self):
        return VocabularyService()

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_get_vocabulary_level_pagination(self, mock_session_local, service):
        """Test pagination parameters in vocabulary level"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        concepts_result = Mock()
        concepts_result.scalars.return_value.all.return_value = []
        user_known_result = Mock()
        user_known_result.fetchall.return_value = []

        mock_session.execute.side_effect = [concepts_result, user_known_result]

        await service.get_vocabulary_level("A1", limit=10, offset=20)

        # Verify that the method was called and handled pagination parameters
        # The exact call count depends on whether user_id is provided
        assert mock_session.execute.call_count >= 1

    @patch('services.vocabulary_service.AsyncSessionLocal')
    async def test_case_insensitive_level_handling(self, mock_session_local, service):
        """Test that level parameters are handled case-insensitively"""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        concepts_result = Mock()
        concepts_result.scalars.return_value.all.return_value = []
        user_known_result = Mock()
        user_known_result.fetchall.return_value = []

        mock_session.execute.side_effect = [concepts_result, user_known_result]

        result = await service.get_vocabulary_level("a1")  # lowercase input

        # Should normalize to uppercase
        assert result["level"] == "A1"
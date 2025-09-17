"""Unit tests for VocabularyService"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from services.dataservice.authenticated_user_vocabulary_service import AuthenticatedUserVocabularyService
from database.models import User


@pytest.mark.asyncio
class TestAuthenticatedUserVocabularyService:
    """Test cases for AuthenticatedUserVocabularyService"""
    
    @pytest.fixture
    def mock_auth_user(self):
        """Mock authenticated user"""
        user = Mock(spec=User)
        user.id = 1
        user.username = "testuser"
        user.is_superuser = False
        return user
    
    @pytest.fixture
    def mock_db_manager(self):
        """Mock database manager"""
        return Mock()
    
    @pytest.fixture
    def mock_auth_service(self, mock_auth_user):
        """Mock authentication service"""
        auth_service = Mock()
        auth_service.validate_session.return_value = mock_auth_user
        return auth_service
    
    @pytest.fixture
    def vocab_service(self, mock_db_manager):
        """Create AuthenticatedUserVocabularyService instance with mocked dependencies"""
        service = AuthenticatedUserVocabularyService(db_session=mock_db_manager)
        # Mock the underlying vocab service
        service.vocab_service = Mock()
        return service
    
    
    async def test_get_known_words_success(self, vocab_service, mock_auth_user):
        """Test successful known words retrieval"""
        # Arrange
        user_id = "1"
        language = "en"
        expected_words = {"hello", "world", "test"}
        
        # Mock the underlying service
        vocab_service.vocab_service.get_known_words = AsyncMock(return_value=expected_words)
        
        # Act
        result = await vocab_service.get_known_words(mock_auth_user, user_id, language)
        
        # Assert
        assert result == expected_words
        vocab_service.vocab_service.get_known_words.assert_called_once_with(user_id, language)
    
    
    async def test_mark_word_learned_success(self, vocab_service, mock_auth_user):
        """Test successful word marking as learned"""
        # Arrange
        user_id = "1"
        word = "hello"
        language = "en"
        
        # Mock the underlying service
        vocab_service.vocab_service.mark_word_learned = AsyncMock(return_value=True)
        
        # Act
        result = await vocab_service.mark_word_learned(mock_auth_user, user_id, word, language)
        
        # Assert
        assert result is True
        vocab_service.vocab_service.mark_word_learned.assert_called_once_with(user_id, word, language)
    
    
    async def test_remove_word_success(self, vocab_service, mock_auth_user):
        """Test successful word removal"""
        # Arrange
        user_id = "1"
        word = "hello"
        language = "en"
        
        # Mock the underlying service
        vocab_service.vocab_service.remove_word = AsyncMock(return_value=True)
        
        # Act
        result = await vocab_service.remove_word(mock_auth_user, user_id, word, language)
        
        # Assert
        assert result is True
        vocab_service.vocab_service.remove_word.assert_called_once_with(user_id, word, language)
    
    
    async def test_is_word_known_success(self, vocab_service, mock_auth_user):
        """Test successful word known check"""
        # Arrange
        user_id = "1"
        word = "hello"
        language = "en"
        
        # Mock the underlying service
        vocab_service.vocab_service.is_word_known = AsyncMock(return_value=True)
        
        # Act
        result = await vocab_service.is_word_known(mock_auth_user, user_id, word, language)
        
        # Assert
        assert result is True
        vocab_service.vocab_service.is_word_known.assert_called_once_with(user_id, word, language)
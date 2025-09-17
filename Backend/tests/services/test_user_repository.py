"""
Unit tests for UserRepository
Tests the standardized repository pattern for user data access
"""
import pytest
from unittest.mock import Mock, patch
import sqlite3
from datetime import datetime
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from services.repository.user_repository import UserRepository, User


class TestUserRepository:
    """Test suite for UserRepository"""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Mock database manager for testing"""
        from unittest.mock import MagicMock
        mock_db = Mock()
        mock_conn = Mock()
        mock_cursor = Mock()

        # Setup connection and cursor mocks
        mock_conn.cursor.return_value = mock_cursor

        # Setup context manager properly
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_conn
        mock_context_manager.__exit__.return_value = None
        mock_db.get_connection.return_value = mock_context_manager
        
        return mock_db, mock_conn, mock_cursor
    
    @pytest.fixture
    def repository(self, mock_db_manager):
        """Create UserRepository with mocked database"""
        mock_db, _, _ = mock_db_manager
        return UserRepository(mock_db)
    
    @pytest.fixture
    def sample_user(self):
        """Sample user for testing"""
        return User(
            id=1,
            username="testuser",
            hashed_password="hashed_password",
            email="test@example.com",
            native_language="en",
            target_language="de",
            created_at=datetime.now()
        )
    
    def test_table_name(self, repository):
        """Test table name property"""
        assert repository.table_name == "users"
    
    def test_row_to_model_conversion(self, repository):
        """Test conversion from database row to User model"""
        row_data = {
            'id': 1,
            'username': 'testuser',
            'hashed_password': 'hashed_password',
            'email': 'test@example.com',
            'native_language': 'en',
            'target_language': 'de',
            'created_at': '2024-01-01T12:00:00'
        }
        
        user = repository._row_to_model(row_data)
        
        assert isinstance(user, User)
        assert user.id == 1
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_password"
        assert user.email == "test@example.com"
        assert user.native_language == "en"
        assert user.target_language == "de"
    
    def test_model_to_dict_conversion(self, repository, sample_user):
        """Test conversion from User model to dictionary"""
        data = repository._model_to_dict(sample_user)
        
        assert isinstance(data, dict)
        assert data['id'] == sample_user.id
        assert data['username'] == sample_user.username
        assert data['hashed_password'] == sample_user.hashed_password
        assert data['email'] == sample_user.email
        assert data['native_language'] == sample_user.native_language
        assert data['target_language'] == sample_user.target_language
        assert 'created_at' in data
    
    def test_find_by_id_success(self, repository, mock_db_manager):
        """Test finding user by ID when user exists"""
        _, mock_conn, mock_cursor = mock_db_manager
        
        # Mock database response
        mock_row = Mock()
        mock_row.keys.return_value = ['id', 'username', 'hashed_password', 'email', 'native_language', 'target_language', 'created_at']
        mock_row.__getitem__ = lambda self, key: {
            'id': 1,
            'username': 'testuser',
            'hashed_password': 'hashed_password',
            'email': 'test@example.com',
            'native_language': 'en',
            'target_language': 'de',
            'created_at': '2024-01-01T12:00:00'
        }[key]
        mock_cursor.fetchone.return_value = mock_row
        
        # Mock dict() conversion
        with patch('builtins.dict', return_value={
            'id': 1,
            'username': 'testuser',
            'hashed_password': 'hashed_password',
            'email': 'test@example.com',
            'native_language': 'en',
            'target_language': 'de',
            'created_at': '2024-01-01T12:00:00'
        }):
            user = repository.find_by_id(1)
        
        assert user is not None
        assert user.id == 1
        assert user.username == "testuser"
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE id = ?", (1,))
    
    def test_find_by_id_not_found(self, repository, mock_db_manager):
        """Test finding user by ID when user doesn't exist"""
        _, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.fetchone.return_value = None
        
        user = repository.find_by_id(999)
        
        assert user is None
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE id = ?", (999,))
    
    def test_find_by_username_success(self, repository, mock_db_manager):
        """Test finding user by username when user exists"""
        _, mock_conn, mock_cursor = mock_db_manager
        
        # Mock database response
        mock_row = Mock()
        mock_cursor.fetchone.return_value = mock_row
        
        with patch('builtins.dict', return_value={
            'id': 1,
            'username': 'testuser',
            'hashed_password': 'hashed_password',
            'email': 'test@example.com',
            'native_language': 'en',
            'target_language': 'de',
            'created_at': '2024-01-01T12:00:00'
        }):
            user = repository.find_by_username("testuser")
        
        assert user is not None
        assert user.username == "testuser"
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE username = ?", ("testuser",))
    
    def test_find_by_username_not_found(self, repository, mock_db_manager):
        """Test finding user by username when user doesn't exist"""
        _, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.fetchone.return_value = None
        
        user = repository.find_by_username("nonexistent")
        
        assert user is None
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE username = ?", ("nonexistent",))
    
    def test_find_by_email_success(self, repository, mock_db_manager):
        """Test finding user by email when user exists"""
        _, mock_conn, mock_cursor = mock_db_manager
        
        mock_row = Mock()
        mock_cursor.fetchone.return_value = mock_row
        
        with patch('builtins.dict', return_value={
            'id': 1,
            'username': 'testuser',
            'hashed_password': 'hashed_password',
            'email': 'test@example.com',
            'native_language': 'en',
            'target_language': 'de',
            'created_at': '2024-01-01T12:00:00'
        }):
            user = repository.find_by_email("test@example.com")
        
        assert user is not None
        assert user.email == "test@example.com"
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users WHERE email = ?", ("test@example.com",))
    
    def test_username_exists_true(self, repository, mock_db_manager):
        """Test username exists check when username is taken"""
        _, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.fetchone.return_value = (1,)  # Count = 1
        
        exists = repository.username_exists("existinguser")
        
        assert exists is True
        mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM users WHERE username = ?", ("existinguser",))
    
    def test_username_exists_false(self, repository, mock_db_manager):
        """Test username exists check when username is available"""
        _, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.fetchone.return_value = (0,)  # Count = 0
        
        exists = repository.username_exists("newuser")
        
        assert exists is False
        mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM users WHERE username = ?", ("newuser",))
    
    def test_username_exists_exclude_id(self, repository, mock_db_manager):
        """Test username exists check excluding specific user ID"""
        _, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.fetchone.return_value = (0,)  # Count = 0
        
        exists = repository.username_exists("existinguser", exclude_id=1)
        
        assert exists is False
        mock_cursor.execute.assert_called_once_with(
            "SELECT COUNT(*) FROM users WHERE username = ? AND id != ?", 
            ("existinguser", 1)
        )
    
    def test_email_exists_true(self, repository, mock_db_manager):
        """Test email exists check when email is taken"""
        _, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.fetchone.return_value = (1,)  # Count = 1
        
        exists = repository.email_exists("existing@example.com")
        
        assert exists is True
        mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM users WHERE email = ?", ("existing@example.com",))
    
    def test_update_language_preference_success(self, repository, mock_db_manager):
        """Test updating user language preferences"""
        mock_db, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.rowcount = 1
        
        # Mock transaction
        mock_db.transaction.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db.transaction.return_value.__exit__ = Mock(return_value=None)
        
        result = repository.update_language_preference(1, "de", "en")
        
        assert result is True
        mock_cursor.execute.assert_called_once_with(
            "UPDATE users SET native_language = ?, target_language = ? WHERE id = ?",
            ("de", "en", 1)
        )
    
    def test_update_language_preference_user_not_found(self, repository, mock_db_manager):
        """Test updating language preferences when user doesn't exist"""
        mock_db, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.rowcount = 0
        
        # Mock transaction
        mock_db.transaction.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db.transaction.return_value.__exit__ = Mock(return_value=None)
        
        result = repository.update_language_preference(999, "de", "en")
        
        assert result is False
    
    def test_update_password_success(self, repository, mock_db_manager):
        """Test updating user password"""
        mock_db, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.rowcount = 1
        
        # Mock transaction
        mock_db.transaction.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db.transaction.return_value.__exit__ = Mock(return_value=None)
        
        result = repository.update_password(1, "new_hashed_password")
        
        assert result is True
        mock_cursor.execute.assert_called_once_with(
            "UPDATE users SET hashed_password = ? WHERE id = ?",
            ("new_hashed_password", 1)
        )
    

    def test_error_handling_database_error(self, repository, mock_db_manager):
        """Test error handling when database operations fail"""
        _, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.execute.side_effect = sqlite3.Error("Database error")
        
        with pytest.raises(sqlite3.Error):
            repository.find_by_id(1)
    
    def test_count_with_criteria(self, repository, mock_db_manager):
        """Test counting entities with criteria"""
        _, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.fetchone.return_value = (5,)  # Count = 5
        
        count = repository.count({"native_language": "en"})
        
        assert count == 5
        mock_cursor.execute.assert_called_once_with(
            "SELECT COUNT(*) FROM users WHERE native_language = ?",
            ["en"]
        )
    
    def test_count_without_criteria(self, repository, mock_db_manager):
        """Test counting all entities"""
        _, mock_conn, mock_cursor = mock_db_manager
        mock_cursor.fetchone.return_value = (10,)  # Count = 10
        
        count = repository.count()
        
        assert count == 10
        mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM users")

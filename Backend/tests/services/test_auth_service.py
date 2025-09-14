"""
Unit tests for AuthService
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from services.authservice.auth_service import (
    AuthService, AuthUser, AuthSession, 
    AuthenticationError, InvalidCredentialsError, 
    UserAlreadyExistsError, SessionExpiredError
)


@pytest.fixture
def mock_db_manager():
    """Mock database manager for testing"""
    return Mock()


@pytest.fixture
def auth_service(mock_db_manager):
    """Create AuthService instance with mock database"""
    return AuthService(mock_db_manager)


class TestAuthService:
    """Test suite for AuthService"""
    
    def test_init(self, auth_service):
        """Test AuthService initialization"""
        assert auth_service.session_lifetime_hours == 24
        assert auth_service.db is not None
        assert auth_service.pwd_context is not None
    
    def test_hash_password(self, auth_service):
        """Test password hashing"""
        password = "test_password"
        hashed = auth_service._hash_password(password)
        assert hashed != password
        assert auth_service._verify_password(password, hashed)
        assert not auth_service._verify_password("wrong_password", hashed)
    
    def test_register_user_success(self, auth_service, mock_db_manager):
        """Test successful user registration"""
        # Mock database response and _get_user_by_username
        mock_db_manager.execute_insert.return_value = 1
        auth_service._get_user_by_username = Mock(return_value=None)  # User doesn't exist
        
        user = auth_service.register_user("testuser", "password123")
        
        assert isinstance(user, AuthUser)
        assert user.username == "testuser"
        assert user.id == 1
        mock_db_manager.execute_insert.assert_called_once()
    
    def test_register_user_invalid_username(self, auth_service):
        """Test user registration with invalid username"""
        with pytest.raises(ValueError, match="Username must be at least 3 characters long"):
            auth_service.register_user("ab", "password123")
    
    def test_register_user_invalid_password(self, auth_service):
        """Test user registration with invalid password"""
        with pytest.raises(ValueError, match="Password must be at least 6 characters long"):
            auth_service.register_user("testuser", "123")
    
    def test_register_user_already_exists(self, auth_service, mock_db_manager):
        """Test user registration when user already exists"""
        # Mock that user already exists
        auth_service._get_user_by_username = Mock(return_value={"id": 1})
        
        with pytest.raises(UserAlreadyExistsError):
            auth_service.register_user("existinguser", "password123")
    
    def test_login_success(self, auth_service, mock_db_manager):
        """Test successful login"""
        # Mock user data
        user_data = {
            'id': 1,
            'username': 'testuser',
            'password_hash': auth_service._hash_password('password123'),
            'salt': '',
            'is_admin': False,
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'native_language': 'en',
            'target_language': 'de'
        }
        
        # Mock database responses
        auth_service._get_user_by_username = Mock(return_value=user_data)
        mock_db_manager.execute_insert.return_value = 1  # Session creation
        mock_db_manager.execute_update.return_value = 1  # Last login update
        
        session = auth_service.login("testuser", "password123")
        
        assert isinstance(session, AuthSession)
        assert session.user.username == "testuser"
        assert len(session.session_token) > 0
        # Verify session was inserted into database
        mock_db_manager.execute_insert.assert_called_once()
    
    def test_login_invalid_credentials(self, auth_service, mock_db_manager):
        """Test login with invalid credentials"""
        # Mock that user doesn't exist
        auth_service._get_user_by_username = Mock(return_value=None)
        
        with pytest.raises(InvalidCredentialsError):
            auth_service.login("nonexistent", "password123")
    
    def test_validate_session_success(self, auth_service, mock_db_manager):
        """Test successful session validation"""
        session_token = "test_token"
        expires_at = datetime.now() + timedelta(hours=1)
        
        # Mock database response for valid session
        session_data = {
            'session_token': session_token,
            'expires_at': expires_at.isoformat(),
            'last_used': datetime.now().isoformat(),
            'is_active': True,
            'id': 1,
            'username': 'testuser',
            'is_admin': False,
            'user_is_active': True,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'native_language': 'en',
            'target_language': 'de'
        }
        
        mock_db_manager.execute_query.return_value = [session_data]
        mock_db_manager.execute_update.return_value = 1  # Update last_used
        
        user = auth_service.validate_session(session_token)
        
        assert isinstance(user, AuthUser)
        assert user.username == "testuser"
        assert user.id == 1
    
    def test_validate_session_expired(self, auth_service, mock_db_manager):
        """Test session validation with expired session"""
        session_token = "expired_token"
        expired_at = datetime.now() - timedelta(hours=1)
        
        # Mock database response for expired session
        session_data = {
            'session_token': session_token,
            'expires_at': expired_at.isoformat(),
            'last_used': datetime.now().isoformat(),
            'is_active': True,
            'id': 1,
            'username': 'testuser',
            'is_admin': False,
            'user_is_active': True,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'native_language': 'en',
            'target_language': 'de'
        }
        
        mock_db_manager.execute_query.return_value = [session_data]
        mock_db_manager.execute_update.return_value = 1  # Deactivate session
        
        with pytest.raises(SessionExpiredError):
            auth_service.validate_session(session_token)
        
        # Verify session was deactivated in database
        mock_db_manager.execute_update.assert_called_once()
    
    def test_logout(self, auth_service, mock_db_manager):
        """Test user logout"""
        session_token = "test_token"
        
        # Mock successful logout (session found and deactivated)
        mock_db_manager.execute_update.return_value = 1
        result = auth_service.logout(session_token)
        assert result is True
        
        # Test logout with non-existent session
        mock_db_manager.execute_update.return_value = 0
        result = auth_service.logout("nonexistent_token")
        assert result is False
    
    def test_update_language_preferences(self, auth_service, mock_db_manager):
        """Test updating user language preferences"""
        mock_db_manager.execute_update.return_value = 1
        
        result = auth_service.update_language_preferences(1, "es", "fr")
        
        assert result is True
        mock_db_manager.execute_update.assert_called_once()
"""
Simple and clean authentication service for LangPlug
No complex dependencies, no fancy logging, just works
"""

import bcrypt
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from passlib.context import CryptContext

from database.database_manager import DatabaseManager
from services.repository.user_repository import UserRepository, User
from .models import (
    AuthUser, AuthSession, AuthenticationError, 
    InvalidCredentialsError, UserAlreadyExistsError, SessionExpiredError
)

class AuthService:
    """
    Simple authentication service with secure bcrypt password hashing
    Uses database-based session storage for scalability and persistence
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.user_repository = UserRepository(db_manager)
        self._sessions: Dict[str, AuthSession] = {}
        # Initialize password context with bcrypt
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against bcrypt hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def register_user(self, username: str, password: str) -> AuthUser:
        """Register a new user"""
        # Validate input
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        # Check if user exists
        existing_user = self._get_user_by_username(username)
        if existing_user:
            raise UserAlreadyExistsError(f"User '{username}' already exists")
        
        # Create user with hashed password (bcrypt includes salt internally)
        password_hash = self._hash_password(password)
        
        try:
            now = datetime.now().isoformat()
            user_id = self.db.execute_insert("""
                INSERT INTO users (username, password_hash, salt, is_admin, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, password_hash, "", False, True, now, now))  # Empty salt field for bcrypt
            
            return AuthUser(
                id=user_id,
                username=username,
                is_admin=False,
                is_active=True,
                created_at=now,
                native_language="en",
                target_language="de"
            )
            
        except Exception as e:
            raise AuthenticationError(f"Failed to register user: {e}")
    
    def login(self, username: str, password: str) -> AuthSession:
        """Login user and create session"""
        # Get user from database
        user_data = self._get_user_by_username(username)
        if not user_data:
            raise InvalidCredentialsError("Invalid username or password")
        
        # Check if user needs password migration (from SHA256 to bcrypt)
        # For legacy users with salt, assume they need migration
        needs_migration = bool(user_data.get('salt'))
        
        if needs_migration and user_data.get('salt'):
            # Old SHA256 verification for legacy users
            old_hash = hashlib.sha256(f"{password}{user_data['salt']}".encode()).hexdigest()
            if user_data['password_hash'] != old_hash:
                raise InvalidCredentialsError("Invalid username or password")
            
            # Migrate to bcrypt on successful login
            new_hash = self._hash_password(password)
            now = datetime.now().isoformat()
            self.db.execute_update("""
                UPDATE users 
                SET password_hash = ?, salt = '', updated_at = ?
                WHERE id = ?
            """, (new_hash, now, user_data['id']))
            
        else:
            # Verify password using bcrypt for new/migrated users
            if not self._verify_password(password, user_data['password_hash']):
                raise InvalidCredentialsError("Invalid username or password")
        
        # Create session token
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=self.session_lifetime_hours)
        
        # Store session in database
        try:
            now = datetime.now().isoformat()
            self.db.execute_insert("""
                INSERT INTO user_sessions (user_id, session_token, expires_at, created_at, last_used, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_data['id'], session_token, expires_at.isoformat(), now, now, True))
        except Exception as e:
            raise AuthenticationError(f"Failed to create session: {e}")
        
        # Update last login
        now = datetime.now().isoformat()
        self.db.execute_update("""
            UPDATE users SET last_login = ?, updated_at = ? WHERE id = ?
        """, (now, now, user_data['id']))
        
        # Create user object
        user = AuthUser(
            id=user_data['id'],
            username=user_data['username'],
            is_admin=bool(user_data.get('is_admin', False)),
            is_active=bool(user_data.get('is_active', True)),
            created_at=user_data.get('created_at', ''),
            last_login=now,
            native_language=user_data.get('native_language', 'en'),
            target_language=user_data.get('target_language', 'de')
        )
        
        return AuthSession(
            session_token=session_token,
            user=user,
            expires_at=expires_at,
            created_at=datetime.now()
        )
    
    def validate_session(self, session_token: str) -> AuthUser:
        """Validate session token and return user"""
        # Get session from database
        try:
            results = self.db.execute_query("""
                SELECT us.session_token, us.expires_at, us.last_used, us.is_active,
                       u.id, u.username, u.is_admin, u.is_active as user_is_active,
                       u.created_at, u.last_login, u.native_language, u.target_language
                FROM user_sessions us
                JOIN users u ON us.user_id = u.id
                WHERE us.session_token = ? AND us.is_active = 1
            """, (session_token,))
            
            if not results:
                raise SessionExpiredError("Invalid or expired session")
            
            session_data = results[0]
            
            # Check if session is expired
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                # Mark session as inactive
                self.db.execute_update("""
                    UPDATE user_sessions SET is_active = 0 WHERE session_token = ?
                """, (session_token,))
                raise SessionExpiredError("Session has expired")
            
            # Update last used timestamp
            now = datetime.now().isoformat()
            self.db.execute_update("""
                UPDATE user_sessions SET last_used = ? WHERE session_token = ?
            """, (now, session_token))
            
            return AuthUser(
                id=session_data['id'],
                username=session_data['username'],
                is_admin=bool(session_data.get('is_admin', False)),
                is_active=bool(session_data.get('user_is_active', True)),
                created_at=session_data.get('created_at', ''),
                last_login=session_data.get('last_login'),
                native_language=session_data.get('native_language', 'en'),
                target_language=session_data.get('target_language', 'de')
            )
        except SessionExpiredError:
            raise
        except Exception as e:
            raise AuthenticationError(f"Failed to validate session: {e}")
    
    def logout(self, session_token: str) -> bool:
        """Logout user by deactivating session"""
        try:
            # Mark session as inactive in database
            rows_affected = self.db.execute_update("""
                UPDATE user_sessions SET is_active = 0 WHERE session_token = ?
            """, (session_token,))
            
            return rows_affected > 0
        except Exception as e:
            raise AuthenticationError(f"Failed to logout: {e}")
    
    def update_language_preferences(self, user_id: int, native_language: str, target_language: str) -> bool:
        """Update user's language preferences"""
        try:
            now = datetime.now().isoformat()
            self.db.execute_update("""
                UPDATE users 
                SET native_language = ?, target_language = ?, updated_at = ?
                WHERE id = ?
            """, (native_language, target_language, now, user_id))
            
            return True
        except Exception as e:
            raise AuthenticationError(f"Failed to update language preferences: {e}")
    
    def _get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user from database by username"""
        results = self.db.execute_query("""
            SELECT id, username, password_hash, salt, is_admin, is_active, created_at, updated_at, last_login,
                   native_language, target_language
            FROM users WHERE username = ?
        """, (username,))
        
        return dict(results[0]) if results else None
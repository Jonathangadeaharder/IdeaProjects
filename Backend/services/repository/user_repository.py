"""
User Repository Implementation
Standardizes user data access patterns and removes direct database queries from services
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .base_repository import BaseRepository
from services.authservice.models import AuthUser

logger = logging.getLogger(__name__)


class User:
    """User domain model"""
    def __init__(self, id: Optional[int] = None, username: str = "", 
                 password_hash: str = "", email: str = "", 
                 native_language: str = "en", target_language: str = "de",
                 created_at: Optional[datetime] = None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.native_language = native_language
        self.target_language = target_language
        self.created_at = created_at or datetime.now()


class UserRepository(BaseRepository[User]):
    """Repository for User entity with standardized database access"""
    
    @property
    def table_name(self) -> str:
        return "users"
    
    def _row_to_model(self, row: Dict[str, Any]) -> User:
        """Convert database row to User model"""
        return User(
            id=row.get('id'),
            username=row.get('username', ''),
            password_hash=row.get('password_hash', ''),
            email=row.get('email', ''),
            native_language=row.get('native_language', 'en'),
            target_language=row.get('target_language', 'de'),
            created_at=datetime.fromisoformat(row['created_at']) if row.get('created_at') else datetime.now()
        )
    
    def _model_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert User model to dictionary for database operations"""
        return {
            'id': user.id,
            'username': user.username,
            'password_hash': user.password_hash,
            'email': user.email,
            'native_language': user.native_language,
            'target_language': user.target_language,
            'created_at': user.created_at.isoformat() if user.created_at else datetime.now().isoformat()
        }
    
    def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_model(dict(row))
                return None
        except Exception as e:
            self.logger.error(f"Error finding user by username {username}: {e}")
            raise
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_model(dict(row))
                return None
        except Exception as e:
            self.logger.error(f"Error finding user by email {email}: {e}")
            raise
    
    def username_exists(self, username: str, exclude_id: Optional[int] = None) -> bool:
        """Check if username already exists (optionally excluding a specific user ID)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if exclude_id:
                    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ? AND id != ?", (username, exclude_id))
                else:
                    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
                
                return cursor.fetchone()[0] > 0
        except Exception as e:
            self.logger.error(f"Error checking username exists {username}: {e}")
            raise
    
    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Check if email already exists (optionally excluding a specific user ID)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if exclude_id:
                    cursor.execute("SELECT COUNT(*) FROM users WHERE email = ? AND id != ?", (email, exclude_id))
                else:
                    cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
                
                return cursor.fetchone()[0] > 0
        except Exception as e:
            self.logger.error(f"Error checking email exists {email}: {e}")
            raise
    
    def update_language_preference(self, user_id: int, native_language: str, target_language: str) -> bool:
        """Update user language preferences"""
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET native_language = ?, target_language = ? WHERE id = ?",
                    (native_language, target_language, user_id)
                )
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error updating language preferences for user {user_id}: {e}")
            raise
    
    def update_password(self, user_id: int, password_hash: str) -> bool:
        """Update user password hash"""
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (password_hash, user_id)
                )
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error updating password for user {user_id}: {e}")
            raise
    
    def to_auth_user(self, user: User) -> AuthUser:
        """Convert User domain model to AuthUser for compatibility"""
        return AuthUser(id=user.id, username=user.username)
    
    def from_auth_user_data(self, user_id: int) -> Optional[User]:
        """Get full User from AuthUser ID for backward compatibility"""
        return self.find_by_id(user_id)

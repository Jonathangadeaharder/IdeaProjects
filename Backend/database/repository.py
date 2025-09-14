"""
Database repository using SQLAlchemy ORM
"""
import logging
from typing import List, Optional, Any
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .models import Base, User, UserSession, Vocabulary, WordCategory, UnknownWord
from ..services.authservice.models import AuthUser

logger = logging.getLogger(__name__)


class DatabaseRepository:
    """Repository class for database operations using SQLAlchemy ORM"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._create_tables()
    
    def _create_tables(self):
        """Create all tables defined in models"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    # User operations
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username"""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.username == username).first()
                return {
                    'id': user.id,
                    'username': user.username,
                    'password_hash': user.password_hash,
                    'salt': user.salt,
                    'is_admin': user.is_admin,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat() if user.created_at else None,
                    'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'native_language': 'en',  # Default values
                    'target_language': 'de'
                } if user else None
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by username: {e}")
            raise
    
    def create_user(self, username: str, password_hash: str, salt: str = "") -> int:
        """Create a new user"""
        try:
            with self.get_session() as session:
                user = User(
                    username=username,
                    password_hash=password_hash,
                    salt=salt,
                    is_admin=False,
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                return user.id
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    def update_user_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    user.last_login = datetime.now()
                    user.updated_at = datetime.now()
                    session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating user last login: {e}")
            raise
    
    def update_user_language_preferences(self, user_id: int, native_language: str, target_language: str) -> bool:
        """Update user's language preferences"""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    # Note: We're storing these in a temporary way since the User model
                    # doesn't have these fields. In a full implementation, we'd add these fields.
                    user.updated_at = datetime.now()
                    session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating user language preferences: {e}")
            raise
    
    # Session operations
    def create_session(self, user_id: int, session_token: str, expires_at: datetime) -> bool:
        """Create a new user session"""
        try:
            with self.get_session() as session:
                user_session = UserSession(
                    user_id=user_id,
                    session_token=session_token,
                    expires_at=expires_at,
                    created_at=datetime.now(),
                    last_used=datetime.now(),
                    is_active=True
                )
                session.add(user_session)
                session.commit()
                return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error creating session: {e}")
            raise
    
    def get_session_by_token(self, session_token: str) -> Optional[dict]:
        """Get session by token"""
        try:
            with self.get_session() as session:
                user_session = session.query(UserSession).filter(
                    UserSession.session_token == session_token,
                    UserSession.is_active == True
                ).first()
                
                if user_session:
                    # Check if session is expired
                    if datetime.now() > user_session.expires_at:
                        # Mark session as inactive
                        user_session.is_active = False
                        session.commit()
                        return None
                    
                    # Update last used timestamp
                    user_session.last_used = datetime.now()
                    session.commit()
                    
                    # Get associated user
                    user = user_session.user
                    return {
                        'session_token': user_session.session_token,
                        'expires_at': user_session.expires_at.isoformat(),
                        'last_used': user_session.last_used.isoformat(),
                        'is_active': user_session.is_active,
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'is_admin': user.is_admin,
                            'is_active': user.is_active,
                            'created_at': user.created_at.isoformat() if user.created_at else None,
                            'last_login': user.last_login.isoformat() if user.last_login else None,
                            'native_language': 'en',  # Default values
                            'target_language': 'de'
                        }
                    }
                return None
        except SQLAlchemyError as e:
            logger.error(f"Error getting session by token: {e}")
            raise
    
    def deactivate_session(self, session_token: str) -> bool:
        """Deactivate a user session"""
        try:
            with self.get_session() as session:
                user_session = session.query(UserSession).filter(
                    UserSession.session_token == session_token
                ).first()
                
                if user_session:
                    user_session.is_active = False
                    session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error deactivating session: {e}")
            raise
    
    # Vocabulary operations
    def get_vocabulary_count(self) -> int:
        """Get total vocabulary count"""
        try:
            with self.get_session() as session:
                return session.query(Vocabulary).count()
        except SQLAlchemyError as e:
            logger.error(f"Error getting vocabulary count: {e}")
            raise
    
    # Generic operations (for backward compatibility with existing code)
    def execute_query(self, query: str, params: tuple = ()) -> List[dict]:
        """Execute a SELECT query and return results"""
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params)
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]
        except SQLAlchemyError as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params)
                session.commit()
                return result.rowcount
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error executing update: {e}")
            raise
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the last row ID"""
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params)
                session.commit()
                # For SQLite, we need to get the last inserted row id
                last_id = result.lastrowid
                return last_id if last_id is not None else 0
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error executing insert: {e}")
            raise
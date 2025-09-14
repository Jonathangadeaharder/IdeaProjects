"""Authentication models and data classes"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AuthUser:
    """Represents an authenticated user"""
    id: int
    username: str
    is_admin: bool = False
    is_active: bool = True
    created_at: str = ""
    last_login: Optional[str] = None
    native_language: str = "en"
    target_language: str = "de"


@dataclass
class AuthSession:
    """Represents a user session"""
    session_token: str
    user: AuthUser
    expires_at: datetime
    created_at: datetime


class AuthenticationError(Exception):
    """Base exception for authentication errors"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid"""
    pass


class UserAlreadyExistsError(AuthenticationError):
    """Raised when trying to register a user that already exists"""
    pass


class SessionExpiredError(AuthenticationError):
    """Raised when a session token has expired"""
    pass
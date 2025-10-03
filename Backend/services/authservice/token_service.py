"""
JWT Token Service with Security Hardening
Implements access tokens (short-lived) and refresh tokens (long-lived)
"""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from core.config import settings
from core.exceptions import AuthenticationError


class TokenService:
    """
    JWT token management with security hardening

    Features:
    - Short-lived access tokens (1 hour)
    - Long-lived refresh tokens (30 days)
    - Token type validation
    - Secure token generation and validation
    """

    # Token configuration
    ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour (reduced from 24 hours)
    REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days
    ALGORITHM = "HS256"

    @classmethod
    def create_access_token(cls, user_id: int, additional_claims: dict | None = None) -> str:
        """
        Create short-lived access token

        Args:
            user_id: User ID to encode in token
            additional_claims: Optional additional claims to include

        Returns:
            Encoded JWT access token
        """
        expires = datetime.now(UTC) + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": str(user_id),
            "exp": expires,
            "iat": datetime.now(UTC),
            "type": "access",
        }

        # Add any additional claims
        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(payload, settings.secret_key, algorithm=cls.ALGORITHM)

    @classmethod
    def create_refresh_token(cls, user_id: int) -> str:
        """
        Create long-lived refresh token

        Args:
            user_id: User ID to encode in token

        Returns:
            Encoded JWT refresh token
        """
        expires = datetime.now(UTC) + timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)

        payload = {
            "sub": str(user_id),
            "exp": expires,
            "iat": datetime.now(UTC),
            "type": "refresh",
        }

        return jwt.encode(payload, settings.secret_key, algorithm=cls.ALGORITHM)

    @classmethod
    def create_token_pair(cls, user_id: int) -> dict[str, str]:
        """
        Create both access and refresh tokens

        Args:
            user_id: User ID

        Returns:
            Dictionary with access_token and refresh_token
        """
        return {
            "access_token": cls.create_access_token(user_id),
            "refresh_token": cls.create_refresh_token(user_id),
            "token_type": "bearer",
            "expires_in": cls.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
        }

    @classmethod
    def decode_token(cls, token: str, expected_type: str | None = None) -> dict:
        """
        Decode and validate JWT token

        Args:
            token: JWT token to decode
            expected_type: Expected token type ("access" or "refresh")

        Returns:
            Decoded token payload

        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[cls.ALGORITHM])

            # Validate token type if specified
            if expected_type and payload.get("type") != expected_type:
                raise AuthenticationError(
                    f"Invalid token type. Expected '{expected_type}', got '{payload.get('type')}'"
                )

            return payload

        except JWTError as e:
            raise AuthenticationError(f"Invalid token: {e}") from e

    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> str:
        """
        Exchange refresh token for new access token

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token

        Raises:
            AuthenticationError: If refresh token is invalid
        """
        # Validate refresh token
        payload = cls.decode_token(refresh_token, expected_type="refresh")

        # Get user ID from payload
        user_id = int(payload.get("sub"))

        # Create new access token
        return cls.create_access_token(user_id)

    @classmethod
    def get_user_id_from_token(cls, token: str) -> int:
        """
        Extract user ID from token

        Args:
            token: JWT token (access or refresh)

        Returns:
            User ID

        Raises:
            AuthenticationError: If token is invalid
        """
        payload = cls.decode_token(token)
        return int(payload.get("sub"))

    @classmethod
    def verify_access_token(cls, token: str) -> int:
        """
        Verify access token and return user ID

        Args:
            token: Access token to verify

        Returns:
            User ID if valid

        Raises:
            AuthenticationError: If token is invalid or wrong type
        """
        payload = cls.decode_token(token, expected_type="access")
        return int(payload.get("sub"))

    @classmethod
    def is_token_expired(cls, token: str) -> bool:
        """
        Check if token is expired

        Args:
            token: JWT token to check

        Returns:
            True if expired, False otherwise
        """
        try:
            payload = cls.decode_token(token)
            exp = payload.get("exp")
            if exp:
                return datetime.fromtimestamp(exp, tz=UTC) < datetime.now(UTC)
            return True
        except AuthenticationError:
            return True

    @classmethod
    def get_token_expiry(cls, token: str) -> datetime | None:
        """
        Get token expiration time

        Args:
            token: JWT token

        Returns:
            Expiration datetime or None if invalid
        """
        try:
            payload = cls.decode_token(token)
            exp = payload.get("exp")
            if exp:
                return datetime.fromtimestamp(exp, tz=UTC)
            return None
        except AuthenticationError:
            return None


# Convenience functions for common operations


def create_tokens_for_user(user_id: int) -> dict[str, str]:
    """
    Create access and refresh tokens for user

    Args:
        user_id: User ID

    Returns:
        Dictionary with token pair
    """
    return TokenService.create_token_pair(user_id)


def verify_access_token(token: str) -> int:
    """
    Verify access token and get user ID

    Args:
        token: Access token

    Returns:
        User ID

    Raises:
        AuthenticationError: If invalid
    """
    return TokenService.verify_access_token(token)


def refresh_token(refresh_token: str) -> str:
    """
    Get new access token from refresh token

    Args:
        refresh_token: Refresh token

    Returns:
        New access token

    Raises:
        AuthenticationError: If invalid
    """
    return TokenService.refresh_access_token(refresh_token)

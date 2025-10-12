"""
Unit tests for TokenService

Tests JWT token generation, validation, refresh, and expiration handling
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

# Python 3.10 compatibility: Use timezone.utc instead of UTC constant
UTC = UTC

import pytest
from jose import jwt

from core.config import settings
from core.exceptions import AuthenticationError
from services.authservice.token_service import TokenService


class TestTokenCreation:
    """Test access and refresh token creation"""

    def test_create_access_token_returns_valid_jwt(self):
        """Access token should be a valid JWT string"""
        token = TokenService.create_access_token(user_id=123)

        assert isinstance(token, str)
        assert len(token) > 0
        # JWT tokens have 3 parts separated by dots
        assert token.count(".") == 2

    def test_create_access_token_encodes_user_id(self):
        """Access token should encode user ID in 'sub' claim"""
        user_id = 456
        token = TokenService.create_access_token(user_id=user_id)

        # Decode without verification to inspect payload
        payload = jwt.decode(token, settings.secret_key, algorithms=[TokenService.ALGORITHM])
        assert payload["sub"] == str(user_id)

    def test_create_access_token_has_correct_type(self):
        """Access token should have type='access'"""
        token = TokenService.create_access_token(user_id=123)

        payload = jwt.decode(token, settings.secret_key, algorithms=[TokenService.ALGORITHM])
        assert payload["type"] == "access"

    def test_create_access_token_has_expiration(self):
        """Access token should have expiration claim"""
        token = TokenService.create_access_token(user_id=123)

        payload = jwt.decode(token, settings.secret_key, algorithms=[TokenService.ALGORITHM])
        assert "exp" in payload
        assert "iat" in payload  # Issued at

        # Expiration should be in the future
        exp_time = datetime.fromtimestamp(payload["exp"], tz=UTC)
        now = datetime.now(UTC)
        assert exp_time > now

    def test_create_access_token_expiration_duration(self):
        """Access token should expire in configured time (60 minutes)"""
        token = TokenService.create_access_token(user_id=123)

        payload = jwt.decode(token, settings.secret_key, algorithms=[TokenService.ALGORITHM])
        exp_time = datetime.fromtimestamp(payload["exp"], tz=UTC)
        iat_time = datetime.fromtimestamp(payload["iat"], tz=UTC)

        # Calculate duration (should be approximately 60 minutes)
        duration_minutes = (exp_time - iat_time).total_seconds() / 60
        assert 59 <= duration_minutes <= 61  # Allow 1 minute tolerance

    def test_create_access_token_with_additional_claims(self):
        """Access token should include additional claims if provided"""
        additional_claims = {"role": "admin", "permissions": ["read", "write"]}
        token = TokenService.create_access_token(user_id=123, additional_claims=additional_claims)

        payload = jwt.decode(token, settings.secret_key, algorithms=[TokenService.ALGORITHM])
        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write"]

    def test_create_refresh_token_returns_valid_jwt(self):
        """Refresh token should be a valid JWT string"""
        token = TokenService.create_refresh_token(user_id=789)

        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count(".") == 2

    def test_create_refresh_token_has_correct_type(self):
        """Refresh token should have type='refresh'"""
        token = TokenService.create_refresh_token(user_id=123)

        payload = jwt.decode(token, settings.secret_key, algorithms=[TokenService.ALGORITHM])
        assert payload["type"] == "refresh"

    def test_create_refresh_token_longer_expiration(self):
        """Refresh token should have longer expiration than access token (30 days)"""
        token = TokenService.create_refresh_token(user_id=123)

        payload = jwt.decode(token, settings.secret_key, algorithms=[TokenService.ALGORITHM])
        exp_time = datetime.fromtimestamp(payload["exp"], tz=UTC)
        iat_time = datetime.fromtimestamp(payload["iat"], tz=UTC)

        # Calculate duration in days
        duration_days = (exp_time - iat_time).total_seconds() / (60 * 60 * 24)
        assert 29 <= duration_days <= 31  # Allow 1 day tolerance

    def test_create_token_pair_returns_both_tokens(self):
        """Token pair should contain access and refresh tokens"""
        result = TokenService.create_token_pair(user_id=123)

        assert "access_token" in result
        assert "refresh_token" in result
        assert "token_type" in result
        assert "expires_in" in result

        assert result["token_type"] == "bearer"
        assert isinstance(result["access_token"], str)
        assert isinstance(result["refresh_token"], str)

    def test_create_token_pair_different_tokens(self):
        """Access and refresh tokens should be different"""
        result = TokenService.create_token_pair(user_id=123)

        assert result["access_token"] != result["refresh_token"]


class TestTokenDecoding:
    """Test token decoding and validation"""

    def test_decode_token_valid_access_token(self):
        """Decoding valid access token should return payload"""
        token = TokenService.create_access_token(user_id=123)
        payload = TokenService.decode_token(token)

        assert payload["sub"] == "123"
        assert payload["type"] == "access"

    def test_decode_token_with_type_validation(self):
        """Decoding should validate token type when specified"""
        access_token = TokenService.create_access_token(user_id=123)
        payload = TokenService.decode_token(access_token, expected_type="access")

        assert payload["type"] == "access"

    def test_decode_token_wrong_type_raises_error(self):
        """Decoding with wrong expected type should raise error"""
        access_token = TokenService.create_access_token(user_id=123)

        with pytest.raises(AuthenticationError, match="Invalid token type"):
            TokenService.decode_token(access_token, expected_type="refresh")

    def test_decode_token_invalid_signature_raises_error(self):
        """Decoding token with invalid signature should raise error"""
        # Create token with different secret
        fake_token = jwt.encode({"sub": "123"}, "wrong_secret", algorithm="HS256")

        with pytest.raises(AuthenticationError, match="Invalid token"):
            TokenService.decode_token(fake_token)

    def test_decode_token_malformed_token_raises_error(self):
        """Decoding malformed token should raise error"""
        malformed_token = "not.a.valid.jwt"

        with pytest.raises(AuthenticationError, match="Invalid token"):
            TokenService.decode_token(malformed_token)

    def test_decode_token_expired_token_raises_error(self):
        """Decoding expired token should raise error"""
        # Create token that expired 1 hour ago
        expired_payload = {
            "sub": "123",
            "exp": datetime.now(UTC) - timedelta(hours=1),
            "iat": datetime.now(UTC) - timedelta(hours=2),
            "type": "access",
        }
        expired_token = jwt.encode(expired_payload, settings.secret_key, algorithm=TokenService.ALGORITHM)

        with pytest.raises(AuthenticationError, match="Invalid token"):
            TokenService.decode_token(expired_token)


class TestTokenRefresh:
    """Test refresh token functionality"""

    def test_refresh_access_token_returns_new_token(self):
        """Refreshing should return a new valid access token"""
        refresh_token = TokenService.create_refresh_token(user_id=123)
        new_access_token = TokenService.refresh_access_token(refresh_token)

        assert isinstance(new_access_token, str)
        assert new_access_token.count(".") == 2

        # Verify it's an access token
        payload = TokenService.decode_token(new_access_token, expected_type="access")
        assert payload["type"] == "access"
        assert payload["sub"] == "123"

    def test_refresh_access_token_preserves_user_id(self):
        """Refreshed token should have same user ID"""
        user_id = 456
        refresh_token = TokenService.create_refresh_token(user_id=user_id)
        new_access_token = TokenService.refresh_access_token(refresh_token)

        payload = TokenService.decode_token(new_access_token)
        assert payload["sub"] == str(user_id)

    def test_refresh_access_token_with_access_token_fails(self):
        """Using access token to refresh should fail"""
        access_token = TokenService.create_access_token(user_id=123)

        with pytest.raises(AuthenticationError, match="Invalid token type"):
            TokenService.refresh_access_token(access_token)

    def test_refresh_access_token_with_invalid_token_fails(self):
        """Using invalid token to refresh should fail"""
        with pytest.raises(AuthenticationError):
            TokenService.refresh_access_token("invalid.token.here")


class TestTokenUtilities:
    """Test token utility methods"""

    def test_get_user_id_from_token(self):
        """Should extract user ID from valid token"""
        user_id = 789
        token = TokenService.create_access_token(user_id=user_id)

        extracted_id = TokenService.get_user_id_from_token(token)
        assert extracted_id == user_id

    def test_get_user_id_from_refresh_token(self):
        """Should extract user ID from refresh token too"""
        user_id = 321
        token = TokenService.create_refresh_token(user_id=user_id)

        extracted_id = TokenService.get_user_id_from_token(token)
        assert extracted_id == user_id

    def test_verify_access_token_valid(self):
        """Verifying valid access token should return user ID"""
        user_id = 555
        token = TokenService.create_access_token(user_id=user_id)

        verified_id = TokenService.verify_access_token(token)
        assert verified_id == user_id

    def test_verify_access_token_with_refresh_token_fails(self):
        """Verifying refresh token as access token should fail"""
        token = TokenService.create_refresh_token(user_id=123)

        with pytest.raises(AuthenticationError, match="Invalid token type"):
            TokenService.verify_access_token(token)

    def test_is_token_expired_not_expired(self):
        """Fresh token should not be expired"""
        token = TokenService.create_access_token(user_id=123)

        assert TokenService.is_token_expired(token) is False

    def test_is_token_expired_expired_token(self):
        """Expired token should be detected"""
        # Create expired token
        expired_payload = {
            "sub": "123",
            "exp": datetime.now(UTC) - timedelta(hours=1),
            "type": "access",
        }
        expired_token = jwt.encode(expired_payload, settings.secret_key, algorithm=TokenService.ALGORITHM)

        assert TokenService.is_token_expired(expired_token) is True

    def test_is_token_expired_invalid_token(self):
        """Invalid token should be considered expired"""
        assert TokenService.is_token_expired("invalid.token") is True

    def test_get_token_expiry_valid_token(self):
        """Should return expiry datetime for valid token"""
        token = TokenService.create_access_token(user_id=123)
        expiry = TokenService.get_token_expiry(token)

        assert isinstance(expiry, datetime)
        assert expiry > datetime.now(UTC)

    def test_get_token_expiry_invalid_token(self):
        """Should return None for invalid token"""
        expiry = TokenService.get_token_expiry("invalid.token")
        assert expiry is None


class TestSecurityConsiderations:
    """Test security-related edge cases"""

    def test_tokens_are_unique_for_same_user(self):
        """Multiple tokens for same user should be unique (different iat)"""
        from datetime import datetime

        user_id = 123

        # Create first token at time T
        with patch("services.authservice.token_service.datetime") as mock_dt:
            time1 = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
            mock_dt.now.return_value = time1
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
            token1 = TokenService.create_access_token(user_id=user_id)

        # Create second token at time T+1
        with patch("services.authservice.token_service.datetime") as mock_dt:
            time2 = datetime(2025, 1, 1, 12, 0, 1, tzinfo=UTC)
            mock_dt.now.return_value = time2
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
            token2 = TokenService.create_access_token(user_id=user_id)

        assert token1 != token2

    def test_access_token_cannot_be_used_as_refresh(self):
        """Access token should not be accepted for refresh operation"""
        access_token = TokenService.create_access_token(user_id=123)

        with pytest.raises(AuthenticationError):
            TokenService.refresh_access_token(access_token)

    def test_refresh_token_cannot_be_used_for_access(self):
        """Refresh token should not be accepted for access verification"""
        refresh_token = TokenService.create_refresh_token(user_id=123)

        with pytest.raises(AuthenticationError):
            TokenService.verify_access_token(refresh_token)

    def test_token_without_type_field_fails_validation(self):
        """Token without type field should fail type validation"""
        # Create token without type field
        payload = {
            "sub": "123",
            "exp": datetime.now(UTC) + timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.secret_key, algorithm=TokenService.ALGORITHM)

        # Should fail when type is expected
        with pytest.raises(AuthenticationError, match="Invalid token type"):
            TokenService.decode_token(token, expected_type="access")


class TestConvenienceFunctions:
    """Test module-level convenience functions"""

    def test_create_tokens_for_user(self):
        """Convenience function should create token pair"""
        from services.authservice.token_service import create_tokens_for_user

        result = create_tokens_for_user(123)

        assert "access_token" in result
        assert "refresh_token" in result

    def test_verify_access_token_convenience(self):
        """Convenience function should verify token"""
        from services.authservice.token_service import verify_access_token

        token = TokenService.create_access_token(user_id=456)
        user_id = verify_access_token(token)

        assert user_id == 456

    def test_refresh_token_convenience(self):
        """Convenience function should refresh token"""
        from services.authservice.token_service import refresh_token

        refresh_tok = TokenService.create_refresh_token(user_id=789)
        new_access = refresh_token(refresh_tok)

        assert isinstance(new_access, str)
        payload = TokenService.decode_token(new_access)
        assert payload["sub"] == "789"

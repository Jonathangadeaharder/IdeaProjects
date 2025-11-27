"""Tests for token blacklist service."""

from datetime import UTC, datetime, timedelta

UTC = UTC

import pytest

from core.auth.token_blacklist import TokenBlacklist


class TestTokenBlacklistInitialization:
    """Test TokenBlacklist initialization."""

    def test_initialization(self):
        """Test initialization of in-memory blacklist."""
        blacklist = TokenBlacklist()
        assert isinstance(blacklist._blacklist, dict)
        assert len(blacklist._blacklist) == 0


class TestTokenBlacklistOperations:
    """Test token blacklist operations."""

    @pytest.fixture
    def blacklist(self):
        """Create blacklist instance."""
        return TokenBlacklist()

    @pytest.mark.asyncio
    async def test_add_token(self, blacklist):
        """Test adding token to blacklist."""
        token = "test_token_12345"
        expires_at = datetime.now(UTC) + timedelta(hours=1)

        result = await blacklist.add_token(token, expires_at)

        assert result is True
        assert token in blacklist._blacklist
        assert blacklist._blacklist[token] == expires_at

    @pytest.mark.asyncio
    async def test_add_token_default_expiry(self, blacklist):
        """Test adding token with default expiry."""
        token = "test_token_12345"

        result = await blacklist.add_token(token)

        assert result is True
        assert token in blacklist._blacklist
        expiry = blacklist._blacklist[token]
        now = datetime.now(UTC)
        # Check that expiry is within 24 hours (allowing for day boundary issues)
        time_diff = expiry - now
        assert time_diff.total_seconds() > 23 * 3600  # More than 23 hours
        assert time_diff.total_seconds() < 24 * 3600 + 60  # Less than 24 hours + 1 minute buffer

    @pytest.mark.asyncio
    async def test_is_blacklisted(self, blacklist):
        """Test checking if token is blacklisted."""
        token = "test_token_12345"
        expires_at = datetime.now(UTC) + timedelta(hours=1)

        result = await blacklist.is_blacklisted(token)
        assert result is False

        await blacklist.add_token(token, expires_at)

        result = await blacklist.is_blacklisted(token)
        assert result is True

    @pytest.mark.asyncio
    async def test_is_blacklisted_expired_token(self, blacklist):
        """Test blacklisted token that has expired."""
        token = "test_token_12345"
        expires_at = datetime.now(UTC) - timedelta(hours=1)

        await blacklist.add_token(token, expires_at)

        result = await blacklist.is_blacklisted(token)
        assert result is False

        assert token not in blacklist._blacklist

    @pytest.mark.asyncio
    async def test_remove_token(self, blacklist):
        """Test removing token from blacklist."""
        token = "test_token_12345"
        expires_at = datetime.now(UTC) + timedelta(hours=1)

        await blacklist.add_token(token, expires_at)
        assert token in blacklist._blacklist

        result = await blacklist.remove_token(token)
        assert result is True
        assert token not in blacklist._blacklist

    @pytest.mark.asyncio
    async def test_remove_nonexistent_token(self, blacklist):
        """Test removing token that doesn't exist."""
        token = "nonexistent_token"

        result = await blacklist.remove_token(token)
        assert result is False

    @pytest.mark.asyncio
    async def test_cleanup_expired_tokens(self, blacklist):
        """Test cleanup of expired tokens."""
        expired_token = "expired_token"
        valid_token = "valid_token"

        await blacklist.add_token(expired_token, datetime.now(UTC) - timedelta(hours=1))
        await blacklist.add_token(valid_token, datetime.now(UTC) + timedelta(hours=1))

        result = await blacklist.cleanup_expired()

        assert result is None
        assert expired_token not in blacklist._blacklist
        assert valid_token in blacklist._blacklist


class TestTokenBlacklistEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def blacklist(self):
        """Create blacklist instance."""
        return TokenBlacklist()

    @pytest.mark.asyncio
    async def test_add_empty_token(self, blacklist):
        """Test adding empty token."""
        result = await blacklist.add_token("")
        assert result is False

    @pytest.mark.asyncio
    async def test_add_none_token(self, blacklist):
        """Test adding None token."""
        result = await blacklist.add_token(None)
        assert result is False

    @pytest.mark.asyncio
    async def test_is_blacklisted_empty_token(self, blacklist):
        """Test checking empty token."""
        result = await blacklist.is_blacklisted("")
        assert result is False

    @pytest.mark.asyncio
    async def test_is_blacklisted_none_token(self, blacklist):
        """Test checking None token."""
        result = await blacklist.is_blacklisted(None)
        assert result is False

    @pytest.mark.asyncio
    async def test_multiple_cleanup_calls(self, blacklist):
        """Test multiple cleanup operations."""
        token1 = "expired1"
        token2 = "expired2"

        await blacklist.add_token(token1, datetime.now(UTC) - timedelta(hours=1))
        await blacklist.add_token(token2, datetime.now(UTC) - timedelta(hours=2))

        result1 = await blacklist.cleanup_expired()
        result2 = await blacklist.cleanup_expired()

        assert result1 is None
        assert result2 is None
        assert len(blacklist._blacklist) == 0

    @pytest.mark.asyncio
    async def test_cleanup_with_no_expired_tokens(self, blacklist):
        """Test cleanup when no tokens are expired."""
        token = "valid_token"
        await blacklist.add_token(token, datetime.now(UTC) + timedelta(hours=1))

        result = await blacklist.cleanup_expired()

        assert result is None
        assert token in blacklist._blacklist

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, blacklist):
        """Test concurrent token operations."""
        import asyncio

        for i in range(5):
            await blacklist.add_token(f"token_{i}", datetime.now(UTC) + timedelta(hours=1))

        check_tasks = [asyncio.create_task(blacklist.is_blacklisted(f"token_{i}")) for i in range(5)]

        results = await asyncio.gather(*check_tasks)

        assert all(results)

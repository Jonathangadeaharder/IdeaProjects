"""
Shared fixtures for unit tests

Provides reusable mocks and fixtures for common testing patterns.
"""

from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_transaction_context():
    """
    Create properly configured AsyncMock for transaction context.

    Returns an async context manager mock that can be used with:
        async with session.begin_nested()
    """
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=None)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    return mock_context


@pytest.fixture
def mock_db_session(mock_transaction_context):
    """
    Create mock database session with transaction support.

    Provides proper AsyncMock setup for:
    - begin_nested() - returns async context manager
    - commit() - async operation
    - rollback() - async operation
    - flush() - async operation (used by @transactional)
    - execute() - async operation
    - add() - sync operation
    - refresh() - async operation

    Usage:
        def test_my_function(mock_db_session):
            result = await my_service.process(mock_db_session, data)
            mock_db_session.flush.assert_called()
    """
    mock_session = Mock(spec=AsyncSession)

    # Transaction operations (async context manager)
    mock_session.begin_nested = Mock(return_value=mock_transaction_context)

    # Async operations
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.flush = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.close = AsyncMock()

    # Sync operations
    mock_session.add = Mock()
    mock_session.add_all = Mock()
    mock_session.delete = Mock()

    return mock_session

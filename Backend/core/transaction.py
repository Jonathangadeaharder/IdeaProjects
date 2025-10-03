"""
Transaction management utilities for SQLAlchemy async sessions

Provides decorators and context managers for ensuring database operations
are atomic and properly handle rollback on errors.
"""

import functools
import logging
from collections.abc import Callable

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def transactional(func: Callable):
    """
    Decorator to wrap a function in a database transaction.

    Ensures that all database operations within the function are atomic:
    - Commits if the function completes successfully
    - Rolls back if an exception occurs

    Usage:
        @transactional
        async def process_data(session: AsyncSession, data):
            # Multiple DB operations here
            await repo.create(data)
            await repo.update(data.id, {"status": "processed"})
            # All committed together or all rolled back

    Args:
        func: Async function that takes an AsyncSession parameter

    Returns:
        Wrapped function with transaction management
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Find the session parameter
        session = None

        # Check if session is in args
        for arg in args:
            if isinstance(arg, AsyncSession):
                session = arg
                break

        # Check if session is in kwargs
        if session is None:
            for value in kwargs.values():
                if isinstance(value, AsyncSession):
                    session = value
                    break

        # If no session found, call function normally (for services without DB)
        if session is None:
            logger.warning(f"No AsyncSession found in {func.__name__}, skipping transaction management")
            return await func(*args, **kwargs)

        # Execute within transaction
        try:
            async with session.begin_nested():  # Use SAVEPOINT for nested transactions
                result = await func(*args, **kwargs)
                # Commit happens automatically on successful exit
                return result
        except Exception as e:
            logger.error(f"Transaction rolled back in {func.__name__}: {e}")
            # Rollback happens automatically on exception
            raise

    return wrapper


class TransactionContext:
    """
    Context manager for explicit transaction control.

    Usage:
        async with TransactionContext(session) as tx:
            await repo.create(data)
            await repo.update(data.id, {"status": "processed"})
            # Commits on successful exit, rolls back on exception
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.transaction = None

    async def __aenter__(self):
        """Begin transaction"""
        self.transaction = await self.session.begin_nested()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Commit or rollback based on exception"""
        if exc_type is None:
            # Success - commit
            await self.transaction.commit()
        else:
            # Exception - rollback
            await self.transaction.rollback()
            logger.error(f"Transaction rolled back: {exc_val}")
        return False  # Don't suppress exception


__all__ = ["transactional", "TransactionContext"]

"""
Service factory for dependency injection compatibility
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from services.authservice.auth_service import AuthService


def get_auth_service(
    db_session: AsyncSession = Depends(get_async_session)
) -> AuthService:
    """FastAPI dependency to create AuthService with injected database session"""
    return AuthService(db_session)


# Service factories for other services can be added here as needed
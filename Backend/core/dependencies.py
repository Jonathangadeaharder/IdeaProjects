"""Simplified dependency injection for FastAPI using native Depends system"""
import logging
from typing import Optional, Annotated
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import settings
from database.unified_database_manager import UnifiedDatabaseManager as DatabaseManager
from services.authservice.auth_service import AuthService, SessionExpiredError
from services.authservice.models import AuthUser
from services.dataservice.authenticated_user_vocabulary_service import AuthenticatedUserVocabularyService
from services.filterservice.direct_subtitle_processor import DirectSubtitleProcessor
from services.transcriptionservice.factory import get_transcription_service as _get_transcription_service
from services.transcriptionservice.interface import ITranscriptionService
# Removed unused filter chain imports - using DirectSubtitleProcessor instead

security = HTTPBearer()
logger = logging.getLogger(__name__)


@lru_cache()
def get_database_manager() -> DatabaseManager:
    """Get database manager instance (singleton)"""
    logger.info("Creating database manager...")
    return DatabaseManager()


@lru_cache()
def get_auth_service() -> AuthService:
    """Get authentication service instance (singleton)"""
    logger.info("Creating auth service...")
    db_manager = get_database_manager()
    return AuthService(db_manager)


@lru_cache()
def get_vocabulary_service() -> AuthenticatedUserVocabularyService:
    """Get vocabulary service instance (singleton)"""
    db_manager = get_database_manager()
    auth_service = get_auth_service()
    return AuthenticatedUserVocabularyService(db_manager, auth_service)


@lru_cache()
def get_subtitle_processor() -> DirectSubtitleProcessor:
    """Get subtitle processor instance (singleton)"""
    db_manager = get_database_manager()
    return DirectSubtitleProcessor(db_manager)


@lru_cache()
def get_transcription_service() -> Optional[ITranscriptionService]:
    """Get transcription service instance (singleton)"""
    try:
        return _get_transcription_service()
    except Exception as e:
        logger.error(f"Failed to create transcription service: {e}")
        return None


# Removed unused filter chain functions - using DirectSubtitleProcessor instead


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> AuthUser:
    """Validate session token and return current user"""
    try:
        token = credentials.credentials
        user = auth_service.validate_session(token)
        return user
    except SessionExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )


async def get_current_user_ws(token: str) -> AuthUser:
    """Validate session token for WebSocket connections"""
    # For WebSocket, we need to manually get the auth service
    auth_service = get_auth_service()
    
    try:
        user = auth_service.validate_session(token)
        return user
    except SessionExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )


# Optional user dependency (for endpoints that work with or without auth)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: Annotated[AuthService, Depends(get_auth_service)] = None
) -> Optional[AuthUser]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = auth_service.validate_session(token)
        return user
    except (SessionExpiredError, Exception):
        return None


def get_user_subtitle_processor(
    current_user: Annotated[AuthUser, Depends(get_current_user)]
) -> DirectSubtitleProcessor:
    """Get subtitle processor for user-specific processing"""
    # Return the same processor instance - user-specific logic is handled in processing parameters
    return get_subtitle_processor()


# Global task progress registry for background tasks
_task_progress_registry: dict = {}


@lru_cache()
def get_task_progress_registry() -> dict:
    """Get task progress registry for background tasks"""
    return _task_progress_registry


async def init_services():
    """Initialize all services at startup"""
    logger.info("Initializing services...")
    
    # Initialize core services
    get_database_manager()
    get_auth_service()
    get_vocabulary_service()
    
    # Initialize processing services  
    get_subtitle_processor()
    
    # Initialize task progress registry
    get_task_progress_registry()
    
    logger.info("All services initialized successfully")


async def cleanup_services():
    """Cleanup services at shutdown"""
    logger.info("Cleaning up services...")
    
    # Clear task progress registry
    _task_progress_registry.clear()
    
    # Clear LRU cache for singleton services
    get_database_manager.cache_clear()
    get_auth_service.cache_clear()
    get_vocabulary_service.cache_clear()
    get_subtitle_processor.cache_clear()
    get_transcription_service.cache_clear()
    # Removed get_filter_chain.cache_clear() - no longer used
    get_task_progress_registry.cache_clear()
    
    logger.info("Services cleanup completed")


# Export commonly used dependencies for convenience
__all__ = [
    'get_database_manager',
    'get_auth_service', 
    'get_vocabulary_service',
    'get_subtitle_processor',
    'get_transcription_service',
    'get_user_subtitle_processor',
    # Removed unused filter chain exports
    'get_task_progress_registry',
    'get_current_user',
    'get_current_user_ws',
    'get_optional_user',
    'security',
    'init_services',
    'cleanup_services'
]
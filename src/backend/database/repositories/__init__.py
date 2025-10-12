"""Database repositories for clean data access"""

# Repository interfaces
from .interfaces import (
    BaseRepositoryInterface,
    ProcessingSessionRepositoryInterface,
    UserRepositoryInterface,
    UserVocabularyProgressRepositoryInterface,
    VocabularyRepositoryInterface,
)

# Repository implementations (async only - no sync variants per YAGNI principle)
from .processing_repository import ProcessingRepository
from .processing_session_repository import ProcessingSessionRepository
from .user_repository import UserRepository
from .user_vocabulary_progress_repository import UserVocabularyProgressRepository
from .vocabulary_repository import VocabularyRepository

__all__ = [
    # Interfaces
    "BaseRepositoryInterface",
    # Implementations
    "ProcessingRepository",
    "ProcessingSessionRepository",
    "ProcessingSessionRepositoryInterface",
    "UserRepository",
    "UserRepositoryInterface",
    "UserVocabularyProgressRepository",
    "UserVocabularyProgressRepositoryInterface",
    "VocabularyRepository",
    "VocabularyRepositoryInterface",
]

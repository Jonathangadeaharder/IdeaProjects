"""
Repository Package
Standardized database access patterns for all services
"""

from .base_repository import BaseRepository
from .user_repository import UserRepository, User

__all__ = ['BaseRepository', 'UserRepository', 'User']

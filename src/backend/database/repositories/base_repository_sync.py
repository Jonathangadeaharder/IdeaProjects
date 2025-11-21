"""Base repository for synchronous database operations

This is used by repositories that haven't been migrated to async patterns yet.
"""

from typing import Generic, TypeVar

from sqlalchemy.orm import DeclarativeBase, Session

T = TypeVar("T", bound=DeclarativeBase)
ID = TypeVar("ID")


class BaseSyncRepository(Generic[T, ID]):
    """
    Base repository for synchronous SQLAlchemy operations

    This provides a base class for repositories that use synchronous Session
    instead of AsyncSession. These repositories should eventually be migrated
    to async patterns using BaseRepository instead.

    Args:
        model: SQLAlchemy model class
    """

    def __init__(self, model: type[T]):
        self.model = model

    async def get_by_id(self, db: Session, entity_id: ID) -> T | None:
        """
        Get entity by ID

        Args:
            db: Database session
            entity_id: Primary key value

        Returns:
            Entity if found, None otherwise
        """
        return db.query(self.model).filter(self.model.id == entity_id).first()

    async def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> list[T]:
        """
        Get all entities with pagination

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of entities
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    async def create(self, db: Session, **kwargs) -> T:
        """
        Create new entity

        Args:
            db: Database session
            **kwargs: Entity attributes

        Returns:
            Created entity
        """
        instance = self.model(**kwargs)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance

    async def update(self, db: Session, entity_id: ID, **kwargs) -> T | None:
        """
        Update entity by ID

        Args:
            db: Database session
            entity_id: Primary key value
            **kwargs: Attributes to update

        Returns:
            Updated entity if found, None otherwise
        """
        instance = await self.get_by_id(db, entity_id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            db.commit()
            db.refresh(instance)
        return instance

    async def delete(self, db: Session, entity_id: ID) -> bool:
        """
        Delete entity by ID

        Args:
            db: Database session
            entity_id: Primary key value

        Returns:
            True if deleted, False if not found
        """
        instance = await self.get_by_id(db, entity_id)
        if instance:
            db.delete(instance)
            db.commit()
            return True
        return False

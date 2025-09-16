"""Database configuration with SQLAlchemy's built-in connection pooling"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from core.config import settings


class Base(DeclarativeBase):
    pass


# Create async engine with built-in connection pooling
if settings.db_type == "postgresql":
    # PostgreSQL with asyncpg
    database_url = settings.get_database_url().replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(
        database_url,
        pool_size=settings.postgres_pool_size,
        max_overflow=settings.postgres_max_overflow,
        pool_pre_ping=True,
        echo=settings.debug,
    )
else:
    # SQLite with aiosqlite
    database_url = f"sqlite+aiosqlite:///{settings.get_database_path()}"
    engine = create_async_engine(
        database_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=settings.debug,
    )

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_db_and_tables():
    """Create database tables"""
    from core.auth import Base as AuthBase
    async with engine.begin() as conn:
        await conn.run_sync(AuthBase.metadata.create_all)


async def init_db():
    """Initialize database tables"""
    # Import FastAPI-Users models and other models to ensure they're registered with Base
    from core.auth import Base as AuthBase
    import database.models  # noqa: F401 - Import other models
    async with engine.begin() as conn:
        await conn.run_sync(AuthBase.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()
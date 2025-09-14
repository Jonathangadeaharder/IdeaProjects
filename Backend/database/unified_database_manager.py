"""
Unified Database Manager supporting both SQLite and PostgreSQL
"""
import logging
from typing import Any, Dict, List, Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool

from core.config import settings
from database.models import Base

logger = logging.getLogger(__name__)


class UnifiedDatabaseManager:
    """
    Database manager that supports both SQLite and PostgreSQL
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the unified database manager
        
        Args:
            database_url: Database connection URL. If None, uses settings
        """
        self.database_url = database_url or settings.get_database_url()
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        self._create_tables()
        
    def _create_engine(self):
        """Create SQLAlchemy engine based on database type"""
        if self.database_url.startswith("postgresql://"):
            # PostgreSQL configuration
            engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=settings.postgres_pool_size,
                max_overflow=settings.postgres_max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=settings.debug
            )
            logger.info("Created PostgreSQL engine with connection pooling")
        else:
            # SQLite configuration
            engine = create_engine(
                self.database_url,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
                echo=settings.debug
            )
            logger.info("Created SQLite engine")
            
        return engine
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created/verified successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Get a database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries containing query results
        """
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params or {})
                # Convert to list of dictionaries
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        Execute an UPDATE/DELETE query and return affected rows
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params or {})
                return result.rowcount
        except Exception as e:
            logger.error(f"Update execution failed: {e}")
            raise
    
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """
        Execute an INSERT query and return the last inserted row ID
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Last inserted row ID
        """
        try:
            with self.get_session() as session:
                result = session.execute(text(query), params or {})
                return result.lastrowid
        except Exception as e:
            logger.error(f"Insert execution failed: {e}")
            raise
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute a query multiple times with different parameters
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Total number of affected rows
        """
        try:
            total_affected = 0
            with self.get_session() as session:
                for params in params_list:
                    result = session.execute(text(query), params or {})
                    total_affected += result.rowcount
            return total_affected
        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            raise
    
    @contextmanager
    def transaction(self):
        """
        Create a transaction context manager
        
        Yields:
            Database session for transaction operations
        """
        with self.get_session() as session:
            yield session
    
    @contextmanager
    def get_connection(self):
        """
        Get a raw database connection (for backward compatibility)
        
        Yields:
            Raw database connection
        """
        conn = self.engine.raw_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def test_connection(self) -> bool:
        """
        Test database connectivity
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def close(self):
        """Close database connections"""
        if hasattr(self, 'engine'):
            self.engine.dispose()
            logger.info("Database connections closed")

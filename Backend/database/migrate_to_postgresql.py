"""
Data migration script from SQLite to PostgreSQL
"""
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from core.config import settings
from database.unified_database_manager import UnifiedDatabaseManager

logger = logging.getLogger(__name__)


class SQLiteToPostgreSQLMigrator:
    """Migrates data from SQLite to PostgreSQL"""
    
    def __init__(self, sqlite_path: str, postgresql_url: str):
        self.sqlite_path = sqlite_path
        self.postgresql_url = postgresql_url
        
        # Setup connections
        self.sqlite_conn = sqlite3.connect(sqlite_path)
        self.sqlite_conn.row_factory = sqlite3.Row
        
        self.pg_manager = UnifiedDatabaseManager(postgresql_url)
        
    def migrate_table(self, table_name: str, batch_size: int = 1000) -> int:
        """
        Migrate a single table from SQLite to PostgreSQL
        
        Args:
            table_name: Name of the table to migrate
            batch_size: Number of records to process in each batch
            
        Returns:
            Number of records migrated
        """
        logger.info(f"Starting migration for table: {table_name}")
        
        # Get table structure from SQLite
        cursor = self.sqlite_conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        
        if not columns_info:
            logger.warning(f"Table {table_name} not found in SQLite database")
            return 0
        
        columns = [col[1] for col in columns_info]  # Column names
        
        # Count total records
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_records = cursor.fetchone()[0]
        
        if total_records == 0:
            logger.info(f"No data to migrate for table {table_name}")
            return 0
        
        logger.info(f"Migrating {total_records} records from {table_name}")
        
        # Clear existing data in PostgreSQL table (optional)
        with self.pg_manager.get_session() as session:
            session.execute(text(f"DELETE FROM {table_name}"))
            session.commit()
        
        # Migrate data in batches
        migrated_count = 0
        offset = 0
        
        while offset < total_records:
            # Fetch batch from SQLite
            cursor.execute(f"""
                SELECT {', '.join(columns)} 
                FROM {table_name} 
                LIMIT {batch_size} OFFSET {offset}
            """)
            rows = cursor.fetchall()
            
            if not rows:
                break
                
            # Prepare batch insert for PostgreSQL
            placeholders = ', '.join(['?' for _ in columns])
            insert_query = f"""
                INSERT INTO {table_name} ({', '.join(columns)}) 
                VALUES ({placeholders})
            """
            
            # Convert rows to tuples
            batch_data = [tuple(row) for row in rows]
            
            # Insert batch into PostgreSQL
            try:
                affected = self.pg_manager.execute_many(insert_query, batch_data)
                migrated_count += affected
                logger.info(f"Migrated batch: {migrated_count}/{total_records} records for {table_name}")
            except Exception as e:
                logger.error(f"Error migrating batch for {table_name}: {e}")
                raise
            
            offset += batch_size
        
        logger.info(f"Completed migration for {table_name}: {migrated_count} records")
        return migrated_count
    
    def migrate_all_tables(self) -> Dict[str, int]:
        """
        Migrate all tables from SQLite to PostgreSQL
        
        Returns:
            Dictionary mapping table names to number of migrated records
        """
        # Define migration order (tables with foreign keys should come after their referenced tables)
        migration_order = [
            'word_categories',
            'vocabulary', 
            'users',
            'user_sessions',
            'videos',
            'word_category_associations',
            'unknown_words',
            'user_learning_progress',
            'processing_sessions',
            'session_word_discoveries',
            'database_metadata'
        ]
        
        results = {}
        
        for table_name in migration_order:
            try:
                count = self.migrate_table(table_name)
                results[table_name] = count
            except Exception as e:
                logger.error(f"Failed to migrate table {table_name}: {e}")
                results[table_name] = -1  # Indicate failure
        
        return results
    
    def verify_migration(self) -> bool:
        """
        Verify that the migration was successful by comparing record counts
        
        Returns:
            True if verification passes, False otherwise
        """
        logger.info("Starting migration verification")
        
        # Get list of tables from SQLite
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        verification_passed = True
        
        for table in tables:
            # Count records in SQLite
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = cursor.fetchone()[0]
            
            # Count records in PostgreSQL
            pg_result = self.pg_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}")
            pg_count = pg_result[0]['count'] if pg_result else 0
            
            if sqlite_count != pg_count:
                logger.error(f"Verification failed for {table}: SQLite={sqlite_count}, PostgreSQL={pg_count}")
                verification_passed = False
            else:
                logger.info(f"Verification passed for {table}: {sqlite_count} records")
        
        return verification_passed
    
    def close(self):
        """Close database connections"""
        if hasattr(self, 'sqlite_conn'):
            self.sqlite_conn.close()
        if hasattr(self, 'pg_manager'):
            self.pg_manager.close()


def main():
    """Main migration function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get database paths
    sqlite_path = settings.get_database_path()
    postgresql_url = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    
    logger.info(f"Starting migration from SQLite ({sqlite_path}) to PostgreSQL")
    
    # Check if SQLite database exists
    if not Path(sqlite_path).exists():
        logger.error(f"SQLite database not found: {sqlite_path}")
        return False
    
    migrator = None
    try:
        # Create migrator
        migrator = SQLiteToPostgreSQLMigrator(str(sqlite_path), postgresql_url)
        
        # Test PostgreSQL connection
        if not migrator.pg_manager.test_connection():
            logger.error("Failed to connect to PostgreSQL database")
            return False
        
        # Perform migration
        results = migrator.migrate_all_tables()
        
        # Print results
        logger.info("Migration Results:")
        total_migrated = 0
        for table, count in results.items():
            if count >= 0:
                logger.info(f"  {table}: {count} records")
                total_migrated += count
            else:
                logger.error(f"  {table}: FAILED")
        
        logger.info(f"Total records migrated: {total_migrated}")
        
        # Verify migration
        if migrator.verify_migration():
            logger.info("Migration verification PASSED")
            return True
        else:
            logger.error("Migration verification FAILED")
            return False
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False
    finally:
        if migrator:
            migrator.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

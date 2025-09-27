#!/usr/bin/env python3
"""
Fix database schema issues for vocabulary tables
"""

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, inspect, text
from core.config import settings
from database.models import Base

def fix_database_schema():
    """Recreate tables with proper schema"""
    print("[INFO] Fixing database schema...")

    # Create engine
    engine = create_engine(settings.get_database_url())

    # Check current tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"[INFO] Existing tables: {existing_tables}")

    # Check if user_learning_progress exists and has concept_id
    if 'user_learning_progress' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('user_learning_progress')]
        print(f"[INFO] user_learning_progress columns: {columns}")

        if 'concept_id' not in columns:
            print("[WARN] concept_id column missing, dropping and recreating table...")
            with engine.begin() as conn:
                conn.execute(text("DROP TABLE IF EXISTS user_learning_progress"))
                conn.execute(text("DROP TABLE IF EXISTS session_word_discoveries"))
                conn.execute(text("DROP TABLE IF EXISTS vocabulary_translations"))
                conn.execute(text("DROP TABLE IF EXISTS vocabulary_concepts"))

    # Create all tables
    print("[INFO] Creating tables with proper schema...")
    Base.metadata.create_all(bind=engine, checkfirst=True)

    # Verify the fix
    inspector = inspect(engine)
    if 'user_learning_progress' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('user_learning_progress')]
        if 'concept_id' in columns:
            print("[SUCCESS] Database schema fixed successfully!")
            print(f"[INFO] user_learning_progress columns: {columns}")
        else:
            print("[ERROR] Failed to add concept_id column")
    else:
        print("[ERROR] Failed to create user_learning_progress table")

if __name__ == "__main__":
    fix_database_schema()
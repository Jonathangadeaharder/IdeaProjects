#!/usr/bin/env python3
"""
Examine the actual database structure and contents to understand current state.
"""

import sqlite3
import sys
import os

def examine_database():
    db_path = "/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/data/langplug.db"

    if not os.path.exists(db_path):
        print(f"[ERROR] Database file not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        print("[INFO] EXAMINING DATABASE CONTENTS")
        print("=" * 50)

        # Check each table's contents
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            print(f"\n[INFO] Table: {table}")

            # Get row count
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   Rows: {count}")

            if count > 0 and count < 10:
                # Show sample data for small tables
                cursor = conn.execute(f"SELECT * FROM {table} LIMIT 5")
                rows = cursor.fetchall()
                if rows:
                    print("   Sample data:")
                    for row in rows:
                        print(f"     {dict(row)}")
            elif count > 0:
                # Show just first row for large tables
                cursor = conn.execute(f"SELECT * FROM {table} LIMIT 1")
                row = cursor.fetchone()
                if row:
                    print("   Sample row:")
                    print(f"     {dict(row)}")

        # Check for vocabulary-related data
        print(f"\n🔍 SEARCHING FOR VOCABULARY DATA:")
        print("=" * 50)

        # Check if vocabulary table has any German/Spanish data
        cursor = conn.execute("SELECT * FROM vocabulary LIMIT 5")
        vocab_rows = cursor.fetchall()
        print(f"Vocabulary table sample ({len(vocab_rows)} rows):")
        for row in vocab_rows:
            print(f"  {dict(row)}")

        # Check word_categories for CEFR levels
        cursor = conn.execute("SELECT * FROM word_categories")
        category_rows = cursor.fetchall()
        print(f"\nWord categories ({len(category_rows)} rows):")
        for row in category_rows:
            print(f"  {dict(row)}")

        # Check database metadata
        cursor = conn.execute("SELECT * FROM database_metadata")
        metadata_rows = cursor.fetchall()
        print(f"\nDatabase metadata ({len(metadata_rows)} rows):")
        for row in metadata_rows:
            print(f"  {dict(row)}")

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    examine_database()
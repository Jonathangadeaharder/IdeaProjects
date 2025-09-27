#!/usr/bin/env python3
"""
Comprehensive vocabulary database verification script.
Verifies import success, data integrity, and production readiness.
"""

import sqlite3
import sys
import os
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import random

def connect_to_database(db_path: str) -> sqlite3.Connection:
    """Connect to the SQLite database with proper settings."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        # Test connectivity
        conn.execute("SELECT 1").fetchone()
        print("✅ Database connectivity: SUCCESS")
        return conn
    except sqlite3.Error as e:
        print(f"❌ Database connectivity: FAILED - {e}")
        sys.exit(1)

def verify_database_integrity(conn: sqlite3.Connection) -> bool:
    """Run database integrity checks."""
    try:
        result = conn.execute("PRAGMA integrity_check").fetchone()
        if result[0] == 'ok':
            print("✅ Database integrity: OK")
            return True
        else:
            print(f"❌ Database integrity: FAILED - {result[0]}")
            return False
    except sqlite3.Error as e:
        print(f"❌ Database integrity: ERROR - {e}")
        return False

def examine_schema(conn: sqlite3.Connection) -> Dict[str, List[str]]:
    """Examine and display database schema."""
    print("\n📋 DATABASE SCHEMA:")
    print("=" * 50)

    tables = {}
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for table_row in cursor.fetchall():
        table_name = table_row[0]
        print(f"\n🗂️  Table: {table_name}")

        # Get table structure
        columns = []
        cursor2 = conn.execute(f"PRAGMA table_info({table_name})")
        for col in cursor2.fetchall():
            col_info = f"  {col[1]} ({col[2]})" + (" NOT NULL" if col[3] else "") + (" PRIMARY KEY" if col[5] else "")
            columns.append(col_info)
            print(col_info)
        tables[table_name] = columns

    return tables

def count_entries_by_level(conn: sqlite3.Connection) -> Dict[str, int]:
    """Count vocabulary entries by CEFR level."""
    print("\n📊 ENTRY COUNTS BY CEFR LEVEL:")
    print("=" * 50)

    counts = {}
    total = 0

    try:
        # Get all vocabulary entries with their levels
        cursor = conn.execute("""
            SELECT wc.level, COUNT(DISTINCT v.id) as count
            FROM vocabulary v
            JOIN word_category_associations wca ON v.id = wca.vocabulary_id
            JOIN word_categories wc ON wca.category_id = wc.id
            GROUP BY wc.level
            ORDER BY wc.level
        """)

        for row in cursor.fetchall():
            level = row[0]
            count = row[1]
            counts[level] = count
            total += count
            print(f"  {level}: {count:,} entries")

        print(f"\n  Total: {total:,} entries")

        # Also get total unique vocabulary entries
        cursor = conn.execute("SELECT COUNT(*) FROM vocabulary")
        unique_total = cursor.fetchone()[0]
        print(f"  Unique vocabulary entries: {unique_total:,}")

        return counts

    except sqlite3.Error as e:
        print(f"❌ Error counting entries: {e}")
        return {}

def check_data_quality(conn: sqlite3.Connection) -> Dict[str, any]:
    """Perform comprehensive data quality checks."""
    print("\n🔍 DATA QUALITY CHECKS:")
    print("=" * 50)

    issues = []
    stats = {}

    try:
        # Check for NULL values in critical fields
        print("\n🔎 NULL Value Check:")
        cursor = conn.execute("""
            SELECT
                SUM(CASE WHEN german_word IS NULL OR german_word = '' THEN 1 ELSE 0 END) as null_german,
                SUM(CASE WHEN spanish_translation IS NULL OR spanish_translation = '' THEN 1 ELSE 0 END) as null_spanish,
                SUM(CASE WHEN base_form IS NULL OR base_form = '' THEN 1 ELSE 0 END) as null_base_form
            FROM vocabulary
        """)
        row = cursor.fetchone()

        if row[0] == 0:
            print("  ✅ German words: No NULL values")
        else:
            issues.append(f"Found {row[0]} NULL/empty German words")
            print(f"  ❌ German words: {row[0]} NULL/empty values")

        if row[1] == 0:
            print("  ✅ Spanish translations: No NULL values")
        else:
            issues.append(f"Found {row[1]} NULL/empty Spanish translations")
            print(f"  ❌ Spanish translations: {row[1]} NULL/empty values")

        if row[2] == 0:
            print("  ✅ Base forms: No NULL values")
        else:
            issues.append(f"Found {row[2]} NULL/empty base forms")
            print(f"  ❌ Base forms: {row[2]} NULL/empty values")

        # Check for duplicate German words
        print("\n🔎 Duplicate Check:")
        cursor = conn.execute("""
            SELECT german_word, COUNT(*) as count
            FROM vocabulary
            GROUP BY LOWER(german_word)
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 10
        """)
        duplicates = cursor.fetchall()

        if not duplicates:
            print("  ✅ No duplicate German words found")
        else:
            print(f"  ⚠️  Found {len(duplicates)} sets of duplicate German words:")
            for dup in duplicates[:5]:  # Show first 5
                print(f"    '{dup[0]}' appears {dup[1]} times")

        # Check character encoding (look for special German/Spanish characters)
        print("\n🔎 Character Encoding Check:")
        cursor = conn.execute("""
            SELECT
                SUM(CASE WHEN german_word LIKE '%ä%' OR german_word LIKE '%ö%' OR german_word LIKE '%ü%' OR german_word LIKE '%ß%' THEN 1 ELSE 0 END) as german_special,
                SUM(CASE WHEN spanish_translation LIKE '%ñ%' OR spanish_translation LIKE '%á%' OR spanish_translation LIKE '%é%' OR spanish_translation LIKE '%í%' OR spanish_translation LIKE '%ó%' OR spanish_translation LIKE '%ú%' THEN 1 ELSE 0 END) as spanish_special,
                COUNT(*) as total
            FROM vocabulary
        """)
        row = cursor.fetchone()

        german_special_pct = (row[0] / row[2]) * 100 if row[2] > 0 else 0
        spanish_special_pct = (row[1] / row[2]) * 100 if row[2] > 0 else 0

        print(f"  German special characters: {row[0]} entries ({german_special_pct:.1f}%)")
        print(f"  Spanish special characters: {row[1]} entries ({spanish_special_pct:.1f}%)")

        if german_special_pct > 5:  # We expect some German special chars
            print("  ✅ German character encoding appears correct")
        else:
            issues.append("Suspiciously low German special character count - encoding issue?")
            print("  ⚠️  Low German special character count - possible encoding issue")

        stats['issues'] = issues
        stats['duplicates'] = len(duplicates)
        stats['german_special_pct'] = german_special_pct
        stats['spanish_special_pct'] = spanish_special_pct

        return stats

    except sqlite3.Error as e:
        print(f"❌ Error in data quality checks: {e}")
        return {'error': str(e)}

def verify_relationships(conn: sqlite3.Connection) -> bool:
    """Verify foreign key relationships and table integrity."""
    print("\n🔗 RELATIONSHIP INTEGRITY CHECKS:")
    print("=" * 50)

    try:
        # Check word_categories table
        print("\n🔎 Word Categories:")
        cursor = conn.execute("SELECT level, COUNT(*) FROM word_categories GROUP BY level ORDER BY level")
        categories = cursor.fetchall()

        expected_levels = {'A1', 'A2', 'B1', 'B2', 'C1'}
        found_levels = {row[0] for row in categories}

        if expected_levels == found_levels:
            print("  ✅ All CEFR levels present in word_categories")
            for level, count in categories:
                print(f"    {level}: {count} categories")
        else:
            missing = expected_levels - found_levels
            extra = found_levels - expected_levels
            if missing:
                print(f"  ❌ Missing CEFR levels: {missing}")
            if extra:
                print(f"  ⚠️  Extra CEFR levels: {extra}")

        # Check associations integrity
        print("\n🔎 Word Category Associations:")
        cursor = conn.execute("""
            SELECT COUNT(*) as total_associations,
                   COUNT(DISTINCT vocabulary_id) as unique_vocab,
                   COUNT(DISTINCT category_id) as unique_categories
            FROM word_category_associations
        """)
        row = cursor.fetchone()
        print(f"  Total associations: {row[0]:,}")
        print(f"  Unique vocabulary items: {row[1]:,}")
        print(f"  Unique categories used: {row[2]:,}")

        # Check for orphaned associations
        cursor = conn.execute("""
            SELECT COUNT(*)
            FROM word_category_associations wca
            LEFT JOIN vocabulary v ON wca.vocabulary_id = v.id
            WHERE v.id IS NULL
        """)
        orphaned_vocab = cursor.fetchone()[0]

        cursor = conn.execute("""
            SELECT COUNT(*)
            FROM word_category_associations wca
            LEFT JOIN word_categories wc ON wca.category_id = wc.id
            WHERE wc.id IS NULL
        """)
        orphaned_categories = cursor.fetchone()[0]

        if orphaned_vocab == 0 and orphaned_categories == 0:
            print("  ✅ No orphaned associations found")
            return True
        else:
            print(f"  ❌ Found {orphaned_vocab} orphaned vocabulary associations")
            print(f"  ❌ Found {orphaned_categories} orphaned category associations")
            return False

    except sqlite3.Error as e:
        print(f"❌ Error checking relationships: {e}")
        return False

def sample_data_validation(conn: sqlite3.Connection, samples_per_level: int = 3) -> Dict[str, List]:
    """Query and validate sample entries from each CEFR level."""
    print(f"\n🎯 SAMPLE DATA VALIDATION ({samples_per_level} per level):")
    print("=" * 50)

    samples = {}

    try:
        # Get samples from each level
        cursor = conn.execute("""
            SELECT DISTINCT wc.level
            FROM word_categories wc
            ORDER BY wc.level
        """)
        levels = [row[0] for row in cursor.fetchall()]

        for level in levels:
            print(f"\n📝 Level {level} Samples:")
            cursor = conn.execute("""
                SELECT v.german_word, v.spanish_translation, v.base_form
                FROM vocabulary v
                JOIN word_category_associations wca ON v.id = wca.vocabulary_id
                JOIN word_categories wc ON wca.category_id = wc.id
                WHERE wc.level = ?
                ORDER BY RANDOM()
                LIMIT ?
            """, (level, samples_per_level))

            level_samples = []
            for i, row in enumerate(cursor.fetchall(), 1):
                german = row[0]
                spanish = row[1]
                base_form = row[2]

                print(f"  {i}. {german} → {spanish}")
                if base_form != german:
                    print(f"     (base: {base_form})")

                level_samples.append({
                    'german': german,
                    'spanish': spanish,
                    'base_form': base_form
                })

            samples[level] = level_samples

        return samples

    except sqlite3.Error as e:
        print(f"❌ Error sampling data: {e}")
        return {}

def performance_testing(conn: sqlite3.Connection) -> Dict[str, float]:
    """Test query performance for common database operations."""
    print("\n⚡ PERFORMANCE TESTING:")
    print("=" * 50)

    import time

    results = {}

    try:
        # Test 1: Simple vocabulary lookup
        start_time = time.time()
        cursor = conn.execute("SELECT * FROM vocabulary WHERE german_word = 'Haus'")
        cursor.fetchall()
        results['simple_lookup'] = time.time() - start_time
        print(f"  Simple lookup: {results['simple_lookup']:.4f}s")

        # Test 2: Level-based query
        start_time = time.time()
        cursor = conn.execute("""
            SELECT v.german_word, v.spanish_translation
            FROM vocabulary v
            JOIN word_category_associations wca ON v.id = wca.vocabulary_id
            JOIN word_categories wc ON wca.category_id = wc.id
            WHERE wc.level = 'A1'
            LIMIT 100
        """)
        cursor.fetchall()
        results['level_query'] = time.time() - start_time
        print(f"  Level-based query (100 results): {results['level_query']:.4f}s")

        # Test 3: Search query
        start_time = time.time()
        cursor = conn.execute("""
            SELECT v.german_word, v.spanish_translation
            FROM vocabulary v
            WHERE v.german_word LIKE 'haus%'
            LIMIT 50
        """)
        cursor.fetchall()
        results['search_query'] = time.time() - start_time
        print(f"  Search query (LIKE): {results['search_query']:.4f}s")

        # Test 4: Count query
        start_time = time.time()
        cursor = conn.execute("SELECT COUNT(*) FROM vocabulary")
        cursor.fetchone()
        results['count_query'] = time.time() - start_time
        print(f"  Count query: {results['count_query']:.4f}s")

        # Check if indexes exist
        print("\n🔍 Index Analysis:")
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
        indexes = cursor.fetchall()

        if indexes:
            print("  Indexes found:")
            for idx in indexes:
                print(f"    - {idx[0]}")
        else:
            print("  ⚠️  No custom indexes found - consider adding for better performance")

        return results

    except sqlite3.Error as e:
        print(f"❌ Error in performance testing: {e}")
        return {}

def compare_with_expected_counts(actual_counts: Dict[str, int]) -> None:
    """Compare actual counts with expected counts from CSV files."""
    print("\n📈 COMPARISON WITH EXPECTED COUNTS:")
    print("=" * 50)

    expected_counts = {
        'A1': 717,
        'A2': 581,
        'B1': 959,
        'B2': 1413,
        'C1': 2482
    }

    total_expected = sum(expected_counts.values())
    total_actual = sum(actual_counts.values())

    print(f"Expected total: {total_expected:,}")
    print(f"Actual total: {total_actual:,}")
    print(f"Difference: {total_actual - total_expected:,}")

    if abs(total_actual - total_expected) <= 10:  # Allow small variance
        print("✅ Total count matches expected (within tolerance)")
    else:
        print("⚠️  Total count differs significantly from expected")

    print("\nLevel-by-level comparison:")
    for level in ['A1', 'A2', 'B1', 'B2', 'C1']:
        expected = expected_counts.get(level, 0)
        actual = actual_counts.get(level, 0)
        diff = actual - expected

        status = "✅" if abs(diff) <= 5 else "⚠️ " if abs(diff) <= 50 else "❌"
        print(f"  {level}: Expected {expected:,}, Got {actual:,}, Diff {diff:+,} {status}")

def generate_final_report(
    counts: Dict[str, int],
    quality_stats: Dict[str, any],
    performance_results: Dict[str, float],
    relationship_ok: bool
) -> None:
    """Generate final verification report."""
    print("\n" + "=" * 60)
    print("🎯 FINAL VERIFICATION REPORT")
    print("=" * 60)

    total_entries = sum(counts.values())

    # Overall status
    critical_issues = len(quality_stats.get('issues', []))

    if critical_issues == 0 and relationship_ok and total_entries > 5000:
        status = "✅ READY FOR PRODUCTION"
        color = "🟢"
    elif critical_issues <= 2 and relationship_ok and total_entries > 4000:
        status = "⚠️  ACCEPTABLE WITH MINOR ISSUES"
        color = "🟡"
    else:
        status = "❌ NOT READY FOR PRODUCTION"
        color = "🔴"

    print(f"\n{color} Overall Status: {status}")

    print(f"\n📊 Summary Statistics:")
    print(f"   Total vocabulary entries: {total_entries:,}")
    print(f"   CEFR levels covered: {len(counts)}")
    print(f"   Data quality issues: {critical_issues}")
    print(f"   Relationship integrity: {'OK' if relationship_ok else 'Issues found'}")

    if performance_results:
        avg_query_time = sum(performance_results.values()) / len(performance_results)
        print(f"   Average query time: {avg_query_time:.4f}s")

    print(f"\n📋 Recommendations:")

    if quality_stats.get('duplicates', 0) > 0:
        print("   - Review and resolve duplicate German words")

    if quality_stats.get('german_special_pct', 0) < 5:
        print("   - Verify German character encoding is correct")

    if not relationship_ok:
        print("   - Fix foreign key relationship issues before production")

    if any(time > 0.1 for time in performance_results.values()):
        print("   - Consider adding database indexes for better performance")

    if critical_issues == 0 and relationship_ok:
        print("   - Database appears ready for production use!")

def main():
    """Main verification function."""
    print("🔍 VOCABULARY DATABASE VERIFICATION")
    print("=" * 60)

    db_path = "/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend/data/langplug.db"

    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        sys.exit(1)

    # Connect to database
    conn = connect_to_database(db_path)

    try:
        # Run all verification steps
        integrity_ok = verify_database_integrity(conn)
        schema = examine_schema(conn)
        counts = count_entries_by_level(conn)
        quality_stats = check_data_quality(conn)
        relationship_ok = verify_relationships(conn)
        samples = sample_data_validation(conn)
        performance_results = performance_testing(conn)

        # Compare with expected counts
        compare_with_expected_counts(counts)

        # Generate final report
        generate_final_report(counts, quality_stats, performance_results, relationship_ok)

    finally:
        conn.close()
        print(f"\n✅ Database connection closed")

if __name__ == "__main__":
    main()
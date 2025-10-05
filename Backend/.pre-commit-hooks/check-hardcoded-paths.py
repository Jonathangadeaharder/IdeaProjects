#!/usr/bin/env python3
"""
Pre-commit hook to prevent hardcoded API paths in tests.

This hook enforces the path standardization policy:
"Use url_builder.url_for() with route names instead of hardcoded paths
for better maintainability and type safety."

Usage:
    As a pre-commit hook - automatically checks staged files
    Manual: python .pre-commit-hooks/check-hardcoded-paths.py file1.py file2.py

Exit codes:
    0 - No hardcoded paths found
    1 - Hardcoded paths found (blocks commit)
"""

import argparse
import re
import sys
from pathlib import Path

# Pattern to detect hardcoded API paths in async_client calls
HARDCODED_PATH_PATTERN = r'async_client\.(get|post|put|delete|patch)\s*\(\s*["\'][/]'

# Approved hardcoded paths (paths that intentionally don't use route names)
APPROVED_HARDCODED_PATHS = [
    r'"/health"',  # Health check endpoint has no route name
    r"'/health'",
    r'"/api/auth/forgot-password"',  # Testing non-existent endpoint
    r"'/api/auth/forgot-password'",
]

# Pattern to detect if line is in a comment or documentation
COMMENT_PATTERN = r'^\s*(#|"""|\'\'\')'


def check_file_for_hardcoded_paths(filepath: Path) -> list[tuple[int, str]]:
    """
    Check a Python test file for hardcoded API paths.

    Args:
        filepath: Path to the Python file to check

    Returns:
        List of (line_number, line_content) tuples for hardcoded paths
    """
    violations = []

    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
        return violations

    for line_num, line in enumerate(lines, start=1):
        # Skip comments and documentation
        if re.match(COMMENT_PATTERN, line):
            continue

        # Check if line contains hardcoded path pattern
        if re.search(HARDCODED_PATH_PATTERN, line):
            # Check if it's an approved hardcoded path
            is_approved = False
            for approved_path in APPROVED_HARDCODED_PATHS:
                if re.search(approved_path, line):
                    is_approved = True
                    break

            if not is_approved:
                violations.append((line_num, line.strip()))

    return violations


def main(argv=None):
    """Main entry point for the hook."""
    parser = argparse.ArgumentParser(
        description="Check Python test files for hardcoded API paths",
        epilog="""
Approved hardcoded paths:
  - "/health" - Health check endpoint (no route name)
  - "/api/auth/forgot-password" - Testing non-existent endpoint

All other API paths should use url_builder.url_for("route_name") instead.
""",
    )
    parser.add_argument("filenames", nargs="*", help="Files to check")
    args = parser.parse_args(argv)

    # Filter to only test files
    test_files = [Path(f) for f in args.filenames if f.endswith(".py") and "/test" in f.replace("\\", "/")]

    if not test_files:
        return 0  # No test files to check

    all_violations = []

    for filepath in test_files:
        violations = check_file_for_hardcoded_paths(filepath)
        if violations:
            all_violations.append((filepath, violations))

    if all_violations:
        print("\n[FAIL] Hardcoded API paths detected!", file=sys.stderr)
        print("\nPath standardization policy:", file=sys.stderr)
        print("  Use url_builder.url_for() with route names instead of hardcoded paths", file=sys.stderr)
        print("\nHardcoded paths found in:\n", file=sys.stderr)

        for filepath, violations in all_violations:
            print(f"\n{filepath}:", file=sys.stderr)
            for line_num, line_content in violations:
                print(f"  Line {line_num}: {line_content}", file=sys.stderr)

        print("\n" + "=" * 70, file=sys.stderr)
        print("How to fix:", file=sys.stderr)
        print("  1. Add url_builder to test method parameters:", file=sys.stderr)
        print("     async def test_example(self, async_client, url_builder):", file=sys.stderr)
        print("", file=sys.stderr)
        print("  2. Replace hardcoded paths with url_builder.url_for():", file=sys.stderr)
        print("     Before: await async_client.get('/api/vocabulary/stats')", file=sys.stderr)
        print("     After:  await async_client.get(url_builder.url_for('get_vocabulary_stats'))", file=sys.stderr)
        print("", file=sys.stderr)
        print("  3. For paths with parameters:", file=sys.stderr)
        print("     Before: await async_client.get(f'/api/vocabulary/level/{level}')", file=sys.stderr)
        print("     After:  await async_client.get(url_builder.url_for('get_vocabulary_level', level=level))", file=sys.stderr)
        print("", file=sys.stderr)
        print("  4. Find route names in Backend/api/routes/*.py (@router decorator 'name' parameter)", file=sys.stderr)
        print("=" * 70, file=sys.stderr)

        return 1  # Block commit

    return 0  # Allow commit


if __name__ == "__main__":
    sys.exit(main())

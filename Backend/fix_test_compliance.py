#!/usr/bin/env python3
"""Script to fix test compliance with CLAUDE.md rules."""

import re
import os
from pathlib import Path

def add_timeout_decorator(content: str) -> str:
    """Add @pytest.mark.timeout(30) to async test functions that don't have it."""
    lines = content.split('\n')
    result = []

    for i, line in enumerate(lines):
        result.append(line)

        # Check if this is a pytest.mark.anyio decorator
        if line.strip() == '@pytest.mark.anyio':
            # Look ahead to see if next line is already a timeout decorator
            next_line_idx = i + 1
            if (next_line_idx < len(lines) and
                '@pytest.mark.timeout' not in lines[next_line_idx]):
                # Add timeout decorator
                result.append('@pytest.mark.timeout(30)')

    return '\n'.join(result)

def rename_test_functions(content: str) -> str:
    """Rename test functions to follow When<Scenario>_Then<ExpectedOutcome> pattern."""
    # This is complex - for now we'll do this manually for key files
    return content

def process_test_file(file_path: Path):
    """Process a single test file to fix compliance issues."""
    if not file_path.name.startswith('test_') or not file_path.suffix == '.py':
        return False

    print(f"Processing {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Add timeout decorators
    content = add_timeout_decorator(content)

    # Only write if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Updated {file_path}")
        return True

    return False

def main():
    """Main function to process all test files."""
    backend_tests = Path("tests")
    if not backend_tests.exists():
        print("tests directory not found. Run from Backend directory.")
        return

    files_processed = 0
    files_changed = 0

    # Process all test files recursively
    for test_file in backend_tests.rglob("test_*.py"):
        files_processed += 1
        if process_test_file(test_file):
            files_changed += 1

    print(f"\nProcessed {files_processed} files, changed {files_changed} files.")

if __name__ == "__main__":
    main()
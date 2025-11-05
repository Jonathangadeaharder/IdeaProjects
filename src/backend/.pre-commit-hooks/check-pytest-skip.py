#!/usr/bin/env python3
"""
Pre-commit hook to prevent new pytest skip markers without approval.

This hook enforces the CLAUDE.md testing standard:
"Never introduce skip/xfail/ignore markers to bypass a failing path.
Surface the failure and coordinate with the user."

Usage:
    As a pre-commit hook - automatically checks staged files
    Manual: python .pre-commit-hooks/check-pytest-skip.py file1.py file2.py

Exit codes:
    0 - No unauthorized skip markers found
    1 - Unauthorized skip markers found (blocks commit)
"""

import argparse
import re
import sys
from pathlib import Path

# Patterns that indicate skip markers
SKIP_PATTERNS = [
    r"@pytest\.mark\.skip\(",  # @pytest.mark.skip(reason="...")
    r"@pytest\.mark\.xfail",  # @pytest.mark.xfail
    r"pytest\.skip\(",  # pytest.skip("reason")
    r"@pytest\.mark\.skipif",  # @pytest.mark.skipif (conditional skip)
]

# Approved skip reasons (case-insensitive substring match)
APPROVED_REASONS = [
    "requires openai-whisper",  # AI/ML dependencies
    "requires pytorch",
    "requires torch",
    "requires spacy",
    "requires nemo",
    "pip install",  # Installation instructions
    "SKIP_HEAVY_AI_TESTS",  # Environment-controlled skips
    "performance test",  # Manual performance tests
    "manual test",
]


def check_file_for_unapproved_skips(filepath: Path) -> list[tuple[int, str]]:
    """
    Check a Python test file for unapproved skip markers.

    Args:
        filepath: Path to the Python file to check

    Returns:
        List of (line_number, line_content) tuples for unapproved skips
    """
    violations = []

    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
        return violations

    for line_num, line in enumerate(lines, start=1):
        # Check if line contains any skip pattern
        for pattern in SKIP_PATTERNS:
            if re.search(pattern, line):
                # Check if skip reason is approved
                is_approved = False

                # Look for reason in current line and next few lines
                context_lines = lines[line_num - 1 : line_num + 3]
                context = " ".join(context_lines)

                for approved_reason in APPROVED_REASONS:
                    if approved_reason.lower() in context.lower():
                        is_approved = True
                        break

                if not is_approved:
                    violations.append((line_num, line.strip()))
                break  # Only report once per line

    return violations


def main(argv=None):
    """Main entry point for the hook."""
    parser = argparse.ArgumentParser(
        description="Check Python test files for unapproved pytest skip markers",
        epilog=f"""
Approved skip reasons (must appear in skip decorator or nearby):
{chr(10).join(f"  - {reason}" for reason in APPROVED_REASONS)}

Any skip markers without these approved reasons will block the commit.
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
        violations = check_file_for_unapproved_skips(filepath)
        if violations:
            all_violations.append((filepath, violations))

    if all_violations:
        print("\n[FAIL] Unauthorized pytest skip markers detected!", file=sys.stderr)
        print("\nPer CLAUDE.md testing standards:", file=sys.stderr)
        print('  "Never introduce skip/xfail/ignore markers to bypass a failing path."', file=sys.stderr)
        print("\nUnapproved skip markers found in:\n", file=sys.stderr)

        for filepath, violations in all_violations:
            print(f"\n{filepath}:", file=sys.stderr)
            for line_num, line_content in violations:
                print(f"  Line {line_num}: {line_content}", file=sys.stderr)

        print("\n" + "=" * 70, file=sys.stderr)
        print("How to fix:", file=sys.stderr)
        print("  1. Fix the failing test instead of skipping it", file=sys.stderr)
        print("  2. Delete the test if it's obsolete", file=sys.stderr)
        print("  3. If skip is necessary, add an approved reason:", file=sys.stderr)
        print("     - AI/ML dependencies (e.g., 'Requires PyTorch')", file=sys.stderr)
        print("     - Environment-controlled (e.g., 'SKIP_HEAVY_AI_TESTS')", file=sys.stderr)
        print("     - Manual/performance tests", file=sys.stderr)
        print("  4. Coordinate with user for exceptions", file=sys.stderr)
        print("=" * 70, file=sys.stderr)

        return 1  # Block commit

    return 0  # Allow commit


if __name__ == "__main__":
    sys.exit(main())

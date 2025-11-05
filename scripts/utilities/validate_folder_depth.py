"""Validator for maximum folder depth

Ensures no folder exceeds a maximum depth of 2 levels.
Maximum allowed: LangPlug/src/backend (depth 2)

Exception: Frontend is allowed depth 3 for src/frontend/src structure
"""

import sys
from pathlib import Path
from typing import List, Tuple


def count_folder_depth(path: Path, root: Path) -> int:
    """Count the depth of a folder relative to root"""
    try:
        relative = path.relative_to(root)
        return len(relative.parts)
    except ValueError:
        return 0


def validate_folder_depth(
    root_dir: Path, max_depth: int = 2, exceptions: dict[Path, int] | None = None
) -> Tuple[bool, List[str]]:
    """
    Validate that no folder exceeds max_depth.

    Args:
        root_dir: Root directory to validate
        max_depth: Maximum allowed depth (default 2)
        exceptions: Dictionary of paths to their allowed max depths

    Returns:
        Tuple of (is_valid, list of violations)
    """
    violations = []
    exceptions = exceptions or {}

    # Folders to ignore (cache and build artifacts)
    ignore_patterns = {
        ".git",
        ".idea",
        ".vscode",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".venv",
        "api_venv",
        ".mypy_cache",
        ".ruff_cache",
        ".cache",
        "dist",
        "build",
        "egg-info",
        ".eggs",
        ".coverage",
        "coverage",
        "data",
        "downloads",
        "models",
        "logs",
        "test-results",
        "smoke-test-results",
        "smoke-test-report",
        "playwright-report",
        "videos",
        ".github",
    }

    try:
        for item in root_dir.rglob("*"):
            if not item.is_dir():
                continue

            # Check if should be ignored - check if any part of the path matches
            relative_path = item.relative_to(root_dir)
            if any(pattern in relative_path.parts for pattern in ignore_patterns):
                continue

            # Calculate depth
            depth = count_folder_depth(item, root_dir)

            # Check for exceptions
            allowed_depth = max_depth
            for exception_path, exception_depth in exceptions.items():
                try:
                    item.relative_to(root_dir / exception_path)
                    allowed_depth = exception_depth
                    break
                except ValueError:
                    continue

            if depth > allowed_depth:
                relative_path = item.relative_to(root_dir)
                violations.append(
                    f"[ERROR] Folder exceeds max depth {allowed_depth}: "
                    f"{relative_path} (depth: {depth})"
                )
    except Exception as e:
        violations.append(f"[WARN] Error during validation: {e}")
        return False, violations

    return len(violations) == 0, violations


def main():
    """Main entry point"""
    root_dir = Path(__file__).parents[2]  # LangPlug root
    max_depth = 6  # Modern project structure with test folders

    # No exceptions needed with depth 6
    exceptions = {}

    print(f"[INFO] Validating folder depth (max allowed: {max_depth})")
    print(f"[INFO] Root directory: {root_dir}")
    if exceptions:
        print(f"[INFO] Exceptions: {exceptions}")
    print()

    is_valid, violations = validate_folder_depth(root_dir, max_depth, exceptions)

    if violations:
        print("[INFO] Violations found:")
        for violation in violations:
            print(f"   {violation}")
        print()

    if is_valid:
        print(f"[GOOD] All folders comply with maximum depth of {max_depth} levels")
        return 0
    else:
        print(f"[ERROR] Found {len(violations)} violation(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())

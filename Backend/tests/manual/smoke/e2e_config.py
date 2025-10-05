"""
E2E Smoke Test Configuration

Environment variables:
- E2E_TEST_EMAIL: Test user email (default: e2etest@example.com)
- E2E_TEST_PASSWORD: Test user password (required for security)
- E2E_BACKEND_URL: Backend URL (default: http://localhost:8000)
- E2E_FRONTEND_URL: Frontend URL (default: http://localhost:3000)
"""

import os
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent

# Server URLs
BACKEND_URL = os.getenv("E2E_BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("E2E_FRONTEND_URL", "http://localhost:3000")

# Test credentials (NEVER hard-code in production)
TEST_EMAIL = os.getenv("E2E_TEST_EMAIL", "e2etest@example.com")
TEST_PASSWORD = os.getenv("E2E_TEST_PASSWORD")

if not TEST_PASSWORD:
    raise ValueError(
        "E2E_TEST_PASSWORD environment variable is required. "
        "Example: export E2E_TEST_PASSWORD='YourSecurePassword123!'"
    )

# Screenshot directory
SCREENSHOT_DIR = REPO_ROOT / "tests" / "manual" / "smoke" / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

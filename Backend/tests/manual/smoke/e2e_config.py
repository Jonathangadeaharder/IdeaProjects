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


def check_server_health(url: str, timeout: int = 5) -> bool:
    """
    Check if a server is running and healthy.

    Args:
        url: Base URL of the server
        timeout: Request timeout in seconds

    Returns:
        True if server is healthy, False otherwise
    """
    import requests

    try:
        response = requests.get(f"{url}/health", timeout=timeout)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def start_servers_if_needed() -> None:
    """
    Start backend and frontend servers if they're not already running.

    This is acceptable for manual E2E tests because:
    - They are marked with @pytest.mark.manual
    - They are skipped by default in CI
    - They require explicit -m manual flag to run

    Raises:
        RuntimeError: If servers cannot be started or become healthy
    """
    import subprocess
    import time

    print("[E2E] Checking if servers are running...")

    backend_healthy = check_server_health(BACKEND_URL)
    frontend_accessible = check_server_health(FRONTEND_URL.replace(":3000", ":3000"))

    if backend_healthy and frontend_accessible:
        print(f"[E2E] ✓ Backend healthy at {BACKEND_URL}")
        print(f"[E2E] ✓ Frontend accessible at {FRONTEND_URL}")
        return

    print("[E2E] Servers not running, starting them...")

    # Find start script
    start_script = REPO_ROOT / "scripts" / "start-all.bat"
    if not start_script.exists():
        start_script = REPO_ROOT / "scripts" / "start-all.sh"

    if not start_script.exists():
        raise RuntimeError(
            f"Cannot find start script at {REPO_ROOT / 'scripts' / 'start-all.bat'} or .sh. "
            "Please start servers manually."
        )

    # Start servers in background
    print(f"[E2E] Executing: {start_script}")
    subprocess.Popen([str(start_script)], shell=True, cwd=str(REPO_ROOT))

    # Wait for servers to become healthy
    print("[E2E] Waiting for servers to start (max 60 seconds)...")
    max_wait = 60
    check_interval = 3

    for elapsed in range(0, max_wait, check_interval):
        time.sleep(check_interval)

        backend_healthy = check_server_health(BACKEND_URL)
        if backend_healthy:
            print(f"[E2E] ✓ Backend healthy at {BACKEND_URL} (after {elapsed + check_interval}s)")
            # Give frontend a bit more time
            time.sleep(5)
            return

        print(f"[E2E] Waiting... ({elapsed + check_interval}s)")

    raise RuntimeError(
        f"Servers did not become healthy within {max_wait} seconds. " f"Check that {start_script} works correctly."
    )

"""
E2E Smoke Test Configuration

This conftest ensures E2E tests run against REAL servers, not mocks.
It disables test mode to prevent RESPX from intercepting HTTP requests.
"""

import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def disable_test_mode():
    """Disable test mode for E2E tests to use real HTTP requests."""
    # Remove TESTING flag if it was set by parent conftest
    os.environ.pop("TESTING", None)

    # Ensure we're not in test mode
    os.environ["TESTING"] = "0"

    yield

    # Cleanup
    os.environ.pop("TESTING", None)

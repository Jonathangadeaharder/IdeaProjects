"""Simple synchronous test to debug the test infrastructure."""
import pytest
from fastapi.testclient import TestClient
from core.app import create_app

def test_simple_app_creation():
    """Test that the app can be created."""
    app = create_app()
    assert app is not None

def test_simple_http_request():
    """Test a simple HTTP request."""
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/auth/me")
    assert response.status_code == 401  # Should be unauthorized

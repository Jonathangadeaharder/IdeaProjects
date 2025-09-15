"""In-process tests for debug endpoints using httpx async client fixture."""

from datetime import datetime
import pytest


@pytest.mark.anyio
async def test_debug_frontend_logs(async_client):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "category": "Test",
        "message": "Test log from direct API call",
        "data": {"test": True},
        "url": "http://localhost:3000/test",
        "userAgent": "TestScript/1.0",
    }
    r = await async_client.post("/api/debug/frontend-logs", json=log_entry)
    assert r.status_code == 200
    assert r.json().get("success") is True


@pytest.mark.anyio
async def test_debug_health(async_client):
    r = await async_client.get("/api/debug/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"

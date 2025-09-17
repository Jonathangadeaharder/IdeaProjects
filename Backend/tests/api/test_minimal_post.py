"""In-process tests for minimal debug endpoints using httpx async client fixture."""


import pytest


@pytest.mark.asyncio
async def test_minimal_post(async_client):
    r = await async_client.post("/api/debug/test-minimal", json={})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_with_data_post(async_client):
    payload = {"test": "value", "number": 123}
    r = await async_client.post("/api/debug/test-with-data", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["received_data"] == payload


@pytest.mark.asyncio
async def test_debug_health(async_client):
    r = await async_client.get("/api/debug/health")
    assert r.status_code == 200

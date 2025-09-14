"""In-process tests for minimal debug endpoints using httpx async client fixture."""


import pytest


@pytest.mark.anyio
async def test_minimal_post(async_client):
    r = await async_client.post("/debug/test-minimal", json={})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"


@pytest.mark.anyio
async def test_with_data_post(async_client):
    payload = {"test": "value", "number": 123}
    r = await async_client.post("/debug/test-with-data", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["received_data"] == payload


@pytest.mark.anyio
async def test_debug_health(async_client):
    r = await async_client.get("/debug/health")
    assert r.status_code == 200

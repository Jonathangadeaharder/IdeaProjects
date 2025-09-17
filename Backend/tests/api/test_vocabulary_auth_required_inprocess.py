"""
In-process tests to ensure vocabulary endpoints require Authorization.
"""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_vocabulary_requires_auth_stats(async_client):
    r = await async_client.get("/vocabulary/library/stats")
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_vocabulary_requires_auth_level(async_client):
    r = await async_client.get("/vocabulary/library/A1")
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_vocabulary_requires_auth_mark_known(async_client):
    r = await async_client.post("/vocabulary/mark-known", json={"word": "sein", "known": True})
    assert r.status_code == 403


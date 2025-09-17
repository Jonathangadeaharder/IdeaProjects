"""
Validation error tests for several endpoints to ensure 422 handling.
"""
from __future__ import annotations

import pytest


@pytest.fixture()
def auth_header():
    return {"Authorization": "Bearer test_token"}


@pytest.mark.asyncio
async def test_mark_known_missing_fields(async_client, auth_header):
    # Missing required fields -> 422
    r = await async_client.post("/vocabulary/mark-known", json={}, headers=auth_header)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_bulk_mark_missing_fields(async_client, auth_header):
    r = await async_client.post("/vocabulary/library/bulk-mark", json={}, headers=auth_header)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_translate_subtitles_missing_fields(async_client, auth_header):
    r = await async_client.post("/api/process/translate-subtitles", json={}, headers=auth_header)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_filter_subtitles_missing_fields(async_client, auth_header):
    r = await async_client.post("/api/process/filter-subtitles", json={}, headers=auth_header)
    assert r.status_code == 422


"""
Focused tests for vocabulary routes to raise API coverage.
Uses dynamic URL generation for maintainable testing.
"""
from __future__ import annotations

from pathlib import Path
import pytest


@pytest.fixture()
def auth_header():
    return {"Authorization": "Bearer test_token"}


def _set_videos_path(monkeypatch, module, tmp_path: Path):
    monkeypatch.setattr(type(module.settings), "get_videos_path", lambda self: tmp_path)


def get_url(async_client, route_name: str, **path_params):
    """Helper to generate URLs dynamically using FastAPI's url_path_for"""
    return async_client.app.url_path_for(route_name, **path_params)


@pytest.mark.asyncio
async def test_mark_known_toggle(async_client, auth_header):
    # Mark a word known; the service ensures the word exists.
    url = get_url(async_client, "mark_word_known")
    r = await async_client.post(
        url,
        json={"word": "sein", "known": True},
        headers=auth_header,
    )
    assert r.status_code == 200
    assert r.json().get("success") is True or r.json().get("status") in ("ok", True)


@pytest.mark.asyncio
async def test_blocking_words_with_existing_srt(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import vocabulary as vocab
    _set_videos_path(monkeypatch, vocab, tmp_path)

    # Prepare video and srt
    (tmp_path / "vid.mp4").write_bytes(b"x")
    (tmp_path / "vid.srt").write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nHallo Welt\n\n",
        encoding="utf-8",
    )

    url = get_url(async_client, "get_blocking_words")
    r = await async_client.get(
        url,
        params={"video_path": "vid.mp4", "segment_start": 0, "segment_duration": 60},
        headers=auth_header,
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("blocking_words"), list)
    # list can be empty or contain words depending on mock, but key should exist


@pytest.mark.asyncio
async def test_preload_requires_admin(async_client, auth_header):
    # Default mock user is not admin -> 403
    url = get_url(async_client, "preload_vocabulary")
    r = await async_client.post(url, headers=auth_header)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_vocabulary_level_invalid(async_client, auth_header):
    url = get_url(async_client, "get_vocabulary_level", level="Z9")
    r = await async_client.get(url, headers=auth_header)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_bulk_mark_invalid_level(async_client, auth_header):
    url = get_url(async_client, "bulk_mark_level")
    r = await async_client.post(
        url,
        json={"level": "Z9", "known": True},
        headers=auth_header,
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_bulk_mark_success(async_client, auth_header):
    """Test bulk marking words as known - focuses on API contract, not implementation"""
    url = get_url(async_client, "bulk_mark_level")
    r = await async_client.post(
        url,
        json={"level": "A1", "known": True},
        headers=auth_header,
    )
    assert r.status_code == 200
    data = r.json()
    assert "success" in data
    assert "word_count" in data
    assert isinstance(data.get("word_count"), int)


@pytest.mark.asyncio
async def test_stats_detailed(async_client, auth_header):
    """Test vocabulary stats endpoint - focuses on API contract structure"""
    url = get_url(async_client, "get_library_stats")
    r = await async_client.get(url, headers=auth_header)
    assert r.status_code == 200
    data = r.json()
    
    # Verify expected structure without hardcoded values
    assert "levels" in data
    assert "total_words" in data
    assert "total_known" in data
    assert isinstance(data["total_words"], int)
    assert isinstance(data["total_known"], int)
    
    # If levels exist, verify their structure
    if data["levels"]:
        for level_name, level_data in data["levels"].items():
            assert "total_words" in level_data
            assert isinstance(level_data["total_words"], int)

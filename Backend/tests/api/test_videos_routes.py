"""
Focused tests for videos routes to improve API coverage.
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
async def test_list_videos_with_file(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)

    # Create a sample video file
    (tmp_path / "Sample Episode.mp4").write_bytes(b"mp4data")

    url = get_url(async_client, "get_videos")
    r = await async_client.get(url, headers=auth_header)
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list) and len(items) >= 1
    assert any(isinstance(i.get("has_subtitles"), bool) for i in items)


@pytest.mark.asyncio
async def test_get_subtitles_route(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)

    # Prepare a subtitle file
    (tmp_path / "example.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nHello\n\n", encoding="utf-8")

    url = get_url(async_client, "get_subtitles", subtitle_path="example.srt")
    r = await async_client.get(url, headers=auth_header)
    assert r.status_code == 200
    assert "Hello" in r.text


@pytest.mark.asyncio
async def test_list_videos_when_path_missing(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    # Point to a directory that does not exist
    missing = tmp_path / "does_not_exist"
    monkeypatch.setattr(type(vids.settings), "get_videos_path", lambda self: missing)
    url = get_url(async_client, "get_videos")
    r = await async_client.get(url, headers=auth_header)
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_subtitles_windows_path_without_videos_dir(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    monkeypatch.setattr(type(vids.settings), "get_videos_path", lambda self: tmp_path)
    # Create file in root
    (tmp_path / "sample.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nX\n\n", encoding="utf-8")
    # Path that lacks a 'videos' component triggers fallback to basename
    win_path = r"C:\\elsewhere\\notvideos\\sample.srt"
    url = get_url(async_client, "get_subtitles", subtitle_path=win_path)
    r = await async_client.get(url, headers=auth_header)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_stream_video_match(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)

    # Create series directory and video
    series_dir = tmp_path / "Default"
    series_dir.mkdir(parents=True, exist_ok=True)
    (series_dir / "Episode 1.mp4").write_bytes(b"data")

    url = get_url(async_client, "stream_video", series="Default", episode="1")
    r = await async_client.get(url, headers=auth_header)
    assert r.status_code in (200, 206)  # streaming
    assert r.headers.get("Accept-Ranges") == "bytes"


@pytest.mark.asyncio
async def test_stream_video_partial_range_best_effort(async_client, monkeypatch, tmp_path: Path, auth_header):
    """If Range is sent, server may reply 206 or 200; ensure header and body exist."""
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)

    series_dir = tmp_path / "Default"
    series_dir.mkdir(parents=True, exist_ok=True)
    # small file
    (series_dir / "Episode 2.mp4").write_bytes(b"0123456789")

    url = get_url(async_client, "stream_video", series="Default", episode="2")
    r = await async_client.get(
        url,
        headers={**auth_header, "Range": "bytes=0-0"},
    )
    assert r.status_code in (200, 206)
    assert r.headers.get("Accept-Ranges") == "bytes"
    assert r.headers.get("content-type", "").startswith("video/")
    assert len(r.content) >= 1

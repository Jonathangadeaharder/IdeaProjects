"""
Test processing routes using dynamic URL generation
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
async def test_chunk_start_success(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import processing as proc
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    _set_videos_path(monkeypatch, proc, tmp_path)

    # Create a small video file
    (tmp_path / "clip.mp4").write_bytes(b"x")

    url = get_url(async_client, "process_chunk")
    r = await async_client.post(
        url,
        json={"video_path": "clip.mp4", "start_time": 0, "end_time": 5},
        headers=auth_header,
    )
    assert r.status_code == 200
    assert "task_id" in r.json()


@pytest.mark.asyncio
async def test_chunk_invalid_times(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import processing as proc
    _set_videos_path(monkeypatch, proc, tmp_path)

    # Create a small video file
    (tmp_path / "clip.mp4").write_bytes(b"x")

    # end_time <= start_time -> 400
    url = get_url(async_client, "process_chunk")
    r = await async_client.post(
        url,
        json={"video_path": "clip.mp4", "start_time": 5, "end_time": 5},
        headers=auth_header,
    )
    assert r.status_code == 400

    # negative start_time -> 400
    r2 = await async_client.post(
        url,
        json={"video_path": "clip.mp4", "start_time": -1, "end_time": 5},
        headers=auth_header,
    )
    assert r2.status_code == 400


@pytest.mark.asyncio
async def test_chunk_missing_file(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import processing as proc
    _set_videos_path(monkeypatch, proc, tmp_path)

    url = get_url(async_client, "process_chunk")
    r = await async_client.post(
        url,
        json={"video_path": "missing.mp4", "start_time": 0, "end_time": 5},
        headers=auth_header,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_transcribe_service_unavailable(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import processing as proc
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    _set_videos_path(monkeypatch, proc, tmp_path)

    # Create a small video file
    (tmp_path / "clip.mp4").write_bytes(b"x")

    # Force transcription service unavailable
    monkeypatch.setattr(proc, "get_transcription_service", lambda: None)

    url = get_url(async_client, "transcribe_video")
    r = await async_client.post(
        url,
        json={"video_path": "clip.mp4"},
        headers=auth_header,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_progress_not_found(async_client, auth_header):
    url = get_url(async_client, "get_task_progress", task_id="does-not-exist")
    r = await async_client.get(url, headers=auth_header)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_prepare_episode_missing_file(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import processing as proc
    _set_videos_path(monkeypatch, proc, tmp_path)

    url = get_url(async_client, "prepare_episode")
    r = await async_client.post(
        url,
        json={"video_path": "nope.mp4"},
        headers=auth_header,
    )
    assert r.status_code == 404

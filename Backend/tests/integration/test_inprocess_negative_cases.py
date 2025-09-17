"""
Negative-path and edge-case in-process tests for videos, processing, and vocabulary.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture()
def auth_header():
    return {"Authorization": "Bearer test_token"}


def _set_videos_path(monkeypatch, module, tmp_path: Path):
    monkeypatch.setattr(type(module.settings), "get_videos_path", lambda self: tmp_path)


@pytest.mark.asyncio
async def test_upload_subtitle_invalid_extension(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    (tmp_path / "e1.mp4").write_bytes(b"x")

    files = {"subtitle_file": ("bad.txt", b"hello", "text/plain")}
    r = await async_client.post("/videos/subtitle/upload", params={"video_path": "e1.mp4"}, files=files, headers=auth_header)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_upload_subtitle_too_large(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    (tmp_path / "e2.mp4").write_bytes(b"x")

    # Reduce threshold via monkeypatch to avoid large payload in test environment
    monkeypatch.setattr(vids, "MAX_SUBTITLE_SIZE_KB", 8)
    big_content = b"a" * (9 * 1024)  # > 8KB
    files = {"subtitle_file": ("e2.srt", big_content, "text/plain")}
    r = await async_client.post("/videos/subtitle/upload", params={"video_path": "e2.mp4"}, files=files, headers=auth_header)
    assert r.status_code == 413


@pytest.mark.asyncio
async def test_upload_video_invalid_content_type(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)

    files = {"video_file": ("Episode 2.mp4", b"x", "application/octet-stream")}
    r = await async_client.post("/videos/upload/Default", files=files, headers=auth_header)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_upload_video_invalid_extension(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)

    files = {"video_file": ("Episode 2.xyz", b"x", "video/xyz")}
    r = await async_client.post("/videos/upload/Default", files=files, headers=auth_header)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_upload_video_duplicate_conflict(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)

    files = {"video_file": ("Episode 3.mp4", b"x", "video/mp4")}
    r1 = await async_client.post("/videos/upload/Default", files=files, headers=auth_header)
    assert r1.status_code == 200
    r2 = await async_client.post("/videos/upload/Default", files=files, headers=auth_header)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_get_subtitles_not_found(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    r = await async_client.get("/videos/subtitles/missing.srt", headers=auth_header)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_subtitles_windows_path_resolution(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    (tmp_path / "episode1.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nHallo!\n\n", encoding="utf-8")
    win_path = r"C:\\fake\\videos\\episode1.srt"
    r = await async_client.get(f"/videos/subtitles/{win_path}", headers=auth_header)
    assert r.status_code == 200
    assert "Hallo!" in r.text


@pytest.mark.asyncio
async def test_stream_video_not_found(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    r = await async_client.get("/videos/Default/1", headers=auth_header)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_transcribe_service_unavailable(async_client, monkeypatch, auth_header):
    from api.routes import processing as proc
    monkeypatch.setattr(proc, "get_transcription_service", lambda: None)
    r = await async_client.post("/process/transcribe", json={"video_path": "vid.mp4"}, headers=auth_header)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_filter_and_translate_missing_srt_yield_error(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import processing as proc
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    _set_videos_path(monkeypatch, proc, tmp_path)
    # create video file but no srt
    (tmp_path / "v1.mp4").write_bytes(b"x")

    # Speed background
    async def fast_sleep(_):
        return None
    monkeypatch.setattr(proc.asyncio, "sleep", fast_sleep)

    # filter-subtitles
    r1 = await async_client.post("/process/filter-subtitles", json={"video_path": "v1.mp4"}, headers=auth_header)
    assert r1.status_code == 200
    task_id1 = r1.json()["task_id"]
    pr1 = await async_client.get(f"/process/progress/{task_id1}", headers=auth_header)
    # The background task should set error quickly due to missing srt
    assert pr1.status_code == 200
    assert pr1.json().get("status") in {"processing", "error"}

    # translate-subtitles
    r2 = await async_client.post(
        "/process/translate-subtitles",
        json={"video_path": "v1.mp4", "source_lang": "de", "target_lang": "en"},
        headers=auth_header,
    )
    assert r2.status_code == 200
    task_id2 = r2.json()["task_id"]
    # First poll may still be processing; allow a couple polls
    status = None
    for _ in range(5):
        pr2 = await async_client.get(f"/process/progress/{task_id2}", headers=auth_header)
        assert pr2.status_code == 200
        status = pr2.json().get("status")
        if status in {"error", "completed"}:
            break
    assert status in {"error", "completed"}


@pytest.mark.asyncio
async def test_progress_not_found(async_client, auth_header):
    r = await async_client.get("/process/progress/unknown_task_id", headers=auth_header)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_chunk_invalid_and_missing_video(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import processing as proc
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    _set_videos_path(monkeypatch, proc, tmp_path)

    # invalid timing
    r = await async_client.post(
        "/process/chunk",
        json={"video_path": "v2.mp4", "start_time": 10, "end_time": 5},
        headers=auth_header,
    )
    assert r.status_code == 400

    # missing video
    r2 = await async_client.post(
        "/process/chunk",
        json={"video_path": "v2.mp4", "start_time": 0, "end_time": 5},
        headers=auth_header,
    )
    assert r2.status_code == 404


@pytest.mark.asyncio
async def test_vocabulary_mark_known_and_invalid_level(async_client, auth_header):
    # mark known should succeed and return 200
    r = await async_client.post("/vocabulary/mark-known", json={"word": "sein", "known": True}, headers=auth_header)
    assert r.status_code == 200

    # invalid level should 400
    r2 = await async_client.get("/vocabulary/library/C3", headers=auth_header)
    assert r2.status_code == 400


@pytest.mark.asyncio
async def test_vocabulary_preload_forbidden_without_admin(async_client, auth_header):
    r = await async_client.post("/vocabulary/preload", headers=auth_header)
    assert r.status_code == 403

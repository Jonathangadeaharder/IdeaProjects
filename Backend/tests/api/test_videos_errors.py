"""
Additional error-path tests for videos endpoints at API level.
"""
from __future__ import annotations

from pathlib import Path
import pytest


@pytest.fixture()
def auth_header():
    return {"Authorization": "Bearer test_token"}


def _set_videos_path(monkeypatch, module, tmp_path: Path):
    monkeypatch.setattr(type(module.settings), "get_videos_path", lambda self: tmp_path)


@pytest.mark.asyncio
async def test_subtitles_404(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    r = await async_client.get("/videos/subtitles/missing.srt", headers=auth_header)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_upload_invalid_extension_api(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    (tmp_path / "v.mp4").write_bytes(b"x")
    files = {"subtitle_file": ("bad.txt", b"x", "text/plain")}
    r = await async_client.post("/videos/subtitle/upload", params={"video_path": "v.mp4"}, files=files, headers=auth_header)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_upload_video_invalid_content_type_api(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    files = {"video_file": ("Episode 2.mp4", b"x", "application/octet-stream")}
    r = await async_client.post("/videos/upload/Default", files=files, headers=auth_header)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_stream_video_unknown_series(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)

    r = await async_client.get("/videos/Nope/1", headers=auth_header)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_upload_subtitle_missing_video(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)

    files = {"subtitle_file": ("episode1.srt", b"1\n00:00\nHi\n", "text/plain")}
    r = await async_client.post(
        "/videos/subtitle/upload",
        params={"video_path": "episode1.mp4"},
        files=files,
        headers=auth_header,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_upload_subtitle_too_large(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    from core.constants import MAX_SUBTITLE_SIZE_KB
    _set_videos_path(monkeypatch, vids, tmp_path)

    # Need a video to pass existence check, but any .mp4 will do
    (tmp_path / "e1.mp4").write_bytes(b"x")

    too_big = b"x" * ((MAX_SUBTITLE_SIZE_KB + 1) * 1024)
    files = {"subtitle_file": ("e1.srt", too_big, "text/plain")}
    r = await async_client.post(
        "/videos/subtitle/upload",
        params={"video_path": "e1.mp4"},
        files=files,
        headers=auth_header,
    )
    assert r.status_code == 413


@pytest.mark.asyncio
async def test_upload_video_conflict(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)

    files = {"video_file": ("Episode 9.mp4", b"x", "video/mp4")}
    r1 = await async_client.post("/videos/upload/Default", files=files, headers=auth_header)
    assert r1.status_code == 200
    # Second upload with same name should conflict
    files2 = {"video_file": ("Episode 9.mp4", b"x", "video/mp4")}
    r2 = await async_client.post("/videos/upload/Default", files=files2, headers=auth_header)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_upload_video_invalid_extension(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)

    files = {"video_file": ("Episode 10.txt", b"x", "video/mp4")}
    r = await async_client.post("/videos/upload/Default", files=files, headers=auth_header)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_upload_video_empty_filename(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)

    # Simulate empty filename
    files = {"video_file": ("", b"x", "video/mp4")}
    r = await async_client.post("/videos/upload/Default", files=files, headers=auth_header)
    assert r.status_code in (400, 422)

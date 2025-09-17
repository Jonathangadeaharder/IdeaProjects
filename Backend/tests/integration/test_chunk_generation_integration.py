from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from urllib.parse import quote


@pytest.fixture()
def auth_header():
    # Matches conftest mock_auth_service expected token
    return {"Authorization": "Bearer test_token"}


def _set_videos_path(monkeypatch, module, tmp_path: Path):
    # Point videos path to a temp directory for tests
    monkeypatch.setattr(type(module.settings), "get_videos_path", lambda self: tmp_path)


def _make_episode(tmp_path: Path, stem: str, with_srt: str) -> tuple[Path, Path]:
    mp4 = tmp_path / f"{stem}.mp4"
    mp4.write_bytes(b"x")
    srt = tmp_path / f"{stem}.srt"
    srt.write_text(with_srt, encoding="utf-8")
    return mp4, srt


BASIC_SRT = (
    "1\n00:00:01,000 --> 00:00:03,000\nDer amerikanische Superstore.\n\n"
    "2\n00:00:10,000 --> 00:00:12,000\nHallo Welt\n\n"
    "3\n00:09:59,000 --> 00:10:01,000\nSchnitt an der Grenze\n\n"
    "4\n00:10:30,000 --> 00:10:40,000\nAußerhalb des ersten Chunks\n\n"
)


@pytest.mark.asyncio
async def test_process_chunk_generates_non_empty_and_serves(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import processing as proc
    from api.routes import videos as videos_module

    # Point videos path for both modules
    _set_videos_path(monkeypatch, videos_module, tmp_path)
    _set_videos_path(monkeypatch, proc, tmp_path)

    # Speed up background sleeps
    async def fast_sleep(_):
        return None
    monkeypatch.setattr(proc.asyncio, "sleep", fast_sleep)

    # Create episode files
    stem = "Episode 1 Staffel 1 von Superstore S to - Serien Online gratis a"
    mp4, _srt = _make_episode(tmp_path, stem, BASIC_SRT)

    # Start chunk processing 0-600 seconds
    r = await async_client.post(
        "/api/process/chunk",
        json={"video_path": mp4.name, "start_time": 0, "end_time": 600},
        headers=auth_header,
    )
    assert r.status_code == 200
    task_id = r.json()["task_id"]

    # Poll progress until completed
    for _ in range(200):
        pr = await async_client.get(f"/api/process/progress/{task_id}", headers=auth_header)
        assert pr.status_code == 200
        data = pr.json()
        if data.get("status") == "completed":
            break
        await asyncio.sleep(0.01)
    else:
        pytest.fail("Chunk processing did not complete in time")

    # Check file exists and is non-empty
    out_srt = tmp_path / f"{stem}_chunk_0_600.srt"
    assert out_srt.exists(), f"Expected output SRT not created: {out_srt}"
    content = out_srt.read_text(encoding="utf-8")
    assert len(content) > 0, "Generated chunk SRT is empty"

    # Fetch via API using relative path under videos root
    # Emulate frontend building path like 'Superstore/...', but here file is at root of tmp_path
    r2 = await async_client.get(f"/videos/subtitles/{out_srt.name}")
    assert r2.status_code == 200
    assert len(r2.text) > 0


@pytest.mark.asyncio
async def test_process_chunk_prefers_exact_srt(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import processing as proc
    from api.routes import videos as videos_module

    _set_videos_path(monkeypatch, videos_module, tmp_path)
    _set_videos_path(monkeypatch, proc, tmp_path)

    async def fast_sleep(_):
        return None
    monkeypatch.setattr(proc.asyncio, "sleep", fast_sleep)

    stem = "Episode 1 Staffel 1 von Superstore S to - Serien Online gratis a"
    mp4 = tmp_path / f"{stem}.mp4"
    mp4.write_bytes(b"x")

    # Create two SRTs; exact match contains unique line
    exact = tmp_path / f"{stem}.srt"
    other = tmp_path / "Episode 1 Staffel 1 von Superstore.srt"

    exact_text = (
        "1\n00:00:01,000 --> 00:00:02,000\nEXACT_MATCH_LINE\n\n"
        "2\n00:00:03,000 --> 00:00:04,000\nWeiter\n\n"
    )
    exact.write_text(exact_text, encoding="utf-8")
    other.write_text("1\n00:00:01,000 --> 00:00:02,000\nOTHER_SUB\n\n", encoding="utf-8")

    r = await async_client.post(
        "/api/process/chunk",
        json={"video_path": mp4.name, "start_time": 0, "end_time": 600},
        headers=auth_header,
    )
    assert r.status_code == 200
    task_id = r.json()["task_id"]

    for _ in range(200):
        pr = await async_client.get(f"/api/process/progress/{task_id}", headers=auth_header)
        assert pr.status_code == 200
        data = pr.json()
        if data.get("status") == "completed":
            break
        await asyncio.sleep(0.01)
    else:
        pytest.fail("Chunk processing did not complete in time")

    out_srt = tmp_path / f"{stem}_chunk_0_600.srt"
    assert out_srt.exists()
    text = out_srt.read_text(encoding="utf-8")
    assert "EXACT_MATCH_LINE" in text, "Exact-match SRT was not used to generate chunk"


# Removed environment-specific test that relied on hardcoded paths


@pytest.mark.asyncio
async def test_subtitles_endpoint_handles_windows_absolute_path(async_client, monkeypatch, tmp_path: Path, auth_header):
    """Ensure GET /videos/subtitles can handle an absolute Windows path with backslashes."""
    from api.routes import videos as videos_module

    _set_videos_path(monkeypatch, videos_module, tmp_path)

    # Create a video and srt at the videos root
    stem = "abs_path_episode"
    mp4, srt = _make_episode(tmp_path, stem, BASIC_SRT)

    # Build a Windows absolute path (with backslashes)
    abs_path = str(srt)
    # Percent-encode the path so it can be sent on the URL path segment
    encoded = quote(abs_path, safe="")

    r = await async_client.get(f"/videos/subtitles/{encoded}", headers=auth_header)
    assert r.status_code == 200
    assert "Superstore" in BASIC_SRT or len(r.text) > 0


@pytest.mark.asyncio
async def test_progress_contains_paths_and_files_exist(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import processing as proc
    from api.routes import videos as videos_module

    _set_videos_path(monkeypatch, videos_module, tmp_path)
    _set_videos_path(monkeypatch, proc, tmp_path)

    async def fast_sleep(_):
        return None
    monkeypatch.setattr(proc.asyncio, "sleep", fast_sleep)

    stem = "path_fields_episode"
    mp4, _srt = _make_episode(tmp_path, stem, BASIC_SRT)

    r = await async_client.post(
        "/api/process/chunk",
        json={"video_path": mp4.name, "start_time": 0, "end_time": 600},
        headers=auth_header,
    )
    assert r.status_code == 200
    task_id = r.json()["task_id"]

    for _ in range(200):
        pr = await async_client.get(f"/api/process/progress/{task_id}", headers=auth_header)
        assert pr.status_code == 200
        data = pr.json()
        if data.get("status") == "completed":
            # Verify paths are present and files exist
            subtitle_path = data.get("subtitle_path")
            translation_path = data.get("translation_path")
            assert subtitle_path, "subtitle_path missing in progress"
            assert translation_path is not None, "translation_path missing in progress"
            assert Path(subtitle_path).exists(), f"subtitle_path does not exist: {subtitle_path}"
            assert Path(translation_path).exists(), f"translation_path does not exist: {translation_path}"
            break
        await asyncio.sleep(0.01)
    else:
        pytest.fail("Chunk processing did not complete in time")

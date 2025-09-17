"""
Test negative paths for processing routes using dynamic URL generation
"""
from __future__ import annotations

import asyncio
from pathlib import Path
import pytest


def _set_videos_path(monkeypatch, module, tmp_path: Path):
    monkeypatch.setattr(type(module.settings), "get_videos_path", lambda self: tmp_path)


def get_url(async_client, route_name: str, **path_params):
    """Helper to generate URLs dynamically using FastAPI's url_path_for"""
    return async_client.app.url_path_for(route_name, **path_params)


@pytest.mark.asyncio
async def test_full_pipeline_missing_param(async_client, auth_headers):
    # Missing required query param -> 422 from validation
    url = get_url(async_client, "full_pipeline")
    r = await async_client.post(url, headers=auth_headers)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_transcribe_missing_file(async_client, monkeypatch, tmp_path: Path, auth_headers):
    from api.routes import processing as proc
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    _set_videos_path(monkeypatch, proc, tmp_path)

    # Mock transcription service to return None (unavailable)
    monkeypatch.setattr(proc, "get_transcription_service", lambda: None)
    # Do NOT create file
    url = get_url(async_client, "transcribe_video")
    r = await async_client.post(url, json={"video_path": "ghost.mp4"}, headers=auth_headers)
    # Service unavailable returns 422, not 404
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_translate_missing_srt_sets_error(async_client, monkeypatch, tmp_path: Path, auth_headers):
    from api.routes import processing as proc
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    _set_videos_path(monkeypatch, proc, tmp_path)

    # Create video but not .srt
    (tmp_path / "v1.mp4").write_bytes(b"x")

    # Speed up sleeps in background
    async def fast_sleep(_):
        return None
    monkeypatch.setattr(proc.asyncio, "sleep", fast_sleep)

    # Mock translation service as available but will fail on missing SRT
    class MockTranslator:
        def __init__(self):
            self.is_initialized = True
        def initialize(self):
            self.is_initialized = True

    monkeypatch.setattr(proc, "get_translation_service", lambda: MockTranslator())

    url = get_url(async_client, "translate_subtitles")
    r = await async_client.post(
        url,
        json={"video_path": "v1.mp4", "source_lang": "de", "target_lang": "en"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    task_id = r.json()["task_id"]

    # Poll for error status
    for _ in range(50):
        progress_url = get_url(async_client, "get_task_progress", task_id=task_id)
        pr = await async_client.get(progress_url, headers=auth_headers)
        if pr.status_code == 200 and pr.json().get("status") == "error":
            break
        await asyncio.sleep(0.01)
    else:
        pytest.fail("Expected translation error not observed")


@pytest.mark.asyncio
async def test_filter_missing_srt_sets_error(async_client, monkeypatch, tmp_path: Path, auth_headers):
    from api.routes import processing as proc
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)
    _set_videos_path(monkeypatch, proc, tmp_path)

    # Ensure only .mp4 exists
    (tmp_path / "v2.mp4").write_bytes(b"x")

    # Mock subtitle processor to simulate missing SRT error
    class MockSubtitleProcessor:
        async def process_srt_file(self, srt_path: str, user_id: int):
            return {"ok": True}

    # Mock the subtitle processor dependency
    from core.dependencies import get_subtitle_processor
    monkeypatch.setattr("core.dependencies.get_subtitle_processor", lambda: MockSubtitleProcessor())
    
    url = get_url(async_client, "filter_subtitles")
    r = await async_client.post(
        url,
        json={"video_path": "v2.mp4"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    task_id = r.json()["task_id"]

    # Poll for error status
    for _ in range(50):
        progress_url = get_url(async_client, "get_task_progress", task_id=task_id)
        pr = await async_client.get(progress_url, headers=auth_headers)
        if pr.status_code == 200 and pr.json().get("status") == "error":
            break
        await asyncio.sleep(0.01)
    else:
        pytest.fail("Expected filtering error not observed")


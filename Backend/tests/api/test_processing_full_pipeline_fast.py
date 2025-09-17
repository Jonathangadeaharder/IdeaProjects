"""
Happy-path test for /process/full-pipeline using a fast fake background task.
"""
from __future__ import annotations

import asyncio
import pytest


@pytest.mark.asyncio
async def test_full_pipeline_fast(async_client, monkeypatch, auth_headers):
    from api.routes import processing as proc

    # Fast fake pipeline that immediately completes
    async def fake_pipeline(video_path_str: str, task_id: str, task_progress, user_id: int):
        task_progress[task_id] = proc.ProcessingStatus(
            status="completed",
            progress=100.0,
            current_step="done",
            message="ok",
        )

    monkeypatch.setattr(proc, "run_processing_pipeline", fake_pipeline)

    # Route expects a JSON body with FullPipelineRequest structure
    request_body = {
        "video_path": "any.mp4",
        "source_lang": "de",
        "target_lang": "en"
    }
    
    r = await async_client.post("/api/process/full-pipeline", json=request_body, headers=auth_headers)
    assert r.status_code == 200
    task_id = r.json()["task_id"]

    # Immediately completed by fake pipeline, but poll briefly to be safe
    # Use the correct API path with /api prefix
    for _ in range(10):
        pr = await async_client.get(f"/api/process/progress/{task_id}", headers=auth_headers)
        if pr.status_code == 200 and pr.json().get("status") == "completed":
            break
        await asyncio.sleep(0.01)
    else:
        pytest.fail("Full pipeline did not complete")


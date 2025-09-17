"""
Windows path handling for subtitles route.
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
async def test_windows_absolute_subtitle_path(async_client, monkeypatch, tmp_path: Path, auth_header):
    from api.routes import videos as vids
    _set_videos_path(monkeypatch, vids, tmp_path)

    (tmp_path / "example.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nHi!\n\n", encoding="utf-8")
    win_path = r"C:\\fake\\videos\\example.srt"

    r = await async_client.get(f"/videos/subtitles/{win_path}", headers=auth_header)
    assert r.status_code == 200
    assert "Hi!" in r.text


"""Integration tests for video processing endpoints."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from core.config import settings
from tests.helpers import AuthTestHelperAsync


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_Whenvideo_listingCalled_ThenReturnsempty_list(async_http_client, url_builder, monkeypatch, tmp_path):
    flow = await AuthTestHelperAsync.register_and_login_async(async_http_client)

    with patch.object(type(settings), "get_videos_path", return_value=tmp_path):
        response = await async_http_client.get(url_builder.url_for("get_videos"), headers=flow["headers"])

        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_stream_missing_video_returns_404(async_http_client, url_builder, monkeypatch, tmp_path):
    flow = await AuthTestHelperAsync.register_and_login_async(async_http_client)

    with patch.object(type(settings), "get_videos_path", return_value=tmp_path):
        response = await async_http_client.get(
            url_builder.url_for("stream_video", series="Default", episode="episode.mp4"), headers=flow["headers"]
        )

        assert response.status_code == 404

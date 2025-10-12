"""Integration tests for video processing endpoints."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from core.config import settings
from tests.helpers import AsyncAuthHelper


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenvideo_listingCalled_ThenReturnsempty_list(async_http_client, url_builder, monkeypatch, tmp_path):
    helper = AsyncAuthHelper(async_http_client)

    _user, _token, headers = await helper.create_authenticated_user()

    with patch.object(type(settings), "get_videos_path", return_value=tmp_path):
        response = await async_http_client.get(url_builder.url_for("get_videos"), headers=headers)

        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_stream_missing_video_returns_404(async_http_client, url_builder, monkeypatch, tmp_path):
    helper = AsyncAuthHelper(async_http_client)

    _user, _token, headers = await helper.create_authenticated_user()

    with patch.object(type(settings), "get_videos_path", return_value=tmp_path):
        response = await async_http_client.get(
            url_builder.url_for("stream_video", series="Default", episode="episode.mp4"), headers=headers
        )

        assert response.status_code == 404

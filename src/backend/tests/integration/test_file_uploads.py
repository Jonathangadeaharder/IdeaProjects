"""Integration tests for upload endpoints using the in-process client."""

from __future__ import annotations

import io

import pytest

from tests.helpers import AsyncAuthHelper


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whensubtitle_uploadWithnon_srt_ThenRejects(async_http_client, url_builder):
    """Invalid input: uploading a non-.srt file is rejected."""
    helper = AsyncAuthHelper(async_http_client)

    _user, _token, headers = await helper.create_authenticated_user()

    response = await async_http_client.post(
        url_builder.url_for("upload_subtitle"),
        headers=headers,
        files={"subtitle_file": ("notes.txt", b"not subtitle", "text/plain")},
        params={"video_path": "missing.mp4"},
    )

    # Invalid file type should return 400 (bad request)
    assert (
        response.status_code == 400
    ), f"Expected 400 (bad request for invalid file type), got {response.status_code}: {response.text}"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenvideo_uploadWithoutmp_ThenReturnsError4(async_http_client, url_builder):
    """Boundary: non-mp4 uploads return a validation error."""
    helper = AsyncAuthHelper(async_http_client)

    _user, _token, headers = await helper.create_authenticated_user()

    response = await async_http_client.post(
        url_builder.url_for("upload_video_to_series", series="series"),
        headers=headers,
        files={"video_file": ("clip.txt", io.BytesIO(b"content"), "text/plain")},
    )

    # Invalid file type should return 400 (bad request)
    assert (
        response.status_code == 400
    ), f"Expected 400 (bad request for invalid file type), got {response.status_code}: {response.text}"

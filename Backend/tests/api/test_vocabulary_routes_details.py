"""Detailed vocabulary route behavior under protective testing."""

from __future__ import annotations

import pytest

from tests.helpers import AsyncAuthHelper


async def _auth(async_client):
    helper = AsyncAuthHelper(async_client)
    return await helper.create_authenticated_user()


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_Whenmark_known_can_unmarkCalled_ThenSucceeds(async_client, url_builder):
    """Happy path: toggling known flag to False returns consistent structure."""
    _user, _token, headers = await _auth(async_client)

    response = await async_client.post(
        url_builder.url_for("mark_word_known"),
        json={"word": "sein", "known": False},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body.get("known") is False
    assert body.get("word") == "sein"


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_Whenbulk_markCalled_ThenReturnscounts(async_client, url_builder):
    """Happy path: bulk mark returns the number of affected words."""
    from unittest.mock import AsyncMock, patch

    from services.vocabulary.vocabulary_service import vocabulary_service

    # Mock the progress_service.bulk_mark_level method
    mock_bulk_mark = AsyncMock(return_value={"updated_count": 7})

    _user, _token, headers = await _auth(async_client)

    with patch.object(vocabulary_service.progress_service, "bulk_mark_level", mock_bulk_mark):
        response = await async_client.post(
            url_builder.url_for("bulk_mark_level"),
            json={"level": "A1", "known": True, "target_language": "de"},
            headers=headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["word_count"] == 7
    assert body["level"] == "A1"

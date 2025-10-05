"""Integration checks for vocabulary endpoints."""

from __future__ import annotations

from uuid import uuid4

import pytest

from tests.helpers import AsyncAuthHelper


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_Whenmark_known_endpointCalled_ThenSucceeds(async_client, url_builder):
    helper = AsyncAuthHelper(async_client)

    user, token, headers = await helper.create_authenticated_user()
    concept_id = str(uuid4())

    response = await async_client.post(
        url_builder.url_for("mark_word_known"),
        json={"concept_id": concept_id, "known": True},
        headers=headers,
    )

    assert response.status_code == 200


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_Whenlibrary_levelWithoutvalid_code_ThenReturnsError(async_client):
    helper = AsyncAuthHelper(async_client)

    user, token, headers = await helper.create_authenticated_user()

    response = await async_client.get("/api/vocabulary/library/Z9", params={"target_language": "de"}, headers=headers)

    # Invalid level parameter should return 422 (validation error)
    assert (
        response.status_code == 422
    ), f"Expected 422 (validation error for invalid level), got {response.status_code}: {response.text}"


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_Whenvocabulary_stats_endpointCalled_ThenReturnsMultilingualStats(async_client, url_builder):
    """Integration test for multilingual vocabulary stats endpoint."""
    helper = AsyncAuthHelper(async_client)

    user, token, headers = await helper.create_authenticated_user()

    response = await async_client.get(
        url_builder.url_for("get_vocabulary_stats"),
        params={"target_language": "de", "translation_language": "es"},
        headers=headers,
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    payload = response.json()
    assert "levels" in payload
    assert "target_language" in payload
    assert "total_words" in payload


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_Whenlanguages_endpointCalled_ThenReturnsLanguageList(async_client):
    """Integration test for supported languages endpoint."""
    helper = AsyncAuthHelper(async_client)

    user, token, headers = await helper.create_authenticated_user()

    response = await async_client.get(
        "/api/vocabulary/languages",
        headers=headers,
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    payload = response.json()
    assert "languages" in payload
    assert isinstance(payload["languages"], list)


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_Whenbulk_mark_endpointCalled_ThenSucceedsWithLanguage(async_client):
    """Integration test for multilingual bulk mark endpoint."""
    helper = AsyncAuthHelper(async_client)

    user, token, headers = await helper.create_authenticated_user()

    response = await async_client.post(
        "/api/vocabulary/library/bulk-mark",
        json={"level": "A1", "target_language": "de", "known": True},
        headers=headers,
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    payload = response.json()
    assert "success" in payload
    assert "level" in payload
    assert "word_count" in payload

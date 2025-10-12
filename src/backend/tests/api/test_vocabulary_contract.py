"""Vocabulary contract tests in line with the protective testing policy."""

from __future__ import annotations

import pytest

from tests.helpers import AsyncAuthHelper


async def _auth(async_client):
    helper = AsyncAuthHelper(async_client)
    _user, _token, headers = await helper.create_authenticated_user()
    return headers


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenmark_known_AcceptsValid_payloadCalled_ThenSucceeds(async_http_client, url_builder, seeded_vocabulary):
    """Happy path: mark-known stores the flag and returns success metadata."""
    headers = await _auth(async_http_client)

    # Get a real vocabulary word from the library (seeded_vocabulary fixture ensures data exists)
    library_response = await async_http_client.get(
        url_builder.url_for("get_vocabulary_level", level="A1"),
        params={"target_language": "de", "limit": 1},
        headers=headers,
    )
    assert library_response.status_code == 200, f"Failed to get vocabulary: {library_response.text}"
    words = library_response.json()["words"]

    # Fail fast if no words - this indicates a seeding failure
    assert len(words) > 0, "No vocabulary words found - seeding failed or vocabulary system is broken"

    # Use the first word's lemma
    word_lemma = words[0]["lemma"]

    response = await async_http_client.post(
        url_builder.url_for("mark_word_known"),
        json={"word": word_lemma, "language": "de", "known": True},
        headers=headers,
    )

    assert response.status_code == 200, f"Failed to mark word as known: {response.text}"
    body = response.json()
    assert any(key in body for key in ("success", "message", "status"))


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenmark_knownWithoutconcept_id_ThenReturnsError(async_http_client, url_builder):
    """Invalid input: missing concept_id causes internal error (TODO: should return 422)."""
    headers = await _auth(async_http_client)

    response = await async_http_client.post(
        url_builder.url_for("mark_word_known"),
        json={"known": True},
        headers=headers,
    )

    assert response.status_code == 500  # TODO: Should validate and return 422


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenvocabulary_statsCalled_ThenReturnsexpected_fields(async_http_client, url_builder):
    """Happy path: vocabulary stats returns aggregate fields with multilingual support."""
    headers = await _auth(async_http_client)

    response = await async_http_client.get(
        url_builder.url_for("get_vocabulary_stats"),
        params={"target_language": "de", "translation_language": "es"},
        headers=headers,
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    payload = response.json()
    assert any(key in payload for key in ("total_words", "total_known", "levels", "target_language"))


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenlibrary_levelWithoutvalid_code_ThenReturnsError(async_http_client, url_builder):
    """Boundary: requesting unknown level surfaces a 404 or 422 error."""
    headers = await _auth(async_http_client)

    response = await async_http_client.get(
        url_builder.url_for("get_vocabulary_level", level="invalid"), params={"target_language": "de"}, headers=headers
    )

    # Invalid level parameter should return 422 (validation error)
    assert (
        response.status_code == 422
    ), f"Expected 422 (validation error for invalid level), got {response.status_code}: {response.text}"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenlanguages_endpointCalled_ThenReturnsSupported_languages(async_http_client, url_builder):
    """Happy path: languages endpoint returns list of supported languages."""
    headers = await _auth(async_http_client)

    response = await async_http_client.get(
        url_builder.url_for("get_supported_languages"),
        headers=headers,
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    payload = response.json()
    assert "languages" in payload
    assert isinstance(payload["languages"], list)


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenbulk_mark_WithValid_level_ThenSucceeds(async_http_client, url_builder):
    """Happy path: bulk mark endpoint works with valid level and language."""
    headers = await _auth(async_http_client)

    response = await async_http_client.post(
        url_builder.url_for("bulk_mark_level"),
        json={"level": "A1", "target_language": "de", "known": True},
        headers=headers,
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    payload = response.json()
    assert any(key in payload for key in ("success", "level", "word_count"))


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenbulk_mark_WithInvalid_level_ThenReturnsError(async_http_client, url_builder):
    """Invalid input: bulk mark with invalid level returns validation error."""
    headers = await _auth(async_http_client)

    response = await async_http_client.post(
        url_builder.url_for("bulk_mark_level"),
        json={"level": "Z9", "target_language": "de", "known": True},
        headers=headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenmark_known_WithInvalid_uuid_ThenReturnsError(async_http_client, url_builder):
    """Invalid input: mark known with invalid UUID returns validation error."""
    headers = await _auth(async_http_client)

    response = await async_http_client.post(
        url_builder.url_for("mark_word_known"),
        json={"concept_id": "not-a-uuid", "known": True},
        headers=headers,
    )

    assert response.status_code == 422

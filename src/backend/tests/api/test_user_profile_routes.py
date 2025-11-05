"""User profile route tests following the CDD/TDD policies."""

from __future__ import annotations

import pytest

from tests.helpers import AsyncAuthHelper


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenget_profileCalled_ThenReturnsauthenticated_user(async_http_client, url_builder):
    """Happy path: /profile returns the authenticated user's public profile."""
    helper = AsyncAuthHelper(async_http_client)
    user, _token, headers = await helper.create_authenticated_user()
    profile_url = url_builder.url_for("profile_get")

    response = await async_http_client.get(profile_url, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user.username
    assert "id" in data
    assert data["language_runtime"]["native"] == "es"
    assert data["language_runtime"]["target"] == "de"
    assert data["language_runtime"]["translation_service"] in {"opus", "nllb"}


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenget_profileWithoutauthentication_ThenReturnsError(async_http_client, url_builder):
    """Invalid input: missing authorization header yields 401."""
    profile_url = url_builder.url_for("profile_get")

    response = await async_http_client.get(profile_url)

    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_WhenUpdateLanguagesAcceptsValidPayload_ThenSucceeds(async_http_client, url_builder):
    """Happy path: language update persists preferred codes."""
    helper = AsyncAuthHelper(async_http_client)
    _user, _token, headers = await helper.create_authenticated_user()
    languages_url = url_builder.url_for("profile_update_languages")

    response = await async_http_client.put(
        languages_url,
        json={"native_language": "es", "target_language": "de"},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["native_language"]["code"] == "es"
    assert body["target_language"]["code"] == "de"
    runtime = body["language_runtime"]
    assert runtime["native"] == "es"
    assert runtime["target"] == "de"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenupdate_languagesWithduplicate_codes_ThenRejects(async_http_client, url_builder):
    """Boundary: native and target languages must differ."""
    helper = AsyncAuthHelper(async_http_client)
    _user, _token, headers = await helper.create_authenticated_user()
    languages_url = url_builder.url_for("profile_update_languages")

    response = await async_http_client.put(
        languages_url,
        json={"native_language": "es", "target_language": "es"},
        headers=headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_WhenSupportedLanguagesListsKnownCodes_ThenSucceeds(async_http_client, url_builder):
    """Happy path: supported languages endpoint enumerates known codes."""
    languages_url = url_builder.url_for("profile_get_supported_languages")

    response = await async_http_client.get(languages_url)

    assert response.status_code == 200
    codes = response.json()
    assert "en" in codes and "de" in codes


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_WhenGetProfile_ThenIncludesChunkDuration(async_http_client, url_builder):
    """Happy path: profile includes chunk_duration_minutes field with default value."""
    helper = AsyncAuthHelper(async_http_client)
    _user, _token, headers = await helper.create_authenticated_user()
    profile_url = url_builder.url_for("profile_get")

    response = await async_http_client.get(profile_url, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "chunk_duration_minutes" in data
    assert data["chunk_duration_minutes"] == 20  # Default value


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_WhenUpdateSettingsWithValidChunkDuration_ThenSucceeds(async_http_client, url_builder):
    """Happy path: updating chunk duration with valid values (5, 10, 20) succeeds."""
    helper = AsyncAuthHelper(async_http_client)
    _user, _token, headers = await helper.create_authenticated_user()
    settings_url = url_builder.url_for("profile_update_settings")

    # Test each valid value
    for valid_duration in [5, 10, 20]:
        response = await async_http_client.put(
            settings_url,
            json={"chunk_duration_minutes": valid_duration},
            headers=headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["chunk_duration_minutes"] == valid_duration

        # Verify persistence by getting profile
        profile_response = await async_http_client.get(url_builder.url_for("profile_get"), headers=headers)
        assert profile_response.status_code == 200
        assert profile_response.json()["chunk_duration_minutes"] == valid_duration


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_WhenUpdateSettingsWithInvalidChunkDuration_ThenRejects(async_http_client, url_builder):
    """Boundary: chunk duration must be between 5 and 20 minutes."""
    helper = AsyncAuthHelper(async_http_client)
    _user, _token, headers = await helper.create_authenticated_user()
    settings_url = url_builder.url_for("profile_update_settings")

    # Test invalid values (below 5, above 20, negative)
    invalid_values = [3, 4, 21, 25, -1, 0, 100]

    for invalid_duration in invalid_values:
        response = await async_http_client.put(
            settings_url,
            json={"chunk_duration_minutes": invalid_duration},
            headers=headers,
        )

        # Should return 422 for validation error
        assert response.status_code == 422, (
            f"Expected 422 for chunk_duration={invalid_duration}, got {response.status_code}"
        )


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_WhenNewUserCreated_ThenDefaultChunkDurationIs20(async_http_client, url_builder):
    """Default value: newly created users have chunk_duration_minutes=20."""
    helper = AsyncAuthHelper(async_http_client)
    _user, _token, headers = await helper.create_authenticated_user()

    # Get settings immediately after user creation
    settings_url = url_builder.url_for("profile_get_settings")
    response = await async_http_client.get(settings_url, headers=headers)

    assert response.status_code == 200
    settings = response.json()
    assert settings["chunk_duration_minutes"] == 20

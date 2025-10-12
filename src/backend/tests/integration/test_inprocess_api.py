"""Minimal integration checks using the built-in async_client fixture."""

from __future__ import annotations

import pytest

from tests.helpers import AsyncAuthHelper


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenhealth_endpointCalled_ThenSucceeds(async_http_client, url_builder):
    response = await async_http_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenvocabulary_statsWithoutauth_ThenReturnsError(async_http_client, url_builder):
    response = await async_http_client.get(url_builder.url_for("get_vocabulary_stats"))
    assert response.status_code == 401

    helper = AsyncAuthHelper(async_http_client)

    _user, _token, headers = await helper.create_authenticated_user()
    authed = await async_http_client.get(url_builder.url_for("get_vocabulary_stats"), headers=headers)
    assert authed.status_code == 200, f"Expected 200, got {authed.status_code}: {authed.text}"

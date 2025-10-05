"""Validation error contract tests following the 80/20 guideline."""

from __future__ import annotations

import pytest

from tests.helpers import AsyncAuthHelper


@pytest.mark.anyio
@pytest.mark.timeout(30)
@pytest.mark.parametrize(
    "route_or_path",
    [
        "mark_word_known",
        "bulk_mark_level",
        "filter_subtitles",
    ],
)
async def test_WhenEndpointsRequireMandatoryFields_ThenValidates(async_http_client, url_builder, route_or_path: str):
    """Invalid input: missing mandatory fields results in 422 validation errors."""
    helper = AsyncAuthHelper(async_http_client)
    _user, _token, headers = await helper.create_authenticated_user()

    # Determine endpoint - use url_builder for route names, hardcoded path otherwise
    endpoint = url_builder.url_for(route_or_path) if not route_or_path.startswith("/") else route_or_path

    response = await async_http_client.post(endpoint, json={}, headers=headers)

    assert response.status_code == 422

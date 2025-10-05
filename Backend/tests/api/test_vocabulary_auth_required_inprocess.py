"""
In-process tests to ensure vocabulary endpoints require Authorization.
"""

from __future__ import annotations

import pytest


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenvocabularyWithoutauth_stats_ThenReturnsError(async_client, url_builder):
    r = await async_client.get(url_builder.url_for("get_vocabulary_stats"))
    assert r.status_code == 401


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenvocabularyWithoutauth_level_ThenReturnsError(async_client, url_builder):
    r = await async_client.get(url_builder.url_for("get_vocabulary_level", level="A1"))
    assert r.status_code == 401


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_WhenvocabularyWithoutauth_mark_known_ThenReturnsError(async_client, url_builder):
    r = await async_client.post(url_builder.url_for("mark_word_known"), json={"word": "sein", "known": True})
    assert r.status_code == 401

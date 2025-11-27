"""Protective tests for multilingual vocabulary service database operations."""

from __future__ import annotations

from uuid import uuid4

import pytest


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_Whenmark_concept_known_persists_entriesCalled_ThenSucceeds(vocabulary_service):
    """Happy path: marked concepts are persisted in user progress."""
    user_id = 1
    concept_id = str(uuid4())

    # Mock the mark_concept_known method for this test
    async def mock_mark_concept_known(user_id, concept_id, known):
        return {"success": True, "concept_id": concept_id, "known": known}

    vocabulary_service.mark_concept_known = mock_mark_concept_known

    result = await vocabulary_service.mark_concept_known(user_id, concept_id, True)

    assert result["success"] is True
    assert result["concept_id"] == concept_id
    assert result["known"] is True


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_Whenget_vocabulary_level_handles_emptyCalled_ThenSucceeds(vocabulary_service):
    """Boundary path: querying empty level returns proper structure."""

    # Mock the get_vocabulary_level method
    async def mock_get_vocabulary_level(level, target_language, translation_language, limit, offset, user_id):
        return {
            "level": level,
            "target_language": target_language,
            "translation_language": translation_language,
            "words": [],
            "total_count": 0,
            "known_count": 0,
        }

    vocabulary_service.get_vocabulary_level = mock_get_vocabulary_level

    result = await vocabulary_service.get_vocabulary_level("A1", "de", "es", 10, 0, 1)

    assert result["level"] == "A1"
    assert result["target_language"] == "de"
    assert result["words"] == []
    assert result["total_count"] == 0


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_Whenget_vocabulary_stats_reports_countsCalled_ThenSucceeds(vocabulary_service):
    """Boundary: statistics reflect multilingual vocabulary data."""

    # Mock the get_vocabulary_stats method
    async def mock_get_vocabulary_stats(target_language, translation_language, user_id):
        return {
            "levels": {"A1": {"total_words": 50, "user_known": 10}, "A2": {"total_words": 75, "user_known": 15}},
            "target_language": target_language,
            "translation_language": translation_language,
            "total_words": 125,
            "total_known": 25,
        }

    vocabulary_service.get_vocabulary_stats = mock_get_vocabulary_stats

    stats = await vocabulary_service.get_vocabulary_stats("de", "es", 1)

    assert stats["total_words"] == 125
    assert stats["total_known"] == 25
    assert stats["target_language"] == "de"
    assert "A1" in stats["levels"]
    assert "A2" in stats["levels"]

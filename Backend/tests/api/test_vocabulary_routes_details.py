"""
Additional vocabulary API tests to validate totals, defaults, and responses.
"""
from __future__ import annotations

import pytest


@pytest.fixture()
def auth_header():
    return {"Authorization": "Bearer test_token"}


@pytest.mark.asyncio
async def test_stats_totals_with_user_known(async_client, monkeypatch, auth_header):
    from api.routes import vocabulary as vocab

    class FakeService:
        def __init__(self, *_a, **_k):
            pass

        def get_vocabulary_stats(self):
            # Base totals per level
            return {
                "A1": {"total_words": 10},
                "A2": {"total_words": 20},
                "B1": {"total_words": 30},
                "B2": {"total_words": 40},
            }

        def get_user_known_words(self, user_id: int, level: str):
            return {"w1", "w2"} if level in {"A1", "A2"} else set()

    monkeypatch.setattr(vocab, "VocabularyPreloadService", FakeService)

    r = await async_client.get("/vocabulary/library/stats", headers=auth_header)
    assert r.status_code == 200
    data = r.json()
    assert data["total_words"] == 10 + 20 + 30 + 40
    # user_known counts should be present; total_known sums of per-level counts
    assert data["total_known"] == 2 + 2 + 0 + 0
    assert data["levels"]["A1"]["user_known"] == 2


@pytest.mark.asyncio
async def test_level_structure_defaults(async_client, monkeypatch, auth_header):
    from api.routes import vocabulary as vocab

    class FakeService:
        def __init__(self, *_a, **_k):
            pass

        def get_level_words(self, level: str):
            # Missing difficulty and part_of_speech should get defaults
            return [
                {"id": 1, "word": "sein"},
                {"id": 2, "word": "haben", "difficulty_level": level},
            ]

        def get_user_known_words(self, user_id: int, level: str):
            return {"sein"}

    monkeypatch.setattr(vocab, "VocabularyPreloadService", FakeService)

    r = await async_client.get("/vocabulary/library/A2", headers=auth_header)
    assert r.status_code == 200
    body = r.json()
    assert body["level"] == "A2"
    assert body["known_count"] == 1
    # Defaults applied
    words = body["words"]
    w1 = next(w for w in words if w["word"] == "sein")
    assert w1["difficulty_level"] == "A2"
    assert w1["part_of_speech"] == "noun"


@pytest.mark.asyncio
async def test_bulk_mark_response_fields(async_client, monkeypatch, auth_header):
    from api.routes import vocabulary as vocab

    class FakeService:
        def __init__(self, *_a, **_k):
            pass

        def bulk_mark_level_known(self, user_id: int, level: str, known: bool):
            return 5

    monkeypatch.setattr(vocab, "VocabularyPreloadService", FakeService)

    r = await async_client.post(
        "/vocabulary/library/bulk-mark",
        json={"level": "A1", "known": True},
        headers=auth_header,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["level"] == "A1"
    assert data["known"] is True
    assert data["word_count"] == 5


@pytest.mark.asyncio
async def test_unmark_known_word(async_client, auth_header):
    r = await async_client.post(
        "/vocabulary/mark-known",
        json={"word": "sein", "known": False},
        headers=auth_header,
    )
    assert r.status_code == 200
    data = r.json()
    # Endpoint may report success False to indicate 'now unknown'; ensure structure is valid
    assert "success" in data and isinstance(data["success"], bool)
    assert data.get("word") == "sein"
    assert data.get("known") is False

"""
In-process vocabulary endpoint tests using TestClient and monkeypatching services.
Avoids filesystem and database-heavy operations.
"""
from __future__ import annotations

import pytest


class FakeVocabularyPreloadService:
    def __init__(self, *_args, **_kwargs):
        pass

    def get_vocabulary_stats(self):
        return {
            "A1": {"total_words": 10},
            "A2": {"total_words": 20},
            "B1": {"total_words": 30},
            "B2": {"total_words": 40},
        }

    def get_user_known_words(self, user_id: int, level: str):
        return {"sein", "haben"} if level == "A1" else set()

    def get_level_words(self, level: str):
        return [
            {"id": 1, "word": "sein", "difficulty_level": level, "part_of_speech": "verb", "definition": "to be"},
            {"id": 2, "word": "haben", "difficulty_level": level, "part_of_speech": "verb", "definition": "to have"},
        ]

    def bulk_mark_level_known(self, user_id: int, level: str, known: bool):
        return 2


@pytest.fixture()
def auth_header():
    # Matches conftest mock_auth_service expected token
    return {"Authorization": "Bearer test_token"}


@pytest.mark.asyncio
async def test_vocabulary_stats(async_client, monkeypatch, auth_header):
    from api.routes import vocabulary as vocab_module
    monkeypatch.setattr(vocab_module, "VocabularyPreloadService", FakeVocabularyPreloadService)

    r = await async_client.get("/vocabulary/library/stats", headers=auth_header)
    assert r.status_code == 200
    data = r.json()
    assert set(["A1", "A2", "B1", "B2"]).issubset(set(data["levels"].keys()))
    assert "total_words" in data


@pytest.mark.asyncio
async def test_vocabulary_level(async_client, monkeypatch, auth_header):
    from api.routes import vocabulary as vocab_module
    monkeypatch.setattr(vocab_module, "VocabularyPreloadService", FakeVocabularyPreloadService)

    r = await async_client.get("/vocabulary/library/A1", headers=auth_header)
    assert r.status_code == 200
    data = r.json()
    assert data["level"] == "A1"
    assert data["total_count"] >= 2
    assert any(w["word"] == "sein" for w in data["words"])  # type: ignore[index]


@pytest.mark.asyncio
async def test_bulk_mark_level(async_client, monkeypatch, auth_header):
    from api.routes import vocabulary as vocab_module
    monkeypatch.setattr(vocab_module, "VocabularyPreloadService", FakeVocabularyPreloadService)

    r = await async_client.post("/vocabulary/library/bulk-mark", json={"level": "A1", "known": True}, headers=auth_header)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_blocking_words_mock(async_client, auth_header):
    # No subtitle exists; route should return mock words successfully
    r = await async_client.get(
        "/vocabulary/blocking-words",
        params={"video_path": "nonexistent.mp4", "segment_start": 0, "segment_duration": 60},
        headers=auth_header,
    )
    assert r.status_code == 200
    data = r.json()
    assert "blocking_words" in data
    assert isinstance(data["blocking_words"], list)

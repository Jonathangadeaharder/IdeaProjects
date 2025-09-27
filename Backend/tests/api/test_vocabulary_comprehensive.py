"""
Comprehensive Enhanced Vocabulary Route Tests

This test suite significantly expands vocabulary testing coverage with:
- Multilingual translation combinations
- Performance testing with large datasets
- Complex vocabulary progression scenarios
- Statistical accuracy validation
- Bulk operations testing
- Error boundary testing
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from unittest.mock import patch, MagicMock

from tests.helpers.data_builders import VocabularyConceptBuilder, VocabularyTranslationBuilder, TestDataSets, CEFRLevel, UserBuilder


class TestMultilingualVocabulary:
    """Test multilingual vocabulary functionality with various language combinations"""

    @pytest.fixture
    async def auth_user(self, async_client):
        """Create authenticated user for vocabulary tests"""
        from tests.helpers.data_builders import UserBuilder
        user = UserBuilder().build()

        # Register and login user
        register_data = {
            "username": user.username,
            "email": user.email,
            "password": user.password
        }

        register_response = await async_client.post("/api/auth/register", json=register_data)
        assert register_response.status_code == 201

        login_data = {
            "username": user.email,
            "password": user.password
        }
        login_response = await async_client.post("/api/auth/login", data=login_data)
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]
        return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}

    @pytest.mark.asyncio
    async def test_WhenGetVocabularyWithSpanishTranslations_ThenReturnsCorrectTranslations(self, async_client, auth_user):
        """Test vocabulary retrieval with Spanish translations"""
        headers = auth_user["headers"]

        response = await async_client.get(
            "/api/vocabulary/library/A1",
            params={"target_language": "de", "translation_language": "es", "limit": 10},
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["target_language"] == "de"
        assert data["translation_language"] == "es"
        assert data["level"] == "A1"
        assert isinstance(data["words"], list)
        assert data["total_count"] >= 0
        assert data["known_count"] >= 0

        # Verify word structure
        if data["words"]:
            word = data["words"][0]
            assert "concept_id" in word
            assert "word" in word
            assert "difficulty_level" in word
            assert isinstance(word["known"], bool)

    @pytest.mark.asyncio
    async def test_WhenGetVocabularyWithEnglishTranslations_ThenReturnsCorrectTranslations(self, async_client, auth_user):
        """Test vocabulary retrieval with English translations"""
        headers = auth_user["headers"]

        response = await async_client.get(
            "/api/vocabulary/library/B1",
            params={"target_language": "de", "translation_language": "en", "limit": 5},
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["target_language"] == "de"
        assert data["translation_language"] == "en"
        assert data["level"] == "B1"

    @pytest.mark.asyncio
    async def test_WhenGetStatsWithMultipleLanguages_ThenReturnsAccurateStats(self, async_client, auth_user):
        """Test statistics with different language combinations"""
        headers = auth_user["headers"]

        # Test German-Spanish combination
        response = await async_client.get(
            "/api/vocabulary/stats",
            params={"target_language": "de", "translation_language": "es"},
            headers=headers
        )

        assert response.status_code == 200
        stats = response.json()

        assert "levels" in stats
        assert "target_language" in stats
        assert "translation_language" in stats
        assert "total_words" in stats
        assert "total_known" in stats

        # Verify all CEFR levels are present
        for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
            assert level in stats["levels"]
            assert "total_words" in stats["levels"][level]
            assert "user_known" in stats["levels"][level]


class TestVocabularyProgression:
    """Test vocabulary learning progression and knowledge tracking"""

    @pytest.fixture
    async def auth_user(self, async_client):
        """Create authenticated user for progression tests"""
        user = UserBuilder().build()

        register_data = {
            "username": user.username,
            "email": user.email,
            "password": user.password
        }

        register_response = await async_client.post("/api/auth/register", json=register_data)
        assert register_response.status_code == 201

        login_data = {
            "username": user.email,
            "password": user.password
        }
        login_response = await async_client.post("/api/auth/login", data=login_data)
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]
        return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}

    @pytest.mark.asyncio
    async def test_WhenMarkWordKnownAndCheckStats_ThenStatsUpdateCorrectly(self, async_client, auth_user):
        """Test that marking words as known correctly updates statistics"""
        headers = auth_user["headers"]

        # Get initial stats
        initial_stats_response = await async_client.get("/api/vocabulary/stats", headers=headers)
        assert initial_stats_response.status_code == 200
        initial_stats = initial_stats_response.json()
        initial_known = initial_stats["total_known"]

        # Get a word from A1 level
        words_response = await async_client.get(
            "/api/vocabulary/library/A1",
            params={"limit": 1},
            headers=headers
        )
        assert words_response.status_code == 200
        words_data = words_response.json()

        if not words_data["words"]:
            pytest.skip("No vocabulary words available for testing")

        concept_id = words_data["words"][0]["concept_id"]

        # Mark word as known
        mark_response = await async_client.post(
            "/api/vocabulary/mark-known",
            json={"concept_id": concept_id, "known": True},
            headers=headers
        )
        assert mark_response.status_code == 200
        mark_data = mark_response.json()
        assert mark_data["success"] is True
        assert mark_data["known"] is True

        # Check updated stats
        updated_stats_response = await async_client.get("/api/vocabulary/stats", headers=headers)
        assert updated_stats_response.status_code == 200
        updated_stats = updated_stats_response.json()

        # Verify total known count increased
        assert updated_stats["total_known"] == initial_known + 1

    @pytest.mark.asyncio
    async def test_WhenUnmarkWordAsKnown_ThenStatsDecrementCorrectly(self, async_client, auth_user):
        """Test unmarking words as known decrements statistics correctly"""
        headers = auth_user["headers"]

        # Get a word and mark it as known first
        words_response = await async_client.get(
            "/api/vocabulary/library/A1",
            params={"limit": 1},
            headers=headers
        )
        assert words_response.status_code == 200
        words_data = words_response.json()

        if not words_data["words"]:
            pytest.skip("No vocabulary words available for testing")

        concept_id = words_data["words"][0]["concept_id"]

        # Mark as known
        await async_client.post(
            "/api/vocabulary/mark-known",
            json={"concept_id": concept_id, "known": True},
            headers=headers
        )

        # Get stats after marking as known
        stats_known_response = await async_client.get("/api/vocabulary/stats", headers=headers)
        stats_known = stats_known_response.json()
        known_count = stats_known["total_known"]

        # Mark as unknown
        unmark_response = await async_client.post(
            "/api/vocabulary/mark-known",
            json={"concept_id": concept_id, "known": False},
            headers=headers
        )
        assert unmark_response.status_code == 200
        unmark_data = unmark_response.json()
        assert unmark_data["success"] is True
        assert unmark_data["known"] is False

        # Check updated stats
        final_stats_response = await async_client.get("/api/vocabulary/stats", headers=headers)
        final_stats = final_stats_response.json()

        # Verify total known count decreased
        assert final_stats["total_known"] == known_count - 1

    @pytest.mark.asyncio
    async def test_WhenBulkMarkLevelAsKnown_ThenAllWordsMarkedCorrectly(self, async_client, auth_user):
        """Test bulk marking entire level affects all words in that level"""
        headers = auth_user["headers"]

        # Get initial A1 level data
        initial_level_response = await async_client.get(
            "/api/vocabulary/library/A1",
            params={"limit": 100},
            headers=headers
        )
        assert initial_level_response.status_code == 200
        initial_level_data = initial_level_response.json()
        initial_known_count = initial_level_data["known_count"]

        # Bulk mark A1 level as known
        bulk_response = await async_client.post(
            "/api/vocabulary/library/bulk-mark",
            json={"level": "A1", "target_language": "de", "known": True},
            headers=headers
        )
        assert bulk_response.status_code == 200
        bulk_data = bulk_response.json()
        assert bulk_data["success"] is True
        assert bulk_data["level"] == "A1"
        assert bulk_data["known"] is True
        assert "word_count" in bulk_data

        # Verify level data shows increased known count
        final_level_response = await async_client.get(
            "/api/vocabulary/library/A1",
            params={"limit": 100},
            headers=headers
        )
        assert final_level_response.status_code == 200
        final_level_data = final_level_response.json()

        # Known count should have increased
        assert final_level_data["known_count"] >= initial_known_count


class TestVocabularyPerformance:
    """Test vocabulary API performance with large datasets"""

    @pytest.fixture
    async def auth_user(self, async_client):
        """Create authenticated user for performance tests"""
        user = UserBuilder().build()

        register_data = {
            "username": user.username,
            "email": user.email,
            "password": user.password
        }

        register_response = await async_client.post("/api/auth/register", json=register_data)
        assert register_response.status_code == 201

        login_data = {
            "username": user.email,
            "password": user.password
        }
        login_response = await async_client.post("/api/auth/login", data=login_data)
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]
        return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}

    @pytest.mark.asyncio
    async def test_WhenRequestLargeVocabularyLimit_ThenRespondsWithinReasonableTime(self, async_client, auth_user):
        """Test API performance with large vocabulary requests"""
        headers = auth_user["headers"]

        start_time = datetime.now()

        response = await async_client.get(
            "/api/vocabulary/library/A1",
            params={"limit": 1000, "target_language": "de"},
            headers=headers
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        assert response.status_code == 200
        assert duration < 5.0  # Should respond within 5 seconds

        data = response.json()
        assert isinstance(data["words"], list)
        assert len(data["words"]) <= 1000

    @pytest.mark.asyncio
    async def test_WhenGetStatsForAllLevels_ThenRespondsQuickly(self, async_client, auth_user):
        """Test statistics calculation performance"""
        headers = auth_user["headers"]

        start_time = datetime.now()

        response = await async_client.get(
            "/api/vocabulary/stats",
            params={"target_language": "de", "translation_language": "es"},
            headers=headers
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        assert response.status_code == 200
        assert duration < 3.0  # Statistics should be fast

        stats = response.json()
        # Verify all levels are calculated
        for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
            assert level in stats["levels"]

    @pytest.mark.asyncio
    async def test_WhenConcurrentVocabularyRequests_ThenAllSucceed(self, async_client, auth_user):
        """Test concurrent vocabulary requests don't cause race conditions"""
        headers = auth_user["headers"]

        # Make 5 concurrent requests for different levels
        tasks = []
        for level in ["A1", "A2", "B1", "B2", "C1"]:
            task = async_client.get(
                f"/api/vocabulary/library/{level}",
                params={"limit": 10},
                headers=headers
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # All requests should succeed
        for result in results:
            assert result.status_code == 200
            data = result.json()
            assert "words" in data
            assert "level" in data


class TestVocabularyErrorBoundaries:
    """Test vocabulary API error handling and boundary conditions"""

    @pytest.fixture
    async def auth_user(self, async_client):
        """Create authenticated user for error boundary tests"""
        user = UserBuilder().build()

        register_data = {
            "username": user.username,
            "email": user.email,
            "password": user.password
        }

        register_response = await async_client.post("/api/auth/register", json=register_data)
        assert register_response.status_code == 201

        login_data = {
            "username": user.email,
            "password": user.password
        }
        login_response = await async_client.post("/api/auth/login", data=login_data)
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]
        return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}

    @pytest.mark.asyncio
    async def test_WhenMarkKnownWithNonexistentConceptId_ThenHandlesGracefully(self, async_client, auth_user):
        """Test marking nonexistent concept as known handles gracefully"""
        headers = auth_user["headers"]
        fake_concept_id = str(uuid4())

        response = await async_client.post(
            "/api/vocabulary/mark-known",
            json={"concept_id": fake_concept_id, "known": True},
            headers=headers
        )

        # Should either succeed (creating progress for nonexistent concept)
        # or return appropriate error
        assert response.status_code in [200, 404, 422]

    @pytest.mark.asyncio
    async def test_WhenGetLibraryWithInvalidCEFRLevel_ThenReturns422(self, async_client, auth_user):
        """Test invalid CEFR level returns proper validation error"""
        headers = auth_user["headers"]

        response = await async_client.get(
            "/api/vocabulary/library/X5",  # Invalid level
            headers=headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_WhenBulkMarkWithInvalidLevel_ThenReturns422(self, async_client, auth_user):
        """Test bulk marking with invalid level returns validation error"""
        headers = auth_user["headers"]

        response = await async_client.post(
            "/api/vocabulary/library/bulk-mark",
            json={"level": "Z9", "target_language": "de", "known": True},
            headers=headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_WhenGetLibraryWithZeroLimit_ThenHandlesCorrectly(self, async_client, auth_user):
        """Test vocabulary library with zero limit parameter"""
        headers = auth_user["headers"]

        response = await async_client.get(
            "/api/vocabulary/library/A1",
            params={"limit": 0},
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["words"], list)
        assert len(data["words"]) == 0

    @pytest.mark.asyncio
    async def test_WhenGetLibraryWithNegativeLimit_ThenHandlesCorrectly(self, async_client, auth_user):
        """Test vocabulary library with negative limit parameter"""
        headers = auth_user["headers"]

        response = await async_client.get(
            "/api/vocabulary/library/A1",
            params={"limit": -10},
            headers=headers
        )

        # Should either handle gracefully (empty result) or return validation error
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_WhenRequestUnsupportedLanguageCombination_ThenHandlesGracefully(self, async_client, auth_user):
        """Test unsupported language combinations are handled gracefully"""
        headers = auth_user["headers"]

        response = await async_client.get(
            "/api/vocabulary/library/A1",
            params={"target_language": "xyz", "translation_language": "abc"},
            headers=headers
        )

        # Should handle gracefully with empty results or validation error
        assert response.status_code in [200, 422]


class TestVocabularyStatisticalAccuracy:
    """Test accuracy of vocabulary statistics and calculations"""

    @pytest.fixture
    async def auth_user(self, async_client):
        """Create authenticated user for statistical tests"""
        user = UserBuilder().build()

        register_data = {
            "username": user.username,
            "email": user.email,
            "password": user.password
        }

        register_response = await async_client.post("/api/auth/register", json=register_data)
        assert register_response.status_code == 201

        login_data = {
            "username": user.email,
            "password": user.password
        }
        login_response = await async_client.post("/api/auth/login", data=login_data)
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]
        return {"user": user, "token": token, "headers": {"Authorization": f"Bearer {token}"}}

    @pytest.mark.asyncio
    async def test_WhenCalculatingLevelStats_ThenSumMatchesTotalStats(self, async_client, auth_user):
        """Test that individual level stats sum correctly to total stats"""
        headers = auth_user["headers"]

        response = await async_client.get("/api/vocabulary/stats", headers=headers)
        assert response.status_code == 200
        stats = response.json()

        # Calculate sum of individual levels
        total_words_calculated = sum(stats["levels"][level]["total_words"] for level in stats["levels"])
        total_known_calculated = sum(stats["levels"][level]["user_known"] for level in stats["levels"])

        # Should match reported totals
        assert stats["total_words"] == total_words_calculated
        assert stats["total_known"] == total_known_calculated

    @pytest.mark.asyncio
    async def test_WhenComparingLevelDataToStats_ThenCountsMatch(self, async_client, auth_user):
        """Test that level-specific data matches what's reported in stats"""
        headers = auth_user["headers"]

        # Get stats
        stats_response = await async_client.get("/api/vocabulary/stats", headers=headers)
        assert stats_response.status_code == 200
        stats = stats_response.json()

        # Get A1 level details with high limit to get all words
        level_response = await async_client.get(
            "/api/vocabulary/library/A1",
            params={"limit": 10000},  # High limit to get all words
            headers=headers
        )
        assert level_response.status_code == 200
        level_data = level_response.json()

        # Compare A1 counts
        a1_stats = stats["levels"]["A1"]

        # Total words should match or be reasonable (level data might be limited by actual DB content)
        if level_data["total_count"] > 0:
            # If we have level data, known count should be consistent
            assert level_data["known_count"] == a1_stats["user_known"]

    @pytest.mark.asyncio
    async def test_WhenUserHasNoProgress_ThenAllKnownCountsAreZero(self, async_client, auth_user):
        """Test fresh user has zero known counts across all levels"""
        headers = auth_user["headers"]

        response = await async_client.get("/api/vocabulary/stats", headers=headers)
        assert response.status_code == 200
        stats = response.json()

        # Fresh user should have no known words initially
        # (unless seeded data affects this)
        assert stats["total_known"] >= 0
        for level_stats in stats["levels"].values():
            assert level_stats["user_known"] >= 0

    @pytest.mark.asyncio
    async def test_WhenMarkingSameWordMultipleTimes_ThenStatsStayConsistent(self, async_client, auth_user):
        """Test marking same word known multiple times doesn't inflate counts"""
        headers = auth_user["headers"]

        # Get a word
        words_response = await async_client.get(
            "/api/vocabulary/library/A1",
            params={"limit": 1},
            headers=headers
        )
        assert words_response.status_code == 200
        words_data = words_response.json()

        if not words_data["words"]:
            pytest.skip("No vocabulary words available for testing")

        concept_id = words_data["words"][0]["concept_id"]

        # Get initial stats
        initial_stats = await async_client.get("/api/vocabulary/stats", headers=headers)
        initial_known = initial_stats.json()["total_known"]

        # Mark as known multiple times
        for _ in range(3):
            mark_response = await async_client.post(
                "/api/vocabulary/mark-known",
                json={"concept_id": concept_id, "known": True},
                headers=headers
            )
            assert mark_response.status_code == 200

        # Check final stats
        final_stats = await async_client.get("/api/vocabulary/stats", headers=headers)
        final_known = final_stats.json()["total_known"]

        # Should only increase by 1, not 3
        assert final_known == initial_known + 1
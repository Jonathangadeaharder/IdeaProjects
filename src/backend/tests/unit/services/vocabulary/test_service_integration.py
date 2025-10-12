"""
Integration tests for refactored vocabulary services
Verifies that the facade correctly delegates to sub-services
"""

from unittest.mock import AsyncMock

import pytest

from services.vocabulary.vocabulary_progress_service import VocabularyProgressService
from services.vocabulary.vocabulary_query_service import VocabularyQueryService
from services.vocabulary.vocabulary_service import VocabularyService
from services.vocabulary.vocabulary_stats_service import VocabularyStatsService


class TestVocabularyServiceArchitecture:
    """Test the refactored service architecture"""

    def test_service_initialization(self):
        """Test that facade initializes with all sub-services"""
        service = VocabularyService()

        assert service.query_service is not None
        assert service.progress_service is not None
        assert service.stats_service is not None

        assert isinstance(service.query_service, VocabularyQueryService)
        assert isinstance(service.progress_service, VocabularyProgressService)
        assert isinstance(service.stats_service, VocabularyStatsService)

    @pytest.mark.asyncio
    async def test_facade_delegates_to_query_service(self):
        """Test that query methods delegate to query service"""
        service = VocabularyService()
        mock_db = AsyncMock()

        # Mock the query service method
        service.query_service.get_word_info = AsyncMock(return_value={"found": True, "word": "test", "lemma": "test"})

        result = await service.get_word_info("test", "de", mock_db)

        assert result["found"] is True
        service.query_service.get_word_info.assert_called_once_with("test", "de", mock_db)

    @pytest.mark.asyncio
    async def test_facade_delegates_to_progress_service(self):
        """Test that progress methods delegate to progress service"""
        service = VocabularyService()
        mock_db = AsyncMock()

        # Mock the progress service method
        service.progress_service.mark_word_known = AsyncMock(
            return_value={"success": True, "word": "test", "is_known": True}
        )

        result = await service.mark_word_known(123, "test", "de", True, mock_db)

        assert result["success"] is True
        service.progress_service.mark_word_known.assert_called_once_with(123, "test", "de", True, mock_db)

    @pytest.mark.asyncio
    async def test_facade_delegates_to_stats_service(self):
        """Test that stats methods delegate to stats service"""
        service = VocabularyService()

        # Mock the stats service method
        service.stats_service.get_vocabulary_stats = AsyncMock(
            return_value={"target_language": "de", "levels": {}, "total_words": 100, "total_known": 50}
        )

        result = await service.get_vocabulary_stats("de", 123)

        assert result["total_words"] == 100
        service.stats_service.get_vocabulary_stats.assert_called_once()


class TestServiceArchitectureMetrics:
    """Test that architecture improvements are measurable"""

    def test_service_line_counts_reasonable(self):
        """Test that each service is reasonably sized"""
        import inspect

        # Facade should be reasonably sized (delegation + some business logic)
        facade_lines = len(inspect.getsource(VocabularyService).split("\n"))
        assert facade_lines < 400, "Facade should be < 400 lines"

        # Sub-services should be focused (< 400 lines each)
        query_lines = len(inspect.getsource(VocabularyQueryService).split("\n"))
        assert query_lines < 400, "Query service should be < 400 lines"

        progress_lines = len(inspect.getsource(VocabularyProgressService).split("\n"))
        assert progress_lines < 300, "Progress service should be < 300 lines"

        stats_lines = len(inspect.getsource(VocabularyStatsService).split("\n"))
        assert stats_lines < 300, "Stats service should be < 300 lines"

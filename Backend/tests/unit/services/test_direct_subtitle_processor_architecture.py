"""
Architecture Tests for Refactored DirectSubtitleProcessor
Verifies service boundaries and separation of concerns
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock


class TestDirectSubtitleProcessorArchitecture:
    """Test facade delegates properly to services"""

    def test_facade_imports_all_services(self):
        """Facade should import all required services"""
        from services.filterservice.direct_subtitle_processor import DirectSubtitleProcessor

        processor = DirectSubtitleProcessor()

        # Verify all services are initialized
        assert processor.data_loader is not None
        assert processor.validator is not None
        assert processor.filter is not None
        assert processor.processor is not None
        assert processor.file_handler is not None

    def test_facade_does_not_contain_implementation_logic(self):
        """Facade should only delegate, not implement business logic"""
        import inspect
        from services.filterservice.direct_subtitle_processor import DirectSubtitleProcessor

        # Get source code
        source = inspect.getsource(DirectSubtitleProcessor)

        # Facade should not contain these implementation patterns
        forbidden_patterns = [
            '_german_interjections',  # Language data should be in WordValidator
            '_proper_name_pattern',    # Patterns should be in WordValidator
            '_word_difficulty_cache',  # Caching should be in UserDataLoader
            '_level_ranks',            # Level logic should be in WordFilter
            'for word in subtitle.words',  # Word processing should be in SubtitleProcessor
        ]

        for pattern in forbidden_patterns:
            assert pattern not in source, f"Facade contains implementation: {pattern}"

    @pytest.mark.asyncio
    async def test_facade_delegates_process_subtitles_to_processor(self):
        """process_subtitles should delegate to SubtitleProcessor"""
        from services.filterservice.direct_subtitle_processor import DirectSubtitleProcessor
        from services.filterservice.interface import FilteredSubtitle, FilteringResult

        processor = DirectSubtitleProcessor()

        # Mock the services
        processor.data_loader = AsyncMock()
        processor.data_loader.get_user_known_words = AsyncMock(return_value=set())
        processor.data_loader.load_word_difficulties = AsyncMock()

        processor.processor = AsyncMock()
        mock_result = FilteringResult(
            learning_subtitles=[],
            blocker_words=[],
            empty_subtitles=[],
            statistics={}
        )
        processor.processor.process_subtitles = AsyncMock(return_value=mock_result)

        # Call facade
        subtitles = [
            FilteredSubtitle(
                original_text="Test",
                start_time=0.0,
                end_time=1.0,
                words=[]
            )
        ]

        result = await processor.process_subtitles(subtitles, "user123", "A1", "de")

        # Verify delegation occurred
        processor.data_loader.get_user_known_words.assert_called_once_with("user123", "de")
        processor.data_loader.load_word_difficulties.assert_called_once_with("de")
        processor.processor.process_subtitles.assert_called_once()

    @pytest.mark.asyncio
    async def test_facade_delegates_process_srt_file_to_file_handler(self):
        """process_srt_file should delegate to SRTFileHandler"""
        from services.filterservice.direct_subtitle_processor import DirectSubtitleProcessor
        from services.filterservice.interface import FilteredSubtitle, FilteringResult

        processor = DirectSubtitleProcessor()

        # Mock services
        processor.file_handler = AsyncMock()
        processor.file_handler.parse_srt_file = AsyncMock(return_value=[])
        processor.file_handler.format_processing_result = Mock(return_value={
            "blocking_words": [],
            "learning_subtitles": [],
            "empty_subtitles": [],
            "filtered_subtitles": [],
            "statistics": {}
        })

        processor.data_loader = AsyncMock()
        processor.data_loader.get_user_known_words = AsyncMock(return_value=set())
        processor.data_loader.load_word_difficulties = AsyncMock()

        processor.processor = AsyncMock()
        mock_result = FilteringResult(
            learning_subtitles=[],
            blocker_words=[],
            empty_subtitles=[],
            statistics={}
        )
        processor.processor.process_subtitles = AsyncMock(return_value=mock_result)

        # Call facade
        result = await processor.process_srt_file("test.srt", "user123", "A1", "de")

        # Verify delegation
        processor.file_handler.parse_srt_file.assert_called_once_with("test.srt")
        processor.file_handler.format_processing_result.assert_called_once()


class TestUserDataLoaderService:
    """Test UserDataLoader service isolation"""

    def test_user_data_loader_exists(self):
        """UserDataLoader service should exist"""
        from services.filterservice.subtitle_processing import UserDataLoader

        loader = UserDataLoader()
        assert loader is not None

    def test_user_data_loader_has_caching(self):
        """UserDataLoader should have caching capabilities"""
        from services.filterservice.subtitle_processing import UserDataLoader

        loader = UserDataLoader()

        # Should have cache attributes
        assert hasattr(loader, '_word_difficulty_cache')
        assert hasattr(loader, '_user_known_words_cache')

    @pytest.mark.asyncio
    async def test_user_data_loader_provides_user_known_words(self):
        """UserDataLoader should provide user known words"""
        from services.filterservice.subtitle_processing import UserDataLoader

        loader = UserDataLoader()

        # Should return a set
        result = await loader.get_user_known_words("test_user", "de")
        assert isinstance(result, set)

    @pytest.mark.asyncio
    async def test_user_data_loader_loads_word_difficulties(self):
        """UserDataLoader should load word difficulties"""
        from services.filterservice.subtitle_processing import UserDataLoader

        loader = UserDataLoader()

        # Should return a dict
        result = await loader.load_word_difficulties("de")
        assert isinstance(result, dict)


class TestWordValidatorService:
    """Test WordValidator service isolation"""

    def test_word_validator_exists(self):
        """WordValidator service should exist"""
        from services.filterservice.subtitle_processing import WordValidator

        validator = WordValidator()
        assert validator is not None

    def test_word_validator_validates_vocabulary_words(self):
        """WordValidator should validate vocabulary words"""
        from services.filterservice.subtitle_processing import WordValidator

        validator = WordValidator()

        # Valid word
        assert validator.is_valid_vocabulary_word("schwierig", "de") == True

        # Invalid words
        assert validator.is_valid_vocabulary_word("123", "de") == False
        assert validator.is_valid_vocabulary_word("oh", "de") == False

    def test_word_validator_detects_interjections(self):
        """WordValidator should detect interjections"""
        from services.filterservice.subtitle_processing import WordValidator

        validator = WordValidator()

        # German interjections
        assert validator.is_interjection("hallo", "de") == True
        assert validator.is_interjection("ach", "de") == True

        # Not interjections
        assert validator.is_interjection("schwierig", "de") == False

    def test_word_validator_supports_multiple_languages(self):
        """WordValidator should support multiple languages"""
        from services.filterservice.subtitle_processing import WordValidator

        validator = WordValidator()

        # Should have language-specific interjections
        assert hasattr(validator, '_interjections_by_language')
        assert 'de' in validator._interjections_by_language
        assert 'en' in validator._interjections_by_language
        assert 'es' in validator._interjections_by_language

    def test_word_validator_provides_validation_reasons(self):
        """WordValidator should provide reasons for validation failures"""
        from services.filterservice.subtitle_processing import WordValidator

        validator = WordValidator()

        # Should provide reason for invalid words
        reason = validator.get_validation_reason("oh", "de")
        assert reason is not None
        assert isinstance(reason, str)

        # Should return None for valid words
        reason = validator.get_validation_reason("schwierig", "de")
        assert reason is None


class TestWordFilterService:
    """Test WordFilter service isolation"""

    def test_word_filter_exists(self):
        """WordFilter service should exist"""
        from services.filterservice.subtitle_processing import WordFilter

        word_filter = WordFilter()
        assert word_filter is not None

    def test_word_filter_filters_words(self):
        """WordFilter should filter words based on criteria"""
        from services.filterservice.subtitle_processing import WordFilter
        from services.filterservice.interface import FilteredWord, WordStatus

        word_filter = WordFilter()

        test_word = FilteredWord(
            text="schwierig",
            start_time=0.0,
            end_time=1.0,
            status=WordStatus.ACTIVE,
            filter_reason=None,
            confidence=None,
            metadata={}
        )

        # Filter with empty known words - should remain active
        result = word_filter.filter_word(
            test_word,
            user_known_words=set(),
            user_level="A1",
            language="de",
            word_info=None
        )

        assert result.status == WordStatus.ACTIVE
        assert "lemma" in result.metadata

    def test_word_filter_checks_user_knowledge(self):
        """WordFilter should filter known words"""
        from services.filterservice.subtitle_processing import WordFilter
        from services.filterservice.interface import FilteredWord, WordStatus

        word_filter = WordFilter()

        test_word = FilteredWord(
            text="schwierig",
            start_time=0.0,
            end_time=1.0,
            status=WordStatus.ACTIVE,
            filter_reason=None,
            confidence=None,
            metadata={}
        )

        # Filter with word in known words
        result = word_filter.filter_word(
            test_word,
            user_known_words={"schwierig"},
            user_level="A1",
            language="de",
            word_info=None
        )

        assert result.status == WordStatus.FILTERED_KNOWN

    def test_word_filter_has_level_comparison(self):
        """WordFilter should compare CEFR levels"""
        from services.filterservice.subtitle_processing import WordFilter

        word_filter = WordFilter()

        # Should have level comparison logic
        assert hasattr(word_filter, 'is_at_or_below_user_level')
        assert hasattr(word_filter, '_level_ranks')

        # Test level comparison
        assert word_filter.is_at_or_below_user_level("A1", "B1") == True
        assert word_filter.is_at_or_below_user_level("C1", "A1") == False


class TestSubtitleProcessorService:
    """Test SubtitleProcessor service isolation"""

    def test_subtitle_processor_exists(self):
        """SubtitleProcessor service should exist"""
        from services.filterservice.subtitle_processing import SubtitleProcessor

        processor = SubtitleProcessor()
        assert processor is not None

    def test_subtitle_processor_has_dependencies(self):
        """SubtitleProcessor should depend on validator and filter"""
        from services.filterservice.subtitle_processing import SubtitleProcessor

        processor = SubtitleProcessor()

        # Should have validator and filter
        assert hasattr(processor, 'validator')
        assert hasattr(processor, 'word_filter')

    @pytest.mark.asyncio
    async def test_subtitle_processor_processes_subtitles(self):
        """SubtitleProcessor should process subtitles"""
        from services.filterservice.subtitle_processing import SubtitleProcessor
        from services.filterservice.interface import FilteredSubtitle, FilteredWord, WordStatus

        processor = SubtitleProcessor()

        # Create test subtitle
        word = FilteredWord(
            text="test",
            start_time=0.0,
            end_time=1.0,
            status=WordStatus.ACTIVE,
            filter_reason=None,
            confidence=None,
            metadata={}
        )

        subtitle = FilteredSubtitle(
            original_text="Test",
            start_time=0.0,
            end_time=1.0,
            words=[word]
        )

        # Mock vocab service
        vocab_service = Mock()
        vocab_service.get_word_info = AsyncMock(return_value=None)

        # Process
        result = await processor.process_subtitles(
            [subtitle],
            user_known_words=set(),
            user_level="A1",
            language="de",
            vocab_service=vocab_service
        )

        # Should return FilteringResult
        assert hasattr(result, 'learning_subtitles')
        assert hasattr(result, 'blocker_words')
        assert hasattr(result, 'empty_subtitles')
        assert hasattr(result, 'statistics')


class TestSRTFileHandlerService:
    """Test SRTFileHandler service isolation"""

    def test_srt_file_handler_exists(self):
        """SRTFileHandler service should exist"""
        from services.filterservice.subtitle_processing import SRTFileHandler

        handler = SRTFileHandler()
        assert handler is not None

    def test_srt_file_handler_extracts_words(self):
        """SRTFileHandler should extract words from text"""
        from services.filterservice.subtitle_processing import SRTFileHandler

        handler = SRTFileHandler()

        # Extract words
        words = handler.extract_words_from_text("Hello world", 0.0, 2.0)

        # Should return list of FilteredWord objects
        assert isinstance(words, list)
        assert len(words) == 2
        assert words[0].text == "hello"
        assert words[1].text == "world"

    def test_srt_file_handler_formats_results(self):
        """SRTFileHandler should format processing results"""
        from services.filterservice.subtitle_processing import SRTFileHandler
        from services.filterservice.interface import FilteringResult

        handler = SRTFileHandler()

        # Create test result
        result = FilteringResult(
            learning_subtitles=[],
            blocker_words=[],
            empty_subtitles=[],
            statistics={"test": "value"}
        )

        # Format
        formatted = handler.format_processing_result(result, "test.srt")

        # Should have required keys
        assert "blocking_words" in formatted
        assert "learning_subtitles" in formatted
        assert "empty_subtitles" in formatted
        assert "filtered_subtitles" in formatted
        assert "statistics" in formatted


class TestServiceSingletons:
    """Test singleton instances are available"""

    def test_all_singletons_exist(self):
        """All service singletons should be available"""
        from services.filterservice.subtitle_processing import (
            user_data_loader,
            word_validator,
            word_filter,
            subtitle_processor,
            srt_file_handler
        )

        assert user_data_loader is not None
        assert word_validator is not None
        assert word_filter is not None
        assert subtitle_processor is not None
        assert srt_file_handler is not None

    def test_singletons_are_service_instances(self):
        """Singletons should be instances of their respective classes"""
        from services.filterservice.subtitle_processing import (
            user_data_loader,
            word_validator,
            word_filter,
            subtitle_processor,
            srt_file_handler,
            UserDataLoader,
            WordValidator,
            WordFilter,
            SubtitleProcessor,
            SRTFileHandler
        )

        assert isinstance(user_data_loader, UserDataLoader)
        assert isinstance(word_validator, WordValidator)
        assert isinstance(word_filter, WordFilter)
        assert isinstance(subtitle_processor, SubtitleProcessor)
        assert isinstance(srt_file_handler, SRTFileHandler)
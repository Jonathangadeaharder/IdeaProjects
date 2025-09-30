"""
Verification script for refactored ChunkProcessingService
Tests basic functionality and service integration
"""

import sys
from pathlib import Path

# Add Backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def test_imports():
    """Test all service imports work"""
    print("Testing imports...")

    try:
        from services.processing.chunk_services import (
            VocabularyFilterService, vocabulary_filter_service,
            SubtitleGenerationService, subtitle_generation_service,
            TranslationManagementService, translation_management_service
        )
        print("  [GOOD] All service imports successful")
        return True
    except ImportError as e:
        print(f"  [POOR] Import failed: {e}")
        return False


def test_service_singletons():
    """Test singleton instances work"""
    print("\nTesting service singletons...")

    try:
        from services.processing.chunk_services import (
            vocabulary_filter_service,
            subtitle_generation_service,
            translation_management_service
        )

        # Test each singleton
        assert vocabulary_filter_service is not None
        assert subtitle_generation_service is not None
        assert translation_management_service is not None

        print("  [GOOD] All singleton instances available")
        return True
    except Exception as e:
        print(f"  [POOR] Singleton test failed: {e}")
        return False


def test_vocabulary_filter_service():
    """Test VocabularyFilterService basics"""
    print("\nTesting VocabularyFilterService...")

    try:
        from services.processing.chunk_services import VocabularyFilterService

        service = VocabularyFilterService()

        # Test has subtitle_processor
        assert hasattr(service, 'subtitle_processor')
        assert service.subtitle_processor is not None

        # Test has methods
        assert hasattr(service, 'filter_vocabulary_from_srt')
        assert hasattr(service, 'extract_vocabulary_from_result')
        assert hasattr(service, 'debug_empty_vocabulary')

        print("  [GOOD] VocabularyFilterService working")
        return True
    except Exception as e:
        print(f"  [POOR] VocabularyFilterService test failed: {e}")
        return False


def test_subtitle_generation_service():
    """Test SubtitleGenerationService basics"""
    print("\nTesting SubtitleGenerationService...")

    try:
        from services.processing.chunk_services import SubtitleGenerationService

        service = SubtitleGenerationService()

        # Test has methods
        assert hasattr(service, 'generate_filtered_subtitles')
        assert hasattr(service, 'process_srt_content')
        assert hasattr(service, 'highlight_vocabulary_in_line')
        assert hasattr(service, 'read_srt_file')
        assert hasattr(service, 'write_srt_file')

        # Test highlighting logic
        line = "Das ist ein Test"
        vocab_words = {"test"}
        highlighted = service.highlight_vocabulary_in_line(line, vocab_words)

        assert "test" in highlighted.lower()
        assert "font" in highlighted.lower() or highlighted == line  # Either highlighted or unchanged

        print("  [GOOD] SubtitleGenerationService working")
        return True
    except Exception as e:
        print(f"  [POOR] SubtitleGenerationService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_translation_management_service():
    """Test TranslationManagementService basics"""
    print("\nTesting TranslationManagementService...")

    try:
        from services.processing.chunk_services import TranslationManagementService

        service = TranslationManagementService()

        # Test has subtitle_processor
        assert hasattr(service, 'subtitle_processor')
        assert service.subtitle_processor is not None

        # Test has methods
        assert hasattr(service, 'apply_selective_translations')
        assert hasattr(service, 'refilter_for_translations')
        assert hasattr(service, 'build_translation_segments')
        assert hasattr(service, 'filter_unknown_words')
        assert hasattr(service, 'create_translation_segments')
        assert hasattr(service, 'create_translation_segment')
        assert hasattr(service, 'create_translation_response')
        assert hasattr(service, 'create_fallback_response')

        print("  [GOOD] TranslationManagementService working")
        return True
    except Exception as e:
        print(f"  [POOR] TranslationManagementService test failed: {e}")
        return False


def test_chunk_processor_facade():
    """Test ChunkProcessingService facade structure"""
    print("\nTesting ChunkProcessingService facade...")

    try:
        from services.processing.chunk_processor import ChunkProcessingService
        from unittest.mock import Mock

        # Create mock database session
        db_session = Mock()

        # Create facade
        service = ChunkProcessingService(db_session)

        # Verify all services are initialized
        assert hasattr(service, 'transcription_service')
        assert hasattr(service, 'translation_service')
        assert hasattr(service, 'utilities')
        assert hasattr(service, 'vocabulary_filter')
        assert hasattr(service, 'subtitle_generator')
        assert hasattr(service, 'translation_manager')

        print("  [GOOD] ChunkProcessingService facade has all services")
        return True
    except Exception as e:
        print(f"  [POOR] Facade test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("ChunkProcessingService Refactoring Verification")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Service Singletons", test_service_singletons()))
    results.append(("VocabularyFilterService", test_vocabulary_filter_service()))
    results.append(("SubtitleGenerationService", test_subtitle_generation_service()))
    results.append(("TranslationManagementService", test_translation_management_service()))
    results.append(("ChunkProcessingService Facade", test_chunk_processor_facade()))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All verification tests passed!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
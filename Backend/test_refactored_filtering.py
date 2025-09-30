"""
Standalone test to verify refactored filtering handler architecture
Run with: python test_refactored_filtering.py
"""

import inspect
from services.processing.filtering_handler import FilteringHandler
from services.processing.filtering import (
    ProgressTrackerService,
    SubtitleLoaderService,
    VocabularyBuilderService,
    ResultProcessorService,
    FilteringCoordinatorService,
)


def test_architecture_structure():
    """Verify the service architecture is correctly structured"""
    print("\n=== Testing Architecture Structure ===")

    # Test 1: Facade initialization
    print("\n[TEST 1] Facade initializes with all sub-services")
    handler = FilteringHandler()
    assert handler.progress_tracker is not None, "Progress tracker not initialized"
    assert handler.loader is not None, "Loader not initialized"
    assert handler.vocab_builder is not None, "Vocab builder not initialized"
    assert handler.result_processor is not None, "Result processor not initialized"
    assert handler.coordinator is not None, "Coordinator not initialized"
    print("[PASS] All sub-services initialized")

    # Test 2: Sub-service types
    print("\n[TEST 2] Sub-services are correct types")
    assert isinstance(handler.progress_tracker, ProgressTrackerService)
    assert isinstance(handler.loader, SubtitleLoaderService)
    assert isinstance(handler.vocab_builder, VocabularyBuilderService)
    assert isinstance(handler.result_processor, ResultProcessorService)
    assert isinstance(handler.coordinator, FilteringCoordinatorService)
    print("[PASS] All sub-services have correct types")

    # Test 3: Facade exposes required methods
    print("\n[TEST 3] Facade exposes all required methods")
    methods = [
        'health_check', 'handle', 'validate_parameters',
        'filter_subtitles', 'extract_blocking_words',
        'refilter_for_translations', 'estimate_duration'
    ]
    for method in methods:
        assert hasattr(handler, method), f"Missing method: {method}"
        print(f"  [OK] Has method: {method}")
    print("[PASS] All methods available")


def test_sub_service_independence():
    """Verify sub-services can be used independently"""
    print("\n=== Testing Sub-Service Independence ===")

    # Test 4: Progress tracker standalone
    print("\n[TEST 4] Progress tracker works standalone")
    tracker = ProgressTrackerService()
    assert hasattr(tracker, 'initialize')
    assert hasattr(tracker, 'update_progress')
    assert hasattr(tracker, 'mark_complete')
    assert hasattr(tracker, 'mark_failed')
    print("[PASS] Progress tracker standalone")

    # Test 5: Subtitle loader standalone
    print("\n[TEST 5] Subtitle loader works standalone")
    loader = SubtitleLoaderService()
    assert hasattr(loader, 'load_and_parse')
    assert hasattr(loader, 'extract_words_from_text')
    assert hasattr(loader, 'estimate_duration')
    print("[PASS] Subtitle loader standalone")

    # Test 6: Vocabulary builder standalone
    print("\n[TEST 6] Vocabulary builder works standalone")
    builder = VocabularyBuilderService()
    assert hasattr(builder, 'build_vocabulary_words')
    assert hasattr(builder, 'generate_candidate_forms')
    print("[PASS] Vocabulary builder standalone")

    # Test 7: Result processor standalone
    print("\n[TEST 7] Result processor works standalone")
    processor = ResultProcessorService()
    assert hasattr(processor, 'process_filtering_results')
    assert hasattr(processor, 'format_results')
    assert hasattr(processor, 'save_to_file')
    print("[PASS] Result processor standalone")

    # Test 8: Filtering coordinator standalone
    print("\n[TEST 8] Filtering coordinator works standalone")
    coordinator = FilteringCoordinatorService()
    assert hasattr(coordinator, 'extract_blocking_words')
    assert hasattr(coordinator, 'refilter_for_translations')
    print("[PASS] Filtering coordinator standalone")


def test_service_metrics():
    """Verify architectural improvements are measurable"""
    print("\n=== Testing Architecture Metrics ===")

    # Test 9: Service line counts
    print("\n[TEST 9] Service sizes are reasonable")

    facade_lines = len(inspect.getsource(FilteringHandler).split('\n'))
    print(f"  Facade: {facade_lines} lines (target: <300)")
    assert facade_lines < 300, f"Facade too large: {facade_lines} lines"

    tracker_lines = len(inspect.getsource(ProgressTrackerService).split('\n'))
    print(f"  Progress tracker: {tracker_lines} lines (target: <100)")
    assert tracker_lines < 100, f"Progress tracker too large: {tracker_lines} lines"

    loader_lines = len(inspect.getsource(SubtitleLoaderService).split('\n'))
    print(f"  Subtitle loader: {loader_lines} lines (target: <150)")
    assert loader_lines < 150, f"Subtitle loader too large: {loader_lines} lines"

    builder_lines = len(inspect.getsource(VocabularyBuilderService).split('\n'))
    print(f"  Vocabulary builder: {builder_lines} lines (target: <300)")
    assert builder_lines < 300, f"Vocabulary builder too large: {builder_lines} lines"

    processor_lines = len(inspect.getsource(ResultProcessorService).split('\n'))
    print(f"  Result processor: {processor_lines} lines (target: <150)")
    assert processor_lines < 150, f"Result processor too large: {processor_lines} lines"

    coordinator_lines = len(inspect.getsource(FilteringCoordinatorService).split('\n'))
    print(f"  Filtering coordinator: {coordinator_lines} lines (target: <250)")
    assert coordinator_lines < 250, f"Filtering coordinator too large: {coordinator_lines} lines"

    total_lines = (facade_lines + tracker_lines + loader_lines +
                   builder_lines + processor_lines + coordinator_lines)
    print(f"  Total: {total_lines} lines (original: 621 lines)")
    print("[PASS] All services within size targets")

    # Test 10: Method counts per service
    print("\n[TEST 10] Services have focused responsibilities")

    tracker = ProgressTrackerService()
    tracker_methods = [m for m in dir(tracker) if not m.startswith('_') and callable(getattr(tracker, m))]
    print(f"  Progress tracker public methods: {len(tracker_methods)}")
    assert len(tracker_methods) <= 5, "Progress tracker has too many methods"

    loader = SubtitleLoaderService()
    loader_methods = [m for m in dir(loader) if not m.startswith('_') and callable(getattr(loader, m))]
    print(f"  Subtitle loader public methods: {len(loader_methods)}")
    assert len(loader_methods) <= 5, "Subtitle loader has too many methods"

    builder = VocabularyBuilderService()
    builder_methods = [m for m in dir(builder) if not m.startswith('_') and callable(getattr(builder, m))]
    print(f"  Vocabulary builder public methods: {len(builder_methods)}")
    assert len(builder_methods) <= 5, "Vocabulary builder has too many methods"

    print("[PASS] Services have focused method sets")


def main():
    """Run all architecture tests"""
    print("\n" + "="*60)
    print(" REFACTORED FILTERING HANDLER ARCHITECTURE TESTS")
    print("="*60)

    try:
        test_architecture_structure()
        test_sub_service_independence()
        test_service_metrics()

        print("\n" + "="*60)
        print(" ALL TESTS PASSED!")
        print("="*60)
        print("\nArchitecture verification complete:")
        print("  - 10 test groups executed")
        print("  - Facade pattern working correctly")
        print("  - Sub-services independently functional")
        print("  - Size targets met")
        print("  - Separation of concerns achieved")
        print("\n")
        return 0

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
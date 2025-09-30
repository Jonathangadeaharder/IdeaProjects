"""
Architecture Tests for User Vocabulary Service Refactoring
Verifies the refactored service follows SOLID principles and facade pattern
"""

import pytest
from pathlib import Path


class TestUserVocabularyServiceArchitecture:
    """Test suite for user vocabulary service architecture"""

    def test_facade_initialization(self):
        """Test 1: Verify facade initializes with all sub-services"""
        from services.dataservice.user_vocabulary_service import user_vocabulary_service

        assert hasattr(user_vocabulary_service, 'repository')
        assert hasattr(user_vocabulary_service, 'word_status')
        assert hasattr(user_vocabulary_service, 'learning_progress')
        assert hasattr(user_vocabulary_service, 'learning_level')
        assert hasattr(user_vocabulary_service, 'learning_stats')
        assert hasattr(user_vocabulary_service, 'logger')

    def test_all_services_import(self):
        """Test 2: Verify all sub-services can be imported"""
        from services.user_vocabulary import (
            vocabulary_repository,
            word_status_service,
            learning_progress_service,
            learning_level_service,
            learning_stats_service
        )

        assert vocabulary_repository is not None
        assert word_status_service is not None
        assert learning_progress_service is not None
        assert learning_level_service is not None
        assert learning_stats_service is not None

    def test_facade_has_all_public_methods(self):
        """Test 3: Verify facade maintains all original public methods"""
        from services.dataservice.user_vocabulary_service import user_vocabulary_service

        required_methods = [
            'is_word_known',
            'get_known_words',
            'mark_word_learned',
            'get_learning_level',
            'set_learning_level',
            'add_known_words',
            'get_learning_statistics',
            'get_word_learning_history',
            'get_words_by_confidence',
            'remove_word',
            'get_session'
        ]

        for method in required_methods:
            assert hasattr(user_vocabulary_service, method), f"Missing method: {method}"
            assert callable(getattr(user_vocabulary_service, method))

    def test_repository_has_data_access_methods(self):
        """Test 4: Verify repository has data access methods"""
        from services.user_vocabulary import vocabulary_repository

        data_access_methods = [
            'ensure_word_exists',
            'ensure_words_exist_batch',
            'get_existing_progress_batch',
            'get_word_id'
        ]

        for method in data_access_methods:
            assert hasattr(vocabulary_repository, method), f"Missing method: {method}"
            assert callable(getattr(vocabulary_repository, method))

    def test_word_status_service_has_query_methods(self):
        """Test 5: Verify word status service has query methods"""
        from services.user_vocabulary import word_status_service

        query_methods = [
            'is_word_known',
            'get_known_words',
            'get_words_by_confidence'
        ]

        for method in query_methods:
            assert hasattr(word_status_service, method), f"Missing method: {method}"
            assert callable(getattr(word_status_service, method))

    def test_learning_progress_service_has_tracking_methods(self):
        """Test 6: Verify learning progress service has tracking methods"""
        from services.user_vocabulary import learning_progress_service

        tracking_methods = [
            'mark_word_learned',
            'add_known_words',
            'remove_word'
        ]

        for method in tracking_methods:
            assert hasattr(learning_progress_service, method), f"Missing method: {method}"
            assert callable(getattr(learning_progress_service, method))

    def test_learning_level_service_has_level_methods(self):
        """Test 7: Verify learning level service has level management methods"""
        from services.user_vocabulary import learning_level_service

        level_methods = [
            'get_learning_level',
            'set_learning_level'
        ]

        for method in level_methods:
            assert hasattr(learning_level_service, method), f"Missing method: {method}"
            assert callable(getattr(learning_level_service, method))

    def test_learning_stats_service_has_statistics_methods(self):
        """Test 8: Verify learning stats service has statistics methods"""
        from services.user_vocabulary import learning_stats_service

        stats_methods = [
            'get_learning_statistics',
            'get_word_learning_history',
            'get_words_by_confidence'
        ]

        for method in stats_methods:
            assert hasattr(learning_stats_service, method), f"Missing method: {method}"
            assert callable(getattr(learning_stats_service, method))

    def test_service_sizes(self):
        """Test 9: Verify service sizes are reasonable"""
        backend_dir = Path(__file__).parent.parent.parent.parent

        service_files = {
            'Facade': backend_dir / 'services/dataservice/user_vocabulary_service.py',
            'Repository': backend_dir / 'services/user_vocabulary/vocabulary_repository.py',
            'WordStatus': backend_dir / 'services/user_vocabulary/word_status_service.py',
            'LearningProgress': backend_dir / 'services/user_vocabulary/learning_progress_service.py',
            'LearningLevel': backend_dir / 'services/user_vocabulary/learning_level_service.py',
            'LearningStats': backend_dir / 'services/user_vocabulary/learning_stats_service.py',
        }

        max_lines = 200  # Each service should be under 200 lines
        total_lines = 0

        for name, path in service_files.items():
            assert path.exists(), f"Service file not found: {path}"
            lines = len(path.read_text().splitlines())
            total_lines += lines

            if name == 'Facade':
                # Facade should be significantly smaller than original (467 lines)
                assert lines < 150, f"Facade too large: {lines} lines (should be < 150)"
            else:
                assert lines < max_lines, f"{name} too large: {lines} lines (should be < {max_lines})"

        # Total lines can be more than original due to separation and documentation
        assert total_lines < 1000, f"Total lines too large: {total_lines} (should be < 1000)"

    def test_services_have_proper_separation(self):
        """Test 10: Verify services have proper separation of concerns"""
        from services.user_vocabulary import (
            vocabulary_repository,
            word_status_service,
            learning_progress_service,
            learning_level_service,
            learning_stats_service
        )

        # Repository should not have business logic methods
        assert not hasattr(vocabulary_repository, 'get_learning_level')
        assert not hasattr(vocabulary_repository, 'get_learning_statistics')

        # Word status service should not have write methods
        assert not hasattr(word_status_service, 'mark_word_learned')
        assert not hasattr(word_status_service, 'add_known_words')

        # Learning progress should not have statistics methods
        assert not hasattr(learning_progress_service, 'get_learning_statistics')
        assert not hasattr(learning_progress_service, 'get_learning_level')

        # Learning level should not have repository methods
        assert not hasattr(learning_level_service, 'ensure_word_exists')

        # Learning stats should not have write methods
        assert not hasattr(learning_stats_service, 'mark_word_learned')

    def test_authenticated_service_compatibility(self):
        """Test 11: Verify authenticated service still works with refactored facade"""
        from services.dataservice.authenticated_user_vocabulary_service import (
            AuthenticatedUserVocabularyService
        )

        # Can't fully test without a database session, but we can verify the class exists
        # and has the expected structure
        assert AuthenticatedUserVocabularyService is not None

        # Check that it has the expected methods
        expected_methods = [
            'is_word_known',
            'get_known_words',
            'mark_word_learned',
            'get_learning_level',
            'set_learning_level',
            'add_known_words',
            'get_learning_statistics',
            'get_word_learning_history',
            'get_words_by_confidence',
            'remove_word'
        ]

        for method in expected_methods:
            assert hasattr(AuthenticatedUserVocabularyService, method), f"Missing method: {method}"

    def test_no_circular_dependencies(self):
        """Test 12: Verify no circular dependencies between services"""
        # Import all services and check they initialize successfully
        from services.user_vocabulary import (
            vocabulary_repository,
            word_status_service,
            learning_progress_service,
            learning_level_service,
            learning_stats_service
        )
        from services.dataservice.user_vocabulary_service import user_vocabulary_service

        # If we got here without import errors, there are no circular dependencies
        assert True

    def test_services_follow_single_responsibility(self):
        """Test 13: Verify each service has a single clear responsibility"""
        backend_dir = Path(__file__).parent.parent.parent.parent

        # Define expected responsibilities (max methods per service)
        max_methods_per_service = {
            'vocabulary_repository.py': 10,  # Data access layer
            'word_status_service.py': 6,      # Query operations
            'learning_progress_service.py': 8, # Progress tracking
            'learning_level_service.py': 4,   # Level management
            'learning_stats_service.py': 6,   # Statistics
        }

        for filename, max_methods in max_methods_per_service.items():
            file_path = backend_dir / 'services/user_vocabulary' / filename
            assert file_path.exists(), f"Service file not found: {file_path}"

            content = file_path.read_text()

            # Count public methods (starts with 'async def ' or 'def ' and not '_')
            import re
            public_methods = re.findall(r'^\s+(?:async )?def ([a-z][a-z_]+)\(', content, re.MULTILINE)
            method_count = len(public_methods)

            assert method_count <= max_methods, \
                f"{filename} has too many methods: {method_count} (should be <= {max_methods})"

    def test_facade_delegates_not_implements(self):
        """Test 14: Verify facade delegates to sub-services rather than implementing logic"""
        backend_dir = Path(__file__).parent.parent.parent.parent
        facade_path = backend_dir / 'services/dataservice/user_vocabulary_service.py'

        content = facade_path.read_text()

        # Check that facade methods delegate to sub-services
        delegation_patterns = [
            'self.repository.',
            'self.word_status.',
            'self.learning_progress.',
            'self.learning_level.',
            'self.learning_stats.'
        ]

        delegation_count = sum(content.count(pattern) for pattern in delegation_patterns)

        # Facade should have at least 10 delegation calls (one per public method)
        assert delegation_count >= 10, \
            f"Facade should delegate to sub-services: {delegation_count} delegations found"

        # Facade should not have SQL queries (those should be in repository/services)
        assert 'SELECT' not in content or content.count('SELECT') < 2, \
            "Facade should not contain SQL queries"
        assert 'INSERT' not in content or content.count('INSERT') < 2, \
            "Facade should not contain SQL queries"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
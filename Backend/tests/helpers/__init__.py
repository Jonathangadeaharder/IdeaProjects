"""Test helper libraries following modern testing standards."""

# Import main helper classes for easy access
from .assertions import (
    assert_status_code,
    assert_json_response,
    assert_success_response,
    assert_validation_error,
    assert_authentication_error,
    assert_authorization_error,
    assert_not_found_error,
    assert_required_fields,
    assert_field_types,
    assert_response_structure,
    assert_list_response,
    assert_vocabulary_response_structure,
    assert_auth_response_structure,
    assert_user_response_structure,
    assert_error_response_structure,
    assert_response_time,
    assert_pagination_response,
    assert_health_response,
    AssertionContext,
)

from .auth_helpers import (
    AuthHelper,
    AsyncAuthHelper,
    AuthTestHelperAsync,  # For backward compatibility
    AuthTestScenarios,
    create_auth_fixtures,
)

from .data_builders import (
    UserBuilder,
    VocabularyConceptBuilder,
    VocabularyTranslationBuilder,
    TestDataSets,
    TestUser,
    TestVocabularyConcept,
    TestVocabularyTranslation,
    CEFRLevel,
    create_user,
    create_vocabulary_concept,
    create_vocabulary_translation,
)

__all__ = [
    # Assertion helpers
    "assert_status_code",
    "assert_json_response",
    "assert_success_response",
    "assert_validation_error",
    "assert_authentication_error",
    "assert_authorization_error",
    "assert_not_found_error",
    "assert_required_fields",
    "assert_field_types",
    "assert_response_structure",
    "assert_list_response",
    "assert_vocabulary_response_structure",
    "assert_auth_response_structure",
    "assert_user_response_structure",
    "assert_error_response_structure",
    "assert_response_time",
    "assert_pagination_response",
    "assert_health_response",
    "AssertionContext",

    # Authentication helpers
    "AuthHelper",
    "AsyncAuthHelper",
    "AuthTestHelperAsync",
    "AuthTestScenarios",
    "create_auth_fixtures",

    # Data builders
    "UserBuilder",
    "VocabularyConceptBuilder",
    "VocabularyTranslationBuilder",
    "TestDataSets",
    "TestUser",
    "TestVocabularyConcept",
    "TestVocabularyTranslation",
    "CEFRLevel",
    "create_user",
    "create_vocabulary_concept",
    "create_vocabulary_translation",
]
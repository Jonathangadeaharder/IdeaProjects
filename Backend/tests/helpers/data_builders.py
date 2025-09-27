"""Test data builders following the builder pattern for consistent test data creation."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum

from database.models import VocabularyConcept, VocabularyTranslation, Language, UserLearningProgress


class CEFRLevel(str, Enum):
    """CEFR levels for vocabulary testing."""
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


@dataclass
class TestUser:
    """Test user data structure."""
    id: Optional[str] = None
    username: str = ""
    email: str = ""
    password: str = "TestPass123!"
    is_active: bool = True
    is_superuser: bool = False
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password
        }


@dataclass
class TestVocabularyConcept:
    """Test vocabulary concept data structure."""
    id: Optional[str] = None
    word: str = ""
    level: str = "A1"
    language_code: str = "de"
    frequency_rank: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        return {
            "word": self.word,
            "level": self.level,
            "language_code": self.language_code,
            "frequency_rank": self.frequency_rank
        }


@dataclass
class TestVocabularyTranslation:
    """Test vocabulary translation data structure."""
    id: Optional[str] = None
    concept_id: str = ""
    translation: str = ""
    target_language_code: str = "en"
    confidence_score: float = 0.9
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        return {
            "concept_id": self.concept_id,
            "translation": self.translation,
            "target_language_code": self.target_language_code,
            "confidence_score": self.confidence_score
        }


class UserBuilder:
    """Builder for creating test users with sensible defaults."""

    def __init__(self):
        self._reset()

    def _reset(self):
        """Reset builder to default state."""
        unique_id = str(uuid.uuid4())[:8]
        self._user = TestUser(
            id=str(uuid.uuid4()),
            username=f"testuser_{unique_id}",
            email=f"test_{unique_id}@example.com",
            created_at=datetime.utcnow()
        )

    def with_username(self, username: str) -> UserBuilder:
        """Set custom username."""
        self._user.username = username
        return self

    def with_email(self, email: str) -> UserBuilder:
        """Set custom email."""
        self._user.email = email
        return self

    def with_password(self, password: str) -> UserBuilder:
        """Set custom password."""
        self._user.password = password
        return self

    def as_admin(self) -> UserBuilder:
        """Make user a superuser."""
        self._user.is_superuser = True
        return self

    def as_inactive(self) -> UserBuilder:
        """Make user inactive."""
        self._user.is_active = False
        return self

    def with_last_login(self, last_login: datetime = None) -> UserBuilder:
        """Set last login time."""
        self._user.last_login = last_login or datetime.utcnow()
        return self

    def build(self) -> TestUser:
        """Build the user instance."""
        user = self._user
        self._reset()
        return user


class VocabularyConceptBuilder:
    """Builder for creating test vocabulary concepts."""

    def __init__(self):
        self._reset()

    def _reset(self):
        """Reset builder to default state."""
        self._concept = TestVocabularyConcept(
            id=str(uuid.uuid4()),
            word=f"testword_{str(uuid.uuid4())[:8]}",
            created_at=datetime.utcnow()
        )

    def with_word(self, word: str) -> VocabularyConceptBuilder:
        """Set custom word."""
        self._concept.word = word
        return self

    def with_level(self, level: CEFRLevel) -> VocabularyConceptBuilder:
        """Set CEFR level."""
        self._concept.level = level.value
        return self

    def with_language(self, language_code: str) -> VocabularyConceptBuilder:
        """Set language code."""
        self._concept.language_code = language_code
        return self

    def with_frequency_rank(self, rank: int) -> VocabularyConceptBuilder:
        """Set frequency rank."""
        self._concept.frequency_rank = rank
        return self

    def build(self) -> TestVocabularyConcept:
        """Build the concept instance."""
        concept = self._concept
        self._reset()
        return concept


class VocabularyTranslationBuilder:
    """Builder for creating test vocabulary translations."""

    def __init__(self):
        self._reset()

    def _reset(self):
        """Reset builder to default state."""
        self._translation = TestVocabularyTranslation(
            id=str(uuid.uuid4()),
            concept_id=str(uuid.uuid4()),
            translation=f"translation_{str(uuid.uuid4())[:8]}",
            created_at=datetime.utcnow()
        )

    def for_concept(self, concept_id: str) -> VocabularyTranslationBuilder:
        """Set concept ID this translation belongs to."""
        self._translation.concept_id = concept_id
        return self

    def with_translation(self, translation: str) -> VocabularyTranslationBuilder:
        """Set translation text."""
        self._translation.translation = translation
        return self

    def to_language(self, language_code: str) -> VocabularyTranslationBuilder:
        """Set target language."""
        self._translation.target_language_code = language_code
        return self

    def with_confidence(self, score: float) -> VocabularyTranslationBuilder:
        """Set confidence score."""
        if not 0.0 <= score <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        self._translation.confidence_score = score
        return self

    def build(self) -> TestVocabularyTranslation:
        """Build the translation instance."""
        translation = self._translation
        self._reset()
        return translation


class TestDataSets:
    """Predefined test data sets for common testing scenarios."""

    @staticmethod
    def create_basic_user() -> TestUser:
        """Create a basic test user."""
        return UserBuilder().build()

    @staticmethod
    def create_admin_user() -> TestUser:
        """Create an admin test user."""
        return UserBuilder().as_admin().build()

    @staticmethod
    def create_german_vocabulary_set() -> list[TestVocabularyConcept]:
        """Create a set of German vocabulary concepts."""
        return [
            VocabularyConceptBuilder()
            .with_word("das Haus")
            .with_level(CEFRLevel.A1)
            .with_language("de")
            .with_frequency_rank(100)
            .build(),
            VocabularyConceptBuilder()
            .with_word("die Katze")
            .with_level(CEFRLevel.A1)
            .with_language("de")
            .with_frequency_rank(150)
            .build(),
            VocabularyConceptBuilder()
            .with_word("verstehen")
            .with_level(CEFRLevel.A2)
            .with_language("de")
            .with_frequency_rank(300)
            .build()
        ]

    @staticmethod
    def create_translations_for_concept(concept_id: str) -> list[TestVocabularyTranslation]:
        """Create translations for a given concept."""
        return [
            VocabularyTranslationBuilder()
            .for_concept(concept_id)
            .with_translation("house")
            .to_language("en")
            .with_confidence(0.95)
            .build(),
            VocabularyTranslationBuilder()
            .for_concept(concept_id)
            .with_translation("casa")
            .to_language("es")
            .with_confidence(0.90)
            .build()
        ]

    @staticmethod
    def create_multilevel_vocabulary() -> Dict[str, list[TestVocabularyConcept]]:
        """Create vocabulary concepts across different CEFR levels."""
        return {
            "A1": [
                VocabularyConceptBuilder()
                .with_word("ich")
                .with_level(CEFRLevel.A1)
                .with_language("de")
                .build(),
                VocabularyConceptBuilder()
                .with_word("du")
                .with_level(CEFRLevel.A1)
                .with_language("de")
                .build()
            ],
            "B1": [
                VocabularyConceptBuilder()
                .with_word("jedoch")
                .with_level(CEFRLevel.B1)
                .with_language("de")
                .build(),
                VocabularyConceptBuilder()
                .with_word("obwohl")
                .with_level(CEFRLevel.B1)
                .with_language("de")
                .build()
            ],
            "C1": [
                VocabularyConceptBuilder()
                .with_word("diesbezüglich")
                .with_level(CEFRLevel.C1)
                .with_language("de")
                .build()
            ]
        }


# Convenience functions for quick data creation
def create_user(**kwargs) -> TestUser:
    """Create a user with optional overrides."""
    builder = UserBuilder()
    user = builder.build()
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    return user


def create_vocabulary_concept(**kwargs) -> TestVocabularyConcept:
    """Create a vocabulary concept with optional overrides."""
    builder = VocabularyConceptBuilder()
    concept = builder.build()
    for key, value in kwargs.items():
        if hasattr(concept, key):
            setattr(concept, key, value)
    return concept


def create_vocabulary_translation(**kwargs) -> TestVocabularyTranslation:
    """Create a vocabulary translation with optional overrides."""
    builder = VocabularyTranslationBuilder()
    translation = builder.build()
    for key, value in kwargs.items():
        if hasattr(translation, key):
            setattr(translation, key, value)
    return translation
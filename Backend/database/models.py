"""
SQLAlchemy models for the LangPlug multilingual database
"""

import uuid
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from core.database import Base
from core.auth import User


class VocabularyConcept(Base):
    """Core vocabulary concepts table - language-agnostic"""
    __tablename__ = 'vocabulary_concepts'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    difficulty_level = Column(String(10), nullable=False)  # A1, A2, B1, B2, C1, C2
    semantic_category = Column(String(50))  # noun, verb, adjective, etc.
    domain = Column(String(50))  # education, technology, travel, etc.
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    translations = relationship("VocabularyTranslation", back_populates="concept")
    learning_progress = relationship("UserLearningProgress", back_populates="concept")
    word_discoveries = relationship("SessionWordDiscovery", back_populates="concept")

    __table_args__ = (
        Index('idx_concepts_difficulty', 'difficulty_level'),
        Index('idx_concepts_category', 'semantic_category'),
        Index('idx_concepts_domain', 'domain'),
        Index('idx_concepts_created', 'created_at'),
    )


class VocabularyTranslation(Base):
    """Translations for vocabulary concepts in different languages"""
    __tablename__ = 'vocabulary_translations'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    concept_id = Column(String(36), ForeignKey('vocabulary_concepts.id'), nullable=False)
    language_code = Column(String(5), nullable=False)  # de, es, en, fr, etc.
    word = Column(String(100), nullable=False)
    lemma = Column(String(100))  # Base form of the word
    gender = Column(String(10))  # der/die/das for German, el/la for Spanish
    plural_form = Column(String(100))  # Plural form if applicable
    pronunciation = Column(String(200))  # IPA or phonetic representation
    notes = Column(Text)  # Grammar notes, usage notes, etc.
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    concept = relationship("VocabularyConcept", back_populates="translations")

    __table_args__ = (
        UniqueConstraint('concept_id', 'language_code'),
        UniqueConstraint('word', 'language_code'),
        Index('idx_translations_concept', 'concept_id'),
        Index('idx_translations_language', 'language_code'),
        Index('idx_translations_word', 'word'),
        Index('idx_translations_lemma', 'lemma'),
        Index('idx_translations_word_lang', 'word', 'language_code'),
    )


class WordCategory(Base):
    """Word Categories Table"""
    __tablename__ = 'word_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    file_path = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    concept_associations = relationship("ConceptCategoryAssociation", back_populates="category")


class ConceptCategoryAssociation(Base):
    """Association between concepts and categories"""
    __tablename__ = 'concept_category_associations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    concept_id = Column(String(36), ForeignKey('vocabulary_concepts.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('word_categories.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    concept = relationship("VocabularyConcept")
    category = relationship("WordCategory", back_populates="concept_associations")

    __table_args__ = (
        UniqueConstraint('concept_id', 'category_id'),
    )


class UnknownWord(Base):
    """Unknown Words Table"""
    __tablename__ = 'unknown_words'

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String(100), nullable=False)
    lemma = Column(String(100))
    frequency_count = Column(Integer, default=1)
    first_encountered = Column(DateTime, default=func.now())
    last_encountered = Column(DateTime, default=func.now(), onupdate=func.now())
    language = Column(String(10), default='de')

    __table_args__ = (
        UniqueConstraint('word', 'language'),
        Index('idx_unknown_words_word', 'word'),
        Index('idx_unknown_words_frequency', frequency_count.desc()),
        Index('idx_unknown_words_word_lang', 'word', 'language'),
        Index('idx_unknown_words_language', 'language'),
        Index('idx_unknown_words_last_encountered', last_encountered.desc()),
        Index('idx_unknown_words_first_encountered', first_encountered.desc()),
    )


class UserLearningProgress(Base):
    """User Learning Progress Table"""
    __tablename__ = 'user_learning_progress'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), default='default_user')
    concept_id = Column(String(36), ForeignKey('vocabulary_concepts.id'), nullable=False)
    learned_at = Column(DateTime, default=func.now())
    confidence_level = Column(Integer, default=1)
    review_count = Column(Integer, default=0)
    last_reviewed = Column(DateTime)

    # Relationships
    concept = relationship("VocabularyConcept", back_populates="learning_progress")

    __table_args__ = (
        UniqueConstraint('user_id', 'concept_id'),
        Index('idx_user_progress_user', 'user_id'),
        Index('idx_ulp_concept_id', 'concept_id'),
        Index('idx_ulp_confidence', confidence_level.desc()),
        Index('idx_ulp_last_reviewed', 'last_reviewed'),
        Index('idx_ulp_review_count', review_count.desc()),
    )


class ProcessingSession(Base):
    """Processing Sessions Table"""
    __tablename__ = 'processing_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), unique=True, nullable=False)
    content_type = Column(String(50))
    content_path = Column(String(500))
    total_words = Column(Integer)
    unknown_words_found = Column(Integer)
    processing_time_seconds = Column(Float)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    word_discoveries = relationship("SessionWordDiscovery", back_populates="processing_session")

    __table_args__ = (
        Index('idx_sessions_type', 'content_type'),
        Index('idx_sessions_start_time', 'created_at'),
    )


class SessionWordDiscovery(Base):
    """Session Word Discoveries Table"""
    __tablename__ = 'session_word_discoveries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), ForeignKey('processing_sessions.session_id'), nullable=False)
    concept_id = Column(String(36), ForeignKey('vocabulary_concepts.id'), nullable=True)
    word = Column(String(100), nullable=False)
    frequency_in_session = Column(Integer, default=1)
    context_examples = Column(Text)

    # Relationships
    processing_session = relationship("ProcessingSession", back_populates="word_discoveries")
    concept = relationship("VocabularyConcept", back_populates="word_discoveries")

    __table_args__ = (
        Index('idx_session_discoveries_session', 'session_id'),
        Index('idx_swd_word', 'word'),
    )


class GameSessionRecord(Base):
    """Persistent storage for interactive game sessions"""

    __tablename__ = 'game_sessions'

    session_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    game_type = Column(String(32), nullable=False)
    difficulty = Column(String(32), nullable=False)
    video_id = Column(String(100))
    status = Column(String(32), default='active', nullable=False)
    score = Column(Integer, default=0, nullable=False)
    max_score = Column(Integer, default=0, nullable=False)
    questions_answered = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    current_question = Column(Integer, default=0, nullable=False)
    total_questions = Column(Integer, default=0, nullable=False)
    session_data = Column(Text, default='{}', nullable=False)
    start_time = Column(DateTime, default=func.now(), nullable=False)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", lazy="joined")

    __table_args__ = (
        Index('idx_game_sessions_user_start', 'user_id', 'start_time'),
    )


class UserSession(Base):
    """User Sessions Table"""
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    session_token = Column(String(128), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    last_used = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        Index('idx_sessions_token', 'session_token'),
        Index('idx_sessions_user', 'user_id'),
        Index('idx_user_sessions_user_id', 'user_id'),
        Index('idx_user_sessions_token', 'session_token'),
        Index('idx_user_sessions_expires', 'expires_at'),
        Index('idx_user_sessions_active', 'is_active'),
    )


class DatabaseMetadata(Base):
    """Database metadata table"""
    __tablename__ = 'database_metadata'

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Language(Base):
    """Supported languages table"""
    __tablename__ = 'languages'

    code = Column(String(5), primary_key=True)  # ISO 639-1 codes: de, es, en, fr, etc.
    name = Column(String(50), nullable=False)  # German, Spanish, English, French
    native_name = Column(String(50))  # Deutsch, Español, English, Français
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index('idx_languages_active', 'is_active'),
    )

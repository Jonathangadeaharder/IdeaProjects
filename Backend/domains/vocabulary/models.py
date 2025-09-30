"""
Vocabulary domain models and DTOs
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class VocabularyWordBase(BaseModel):
    """Base vocabulary word model"""
    word: str
    lemma: str
    language: str = "de"
    difficulty_level: str
    part_of_speech: Optional[str] = None
    gender: Optional[str] = None
    translation_en: Optional[str] = None
    translation_native: Optional[str] = None
    pronunciation: Optional[str] = None
    notes: Optional[str] = None
    frequency_rank: Optional[int] = None


class VocabularyWordResponse(VocabularyWordBase):
    """Vocabulary word response model"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class UserVocabularyProgressBase(BaseModel):
    """Base user vocabulary progress model"""
    is_known: bool
    confidence_level: int = 0
    review_count: int = 0


class UserVocabularyProgressResponse(UserVocabularyProgressBase):
    """User vocabulary progress response model"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    vocabulary_id: int
    lemma: str
    language: str
    first_seen_at: datetime
    last_reviewed_at: Optional[datetime] = None
    vocabulary: Optional[VocabularyWordResponse] = None


class VocabularySearchRequest(BaseModel):
    """Vocabulary search request"""
    query: str
    language: str = "de"
    limit: int = 20


class VocabularyByLevelRequest(BaseModel):
    """Request vocabulary by difficulty level"""
    level: str
    language: str = "de"
    skip: int = 0
    limit: int = 100


class MarkWordRequest(BaseModel):
    """Mark word as known/unknown request"""
    vocabulary_id: int
    is_known: bool


class BulkMarkWordsRequest(BaseModel):
    """Bulk mark words request"""
    vocabulary_ids: List[int]
    is_known: bool


class VocabularyStatsResponse(BaseModel):
    """Vocabulary statistics response"""
    total_reviewed: int
    known_words: int
    unknown_words: int
    percentage_known: float
    level_breakdown: Optional[dict] = None


class WordNotFoundRequest(BaseModel):
    """Report word not found in vocabulary"""
    word: str
    lemma: Optional[str] = None
    language: str = "de"
    context: Optional[str] = None
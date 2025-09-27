"""
Multilingual Vocabulary Service
Provides abstraction layer for vocabulary operations with UUID-based concepts
"""

import logging
from typing import Optional, Dict, List, Any
from uuid import UUID
from contextlib import asynccontextmanager

from sqlalchemy import select, func as sql_func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import AsyncSessionLocal
from database.models import (
    VocabularyConcept, VocabularyTranslation,
    Language, UserLearningProgress
)

logger = logging.getLogger(__name__)


class VocabularyService:
    """Service for multilingual vocabulary operations"""

    def __init__(self):
        pass

    @asynccontextmanager
    async def _get_session(self):
        """Get database session"""
        async with AsyncSessionLocal() as session:
            yield session

    async def get_supported_languages(self) -> List[Dict[str, Any]]:
        """Get list of supported active languages"""
        try:
            async with self._get_session() as session:
                result = await session.execute(
                    select(Language).where(Language.is_active == True)
                )
                languages = result.scalars().all()

                return [
                    {
                        "code": lang.code,
                        "name": lang.name,
                        "native_name": lang.native_name,
                        "is_active": lang.is_active
                    }
                    for lang in languages
                ]
        except Exception as e:
            logger.error(f"Error getting supported languages: {e}")
            raise

    async def get_vocabulary_stats(
        self,
        target_language: str = "de",
        translation_language: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get vocabulary statistics with multilingual support"""
        try:
            async with self._get_session() as session:
                # Initialize stats structure
                stats = {
                    "levels": {
                        "A1": {"total_words": 0, "user_known": 0},
                        "A2": {"total_words": 0, "user_known": 0},
                        "B1": {"total_words": 0, "user_known": 0},
                        "B2": {"total_words": 0, "user_known": 0},
                        "C1": {"total_words": 0, "user_known": 0},
                        "C2": {"total_words": 0, "user_known": 0}
                    },
                    "target_language": target_language,
                    "translation_language": translation_language,
                    "total_words": 0,
                    "total_known": 0
                }

                # Get total words per level
                for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
                    # Count concepts for this level
                    level_count_result = await session.execute(
                        select(sql_func.count(VocabularyConcept.id)).where(
                            VocabularyConcept.difficulty_level == level
                        )
                    )
                    level_total = level_count_result.scalar() or 0

                    # Count known words for this user and level if user provided
                    known_count = 0
                    if user_id:
                        known_count_result = await session.execute(
                            select(sql_func.count(UserLearningProgress.id)).where(
                                UserLearningProgress.user_id == str(user_id),
                                VocabularyConcept.difficulty_level == level
                            ).join(VocabularyConcept, UserLearningProgress.concept_id == VocabularyConcept.id)
                        )
                        known_count = known_count_result.scalar() or 0

                    # Update level stats
                    stats["levels"][level] = {
                        "total_words": level_total,
                        "user_known": known_count
                    }

                    stats["total_words"] += level_total
                    stats["total_known"] += known_count

                return stats

        except Exception as e:
            logger.error(f"Error getting vocabulary stats: {e}")
            raise

    async def get_vocabulary_level(
        self,
        level: str,
        target_language: str = "de",
        translation_language: Optional[str] = "es",
        limit: int = 50,
        offset: int = 0,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get vocabulary words for a specific level"""
        try:
            async with self._get_session() as session:
                # Get concepts for this level with their translations
                concepts_result = await session.execute(
                    select(VocabularyConcept)
                    .options(selectinload(VocabularyConcept.translations))
                    .where(VocabularyConcept.difficulty_level == level.upper())
                    .offset(offset)
                    .limit(limit)
                )
                concepts = concepts_result.scalars().all()

                # Get user's known concepts if user provided
                known_concept_ids = set()
                if user_id:
                    user_known_result = await session.execute(
                        select(UserLearningProgress.concept_id).where(
                            UserLearningProgress.user_id == str(user_id)
                        )
                    )
                    known_concept_ids = set(row[0] for row in user_known_result.fetchall())

                vocabulary_words = []
                known_count = 0

                for concept in concepts:
                    # Find target language translation
                    target_translation = None
                    translation_text = None

                    for trans in concept.translations:
                        if trans.language_code == target_language:
                            target_translation = trans
                        elif translation_language and trans.language_code == translation_language:
                            translation_text = trans.word

                    if not target_translation:
                        continue  # Skip if no target language translation

                    is_known = concept.id in known_concept_ids
                    if is_known:
                        known_count += 1

                    vocabulary_words.append({
                        "concept_id": concept.id,
                        "word": target_translation.word,
                        "translation": translation_text,
                        "lemma": target_translation.lemma,
                        "difficulty_level": concept.difficulty_level,
                        "semantic_category": concept.semantic_category,
                        "domain": concept.domain,
                        "gender": target_translation.gender,
                        "plural_form": target_translation.plural_form,
                        "pronunciation": target_translation.pronunciation,
                        "notes": target_translation.notes,
                        "known": is_known
                    })

                return {
                    "level": level.upper(),
                    "target_language": target_language,
                    "translation_language": translation_language,
                    "words": vocabulary_words,
                    "total_count": len(vocabulary_words),
                    "known_count": known_count
                }

        except Exception as e:
            logger.error(f"Error getting vocabulary level {level}: {e}")
            raise

    async def mark_concept_known(
        self,
        user_id: int,
        concept_id: str,
        known: bool
    ) -> Dict[str, Any]:
        """Mark a concept as known or unknown for a user"""
        try:
            async with self._get_session() as session:
                # Check if learning progress already exists
                result = await session.execute(
                    select(UserLearningProgress).where(
                        UserLearningProgress.user_id == str(user_id),
                        UserLearningProgress.concept_id == concept_id
                    )
                )
                existing_progress = result.scalar_one_or_none()

                if known:
                    if not existing_progress:
                        # Create new learning progress record
                        progress = UserLearningProgress(
                            user_id=str(user_id),
                            concept_id=concept_id,
                            confidence_level=1
                        )
                        session.add(progress)
                else:
                    if existing_progress:
                        # Remove learning progress record
                        await session.delete(existing_progress)

                await session.commit()

                return {
                    "success": True,
                    "concept_id": concept_id,
                    "known": known
                }

        except Exception as e:
            logger.error(f"Error marking concept {concept_id} as known: {e}")
            raise

    async def bulk_mark_level(
        self,
        user_id: int,
        level: str,
        target_language: str,
        known: bool
    ) -> Dict[str, Any]:
        """Mark all words in a level as known or unknown"""
        try:
            async with self._get_session() as session:
                # Get all concepts for this level
                concepts_result = await session.execute(
                    select(VocabularyConcept.id).where(
                        VocabularyConcept.difficulty_level == level.upper()
                    )
                )
                concept_ids = [row[0] for row in concepts_result.fetchall()]

                success_count = 0

                if known:
                    # Mark all as known
                    for concept_id in concept_ids:
                        # Check if already exists
                        existing_result = await session.execute(
                            select(UserLearningProgress).where(
                                UserLearningProgress.user_id == str(user_id),
                                UserLearningProgress.concept_id == concept_id
                            )
                        )
                        if not existing_result.scalar_one_or_none():
                            progress = UserLearningProgress(
                                user_id=str(user_id),
                                concept_id=concept_id,
                                confidence_level=1
                            )
                            session.add(progress)
                            success_count += 1
                else:
                    # Mark all as unknown (remove learning progress)
                    for concept_id in concept_ids:
                        existing_result = await session.execute(
                            select(UserLearningProgress).where(
                                UserLearningProgress.user_id == str(user_id),
                                UserLearningProgress.concept_id == concept_id
                            )
                        )
                        existing_progress = existing_result.scalar_one_or_none()
                        if existing_progress:
                            await session.delete(existing_progress)
                            success_count += 1

                await session.commit()

                return {
                    "success": True,
                    "level": level.upper(),
                    "target_language": target_language,
                    "known": known,
                    "word_count": success_count
                }

        except Exception as e:
            logger.error(f"Error bulk marking level {level}: {e}")
            raise

    async def _get_user_known_concepts(
        self,
        user_id: int,
        language: str
    ) -> set[str]:
        """Get set of concept IDs that the user knows"""
        try:
            async with self._get_session() as session:
                result = await session.execute(
                    select(UserLearningProgress.concept_id).where(
                        UserLearningProgress.user_id == str(user_id)
                    )
                )
                return set(row[0] for row in result.fetchall())
        except Exception as e:
            logger.error(f"Error getting user known concepts: {e}")
            return set()


# Dependency injection function
def get_vocabulary_service() -> VocabularyService:
    """Get vocabulary service instance"""
    return VocabularyService()
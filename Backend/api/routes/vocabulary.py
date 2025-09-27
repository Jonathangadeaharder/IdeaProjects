"""Multilingual vocabulary management API routes"""
import logging
from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.config import settings
from core.database import get_async_session
from core.dependencies import current_active_user
from database.models import (
    User, VocabularyConcept, VocabularyTranslation,
    Language, UserLearningProgress
)

from ..models.vocabulary import (
    VocabularyStats,
    VocabularyLevel,
    VocabularyLibraryWord,
    MarkKnownRequest,
    BulkMarkRequest,
    LanguagesResponse,
    SupportedLanguage,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["vocabulary"])


@router.get("/languages", response_model=LanguagesResponse, name="get_supported_languages")
async def get_supported_languages(
    db: AsyncSession = Depends(get_async_session)
):
    """Get list of supported languages"""
    try:
        result = await db.execute(
            select(Language).where(Language.is_active == True)
        )
        languages = result.scalars().all()

        supported_languages = [
            SupportedLanguage(
                code=lang.code,
                name=lang.name,
                native_name=lang.native_name,
                is_active=lang.is_active
            )
            for lang in languages
        ]

        return LanguagesResponse(languages=supported_languages)

    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving languages: {e}")


@router.get("/stats", response_model=VocabularyStats, name="get_vocabulary_stats")
async def get_vocabulary_stats_endpoint(
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
    target_language: str = Query("de", description="Target language code"),
    translation_language: Optional[str] = Query(None, description="Translation language code")
):
    """Get vocabulary statistics for the current user"""
    try:
        # Initialize default stats with CEFR levels
        stats = VocabularyStats(
            levels={
                "A1": {"total_words": 0, "user_known": 0},
                "A2": {"total_words": 0, "user_known": 0},
                "B1": {"total_words": 0, "user_known": 0},
                "B2": {"total_words": 0, "user_known": 0},
                "C1": {"total_words": 0, "user_known": 0},
                "C2": {"total_words": 0, "user_known": 0}
            },
            target_language=target_language,
            translation_language=translation_language,
            total_words=0,
            total_known=0
        )

        # Get total words per level
        for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
            # Count concepts for this level
            level_count_result = await db.execute(
                select(sql_func.count(VocabularyConcept.id)).where(
                    VocabularyConcept.difficulty_level == level
                )
            )
            level_total = level_count_result.scalar() or 0

            # Count known words for this user and level
            known_count_result = await db.execute(
                select(sql_func.count(UserLearningProgress.id)).where(
                    UserLearningProgress.user_id == str(current_user.id),
                    VocabularyConcept.difficulty_level == level
                ).join(VocabularyConcept, UserLearningProgress.concept_id == VocabularyConcept.id)
            )
            known_count = known_count_result.scalar() or 0

            # Update level stats
            stats.levels[level] = {
                "total_words": level_total,
                "user_known": known_count
            }

            stats.total_words += level_total
            stats.total_known += known_count

        logger.info(f"Retrieved vocabulary stats for user {current_user.id}: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Error getting vocabulary stats for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving vocabulary stats: {e}")


@router.get("/library/{level}", name="get_vocabulary_level")
async def get_vocabulary_level(
    level: str,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
    target_language: str = Query("de", description="Target language code"),
    translation_language: Optional[str] = Query("es", description="Translation language code"),
    limit: int = Query(50, description="Maximum number of words to return")
):
    """Get vocabulary words for a specific level with user's known status"""
    try:
        if level.upper() not in ["A1", "A2", "B1", "B2", "C1", "C2"]:
            raise HTTPException(status_code=422, detail="Invalid level. Must be A1, A2, B1, B2, C1, or C2")

        # Get concepts for this level with their translations
        concepts_result = await db.execute(
            select(VocabularyConcept)
            .options(selectinload(VocabularyConcept.translations))
            .where(VocabularyConcept.difficulty_level == level.upper())
            .limit(limit)
        )
        concepts = concepts_result.scalars().all()

        # Get user's known concepts
        user_known_result = await db.execute(
            select(UserLearningProgress.concept_id).where(
                UserLearningProgress.user_id == str(current_user.id)
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

            vocabulary_words.append(VocabularyLibraryWord(
                concept_id=UUID(concept.id),
                word=target_translation.word,
                translation=translation_text,
                lemma=target_translation.lemma,
                difficulty_level=concept.difficulty_level,
                semantic_category=concept.semantic_category,
                domain=concept.domain,
                gender=target_translation.gender,
                plural_form=target_translation.plural_form,
                pronunciation=target_translation.pronunciation,
                notes=target_translation.notes,
                known=is_known
            ))

        return VocabularyLevel(
            level=level.upper(),
            target_language=target_language,
            translation_language=translation_language,
            words=vocabulary_words,
            total_count=len(vocabulary_words),
            known_count=known_count
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get vocabulary level {level}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get vocabulary level: {e}")


@router.post("/mark-known", name="mark_word_known")
async def mark_word_as_known(
    request: MarkKnownRequest,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Mark a word concept as known or unknown"""
    try:
        logger.info(f"Marking concept {request.concept_id} as {'known' if request.known else 'unknown'} for user {current_user.id}")

        # Check if learning progress already exists
        result = await db.execute(
            select(UserLearningProgress).where(
                UserLearningProgress.user_id == str(current_user.id),
                UserLearningProgress.concept_id == str(request.concept_id)
            )
        )
        existing_progress = result.scalar_one_or_none()

        if request.known:
            if not existing_progress:
                # Create new learning progress record
                progress = UserLearningProgress(
                    user_id=str(current_user.id),
                    concept_id=str(request.concept_id),
                    confidence_level=1
                )
                db.add(progress)
            # If already exists, no need to update
        else:
            if existing_progress:
                # Remove learning progress record
                await db.delete(existing_progress)

        await db.commit()

        logger.info(f"Successfully updated concept status: {request.concept_id} -> {request.known}")
        return {"success": True, "concept_id": str(request.concept_id), "known": request.known}

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update word: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update word: {e}")


@router.post("/library/bulk-mark", name="bulk_mark_level")
async def bulk_mark_level_known(
    request: BulkMarkRequest,
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Mark all words in a level as known or unknown"""
    try:
        if request.level.upper() not in ["A1", "A2", "B1", "B2", "C1", "C2"]:
            raise HTTPException(status_code=400, detail="Invalid level. Must be A1, A2, B1, B2, C1, or C2")

        # Get all concepts for this level
        concepts_result = await db.execute(
            select(VocabularyConcept.id).where(
                VocabularyConcept.difficulty_level == request.level.upper()
            )
        )
        concept_ids = [row[0] for row in concepts_result.fetchall()]

        success_count = 0

        if request.known:
            # Mark all as known
            for concept_id in concept_ids:
                # Check if already exists
                existing_result = await db.execute(
                    select(UserLearningProgress).where(
                        UserLearningProgress.user_id == str(current_user.id),
                        UserLearningProgress.concept_id == concept_id
                    )
                )
                if not existing_result.scalar_one_or_none():
                    progress = UserLearningProgress(
                        user_id=str(current_user.id),
                        concept_id=concept_id,
                        confidence_level=1
                    )
                    db.add(progress)
                    success_count += 1
        else:
            # Mark all as unknown (remove learning progress)
            for concept_id in concept_ids:
                existing_result = await db.execute(
                    select(UserLearningProgress).where(
                        UserLearningProgress.user_id == str(current_user.id),
                        UserLearningProgress.concept_id == concept_id
                    )
                )
                existing_progress = existing_result.scalar_one_or_none()
                if existing_progress:
                    await db.delete(existing_progress)
                    success_count += 1

        await db.commit()

        action = "marked as known" if request.known else "unmarked"
        return {
            "success": True,
            "message": f"Successfully {action} {success_count} words in {request.level.upper()}",
            "level": request.level.upper(),
            "known": request.known,
            "word_count": success_count
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to bulk mark {request.level}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to bulk mark words: {e}")


@router.get("/test-data", name="get_test_data")
async def get_test_data(
    db: AsyncSession = Depends(get_async_session)
):
    """Get test data to verify the multilingual setup works"""
    try:
        # Get concept count
        concept_count_result = await db.execute(
            select(sql_func.count(VocabularyConcept.id))
        )
        concept_count = concept_count_result.scalar()

        # Get translation count
        translation_count_result = await db.execute(
            select(sql_func.count(VocabularyTranslation.id))
        )
        translation_count = translation_count_result.scalar()

        # Get sample translations
        sample_result = await db.execute(
            select(VocabularyTranslation.word, VocabularyTranslation.language_code).limit(10)
        )
        sample_translations = [{"word": row[0], "language": row[1]} for row in sample_result.fetchall()]

        return {
            "concept_count": concept_count,
            "translation_count": translation_count,
            "sample_translations": sample_translations
        }

    except Exception as e:
        logger.error(f"Error getting test data: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving test data: {e}")


@router.get("/blocking-words", name="get_blocking_words")
async def get_blocking_words(
    video_path: str = Query(..., description="Path to the video file"),
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get words that would block comprehension from video subtitles"""
    try:
        # Get video file path
        videos_path = settings.get_videos_path()
        video_file = videos_path / video_path

        # Look for corresponding SRT file
        srt_file = video_file.with_suffix('.srt')

        if not srt_file.exists():
            raise HTTPException(status_code=404, detail="Subtitle file not found")

        # For now, return a simple structure
        # This could be enhanced to actually parse SRT and find blocking words
        return {
            "blocking_words": [],
            "video_path": str(video_file),
            "srt_path": str(srt_file),
            "message": "Blocking words endpoint - basic implementation"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting blocking words for {video_path}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing video: {e}")
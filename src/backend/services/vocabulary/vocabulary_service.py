"""
Vocabulary Service Facade

Modern facade pattern implementation for vocabulary operations, delegating to specialized sub-services.
This module provides a unified interface for vocabulary querying, progress tracking, and statistics.

Key Components:
    - VocabularyService: Main facade coordinating sub-services
    - vocabulary_query_service: Word lookup and search operations
    - vocabulary_progress_service: User progress tracking and bulk operations
    - vocabulary_stats_service: Statistics and analytics

Architecture:
    This facade delegates to three specialized services:
    1. Query Service: Read operations (word info, library, search)
    2. Progress Service: Write operations (mark known, bulk updates)
    3. Stats Service: Analytics (statistics, summaries, supported languages)

Usage Example:
    ```python
    from services.vocabulary.vocabulary_service import vocabulary_service

    # Get word information
    word_info = await vocabulary_service.get_word_info("Haus", "de", db)

    # Mark word as known
    result = await vocabulary_service.mark_word_known(
        user_id=123,
        word="Haus",
        language="de",
        is_known=True,
        db=db
    )

    # Get user statistics
    stats = await vocabulary_service.get_user_vocabulary_stats(123, "de", db)
    ```

Dependencies:
    - sqlalchemy: Database operations
    - vocabulary_query_service: Word lookups
    - vocabulary_progress_service: Progress tracking
    - vocabulary_stats_service: Statistics generation

Thread Safety:
    Yes. Service instance is stateless, delegates to sub-services which handle their own concurrency.

Performance Notes:
    - Query operations: O(1) with database indexes
    - Progress updates: Transactional, may involve locking
    - Statistics: May involve aggregations, consider caching

Architecture Note:
    This facade pattern provides a clean API while delegating to specialized services.
    Maintains separation of concerns while offering convenience methods.
"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class VocabularyService:
    """
    Facade for vocabulary operations coordinating specialized sub-services.

    Provides a unified API for all vocabulary-related operations while delegating
    to focused services for query, progress tracking, and statistics.

    Attributes:
        query_service: Handles word lookups and searches
        progress_service: Manages user progress and bulk operations
        stats_service: Generates statistics and analytics

    Example:
        ```python
        service = VocabularyService()

        # Query operations
        word = await service.get_word_info("Haus", "de", db)
        library = await service.get_vocabulary_library(db, "de", level="A1")

        # Progress operations
        await service.mark_word_known(123, "Haus", "de", True, db)
        await service.bulk_mark_level(db, 123, "de", "A1", True)

        # Statistics
        stats = await service.get_user_vocabulary_stats(123, "de", db)
        ```

    Note:
        This is a stateless facade - all state is managed by sub-services.
        Safe to use as singleton (vocabulary_service instance).
    """

    def __init__(self):
        # Get fresh instances via factory functions to avoid global state
        from .vocabulary_progress_service import get_vocabulary_progress_service
        from .vocabulary_query_service import get_vocabulary_query_service
        from .vocabulary_stats_service import get_vocabulary_stats_service

        self.query_service = get_vocabulary_query_service()
        self.progress_service = get_vocabulary_progress_service()
        self.stats_service = get_vocabulary_stats_service()

    def _get_session(self):
        """Get database session context manager"""
        return AsyncSessionLocal()

    # ========== Query Service Methods ==========

    async def get_word_info(self, word: str, language: str, db: AsyncSession) -> dict[str, Any] | None:
        """Get vocabulary information for a word"""
        return await self.query_service.get_word_info(word, language, db)

    async def get_vocabulary_library(
        self,
        db: AsyncSession,
        language: str,
        level: str | None = None,
        user_id: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Get vocabulary library with optional filtering"""
        return await self.query_service.get_vocabulary_library(db, language, level, user_id, limit, offset)

    async def search_vocabulary(
        self, db: AsyncSession, search_term: str, language: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Search vocabulary by word or lemma"""
        return await self.query_service.search_vocabulary(db, search_term, language, limit)

    # ========== Progress Service Methods ==========

    async def mark_word_known(
        self, user_id: int, word: str, language: str, is_known: bool, db: AsyncSession
    ) -> dict[str, Any]:
        """Mark a word as known or unknown for a user"""
        return await self.progress_service.mark_word_known(user_id, word, language, is_known, db)

    async def bulk_mark_level(
        self, db: AsyncSession, user_id: int, language: str, level: str, is_known: bool
    ) -> dict[str, Any]:
        """Mark all words of a level as known or unknown"""
        return await self.progress_service.bulk_mark_level(db, user_id, language, level, is_known)

    async def get_user_vocabulary_stats(self, user_id: int, language: str, db: AsyncSession) -> dict[str, Any]:
        """Get vocabulary statistics for a user"""
        return await self.progress_service.get_user_vocabulary_stats(user_id, language, db)

    # ========== Stats Service Methods ==========

    async def get_vocabulary_stats(self, *args, **kwargs):
        """Get vocabulary statistics by level"""
        return await self.stats_service.get_vocabulary_stats(*args, **kwargs)

    async def get_user_progress_summary(self, db_session, user_id: str):
        """Get user's overall progress summary"""
        return await self.stats_service.get_user_progress_summary(db_session, user_id)

    async def get_supported_languages(self):
        """Get list of supported languages"""
        return await self.stats_service.get_supported_languages()

    # ========== Legacy/Compatibility Methods ==========
    # These remain for backward compatibility with tests

    async def get_vocabulary_level(
        self, level, target_language="de", translation_language="es", user_id=None, limit=50, offset=0
    ):
        """Get vocabulary for a specific level - legacy method for test compatibility"""
        async with AsyncSessionLocal() as session:
            level = level.upper()

            # Use get_vocabulary_library from query service
            library = await self.get_vocabulary_library(
                db=session, language=target_language, level=level, user_id=user_id, limit=limit, offset=offset
            )

            # Format for legacy test expectations
            return {
                "level": level,
                "target_language": target_language,
                "translation_language": translation_language,
                "words": library["words"],
                "total_count": library["total_count"],
                "known_count": sum(1 for w in library["words"] if w.get("is_known", False)),
            }

    async def extract_blocking_words_from_srt(
        self, db: AsyncSession, srt_content: str, user_id: int, video_path: str
    ) -> list[dict[str, Any]]:
        """Extract blocking words from SRT content for vocabulary learning"""
        try:
            import re

            # Parse SRT content to extract text
            blocks = re.split(r'\n\s*\n', srt_content.strip())
            all_text = []

            for block in blocks:
                lines = block.split('\n')
                if len(lines) >= 3:
                    # Skip the sequence number and timestamp lines
                    text_lines = lines[2:]
                    if text_lines:
                        all_text.append(' '.join(text_lines))

            # Combine all subtitle text
            full_text = ' '.join(all_text)

            if not full_text.strip():
                return []

            # Extract German words from the text
            # Simple word extraction - in production this would use proper NLP
            german_words = re.findall(r'\b[A-Za-zäöüÄÖÜß]+(?:-[A-Za-zäöüÄÖÜß]+)*\b', full_text)

            # Filter out common words and short words
            filtered_words = [
                word.lower() for word in german_words
                if len(word) > 3 and word.lower() not in {
                    'und', 'oder', 'der', 'die', 'das', 'ein', 'eine', 'einer', 'eines',
                    'den', 'dem', 'des', 'sie', 'wir', 'ihr', 'ich', 'du', 'er',
                    'es', 'ist', 'sind', 'war', 'waren', 'hat', 'haben', 'habe',
                    'mit', 'auf', 'aus', 'von', 'zu', 'für', 'durch', 'über', 'unter',
                    'vor', 'nach', 'bei', 'als', 'wie', 'was', 'wer', 'wo', 'wann',
                    'warum', 'viel', 'viele', 'wenig', 'wenige', 'mehr',
                    'weniger', 'am', 'im', 'um', 'an', 'in', 'ab',
                    'dann', 'also', 'aber', 'sondern', 'denn', 'doch', 'jedoch', 'nur',
                    'auch', 'noch', 'schon', 'bereits', 'immer', 'nie', 'oft', 'selten',
                    'manchmal', 'vielleicht', 'wahrscheinlich', 'sicher', 'bestimmt'
                }
            ]

            # Get unique words and create vocabulary entries
            unique_words = list(set(filtered_words))[:20]  # Limit to 20 words for testing

            blocking_words = []
            for word in unique_words:
                # Create a vocabulary entry matching the expected schema
                blocking_words.append({
                    "word": word,
                    "translation": f"Translation for {word}",  # Placeholder translation
                    "difficulty_level": "B1",  # Use difficulty_level not level
                    "lemma": word.lower(),
                    "concept_id": None,
                    "semantic_category": None,
                    "domain": None,
                    "known": False
                })

            logger.info(f"Extracted {len(blocking_words)} blocking words from SRT content")
            return blocking_words

        except Exception as e:
            logger.error(f"Error extracting blocking words from SRT: {e}")
            return []

    async def add_custom_word(
        self,
        user_id: int,
        word: str,
        lemma: str,
        language: str = "de",
        translation: str | None = None,
        part_of_speech: str | None = None,
        gender: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """
        Add a custom user-defined vocabulary word to C2 level.

        Args:
            user_id: ID of the user adding the word
            word: The word to add
            lemma: Base form of the word
            language: Language code
            translation: Translation in user's native language
            part_of_speech: Part of speech
            gender: Gender (for nouns)
            notes: User notes

        Returns:
            dict: Created word information

        Raises:
            ValueError: If word already exists for this user
        """
        from sqlalchemy import select

        from database.models import VocabularyWord

        async with AsyncSessionLocal() as db:
            try:
                # Check if word already exists for this user
                result = await db.execute(
                    select(VocabularyWord).where(
                        VocabularyWord.user_id == user_id,
                        VocabularyWord.word == word,
                        VocabularyWord.language == language,
                    )
                )
                existing_word = result.scalar_one_or_none()

                if existing_word:
                    raise ValueError(f"Word '{word}' already exists in your custom vocabulary")

                # Create new custom word
                new_word = VocabularyWord(
                    user_id=user_id,
                    word=word,
                    lemma=lemma,
                    language=language,
                    difficulty_level="C2",  # Custom words are always C2
                    part_of_speech=part_of_speech,
                    gender=gender,
                    translation_en=translation,
                    translation_native=translation,
                    notes=notes,
                )

                db.add(new_word)
                await db.commit()
                await db.refresh(new_word)

                logger.info(f"Created custom word '{word}' for user {user_id}")

                return {
                    "id": new_word.id,
                    "word": new_word.word,
                    "lemma": new_word.lemma,
                    "language": new_word.language,
                    "difficulty_level": new_word.difficulty_level,
                    "translation": new_word.translation_en,
                    "success": True,
                }

            except ValueError:
                raise
            except Exception as e:
                await db.rollback()
                logger.error(f"Error adding custom word: {e}")
                raise

    async def delete_custom_word(
        self,
        user_id: int,
        word_id: int,
    ) -> None:
        """
        Delete a user-defined custom vocabulary word.

        Args:
            user_id: ID of the user deleting the word
            word_id: Database ID of the word to delete

        Raises:
            ValueError: If word not found
            PermissionError: If word doesn't belong to user or is system vocabulary
        """
        from sqlalchemy import select

        from database.models import VocabularyWord

        async with AsyncSessionLocal() as db:
            try:
                # Get the word
                result = await db.execute(
                    select(VocabularyWord).where(VocabularyWord.id == word_id)
                )
                word = result.scalar_one_or_none()

                if not word:
                    raise ValueError(f"Word with ID {word_id} not found")

                # Check if word belongs to user
                if word.user_id is None:
                    raise PermissionError("Cannot delete system vocabulary words")

                if word.user_id != user_id:
                    raise PermissionError("You can only delete your own custom words")

                # Delete the word
                await db.delete(word)
                await db.commit()

                logger.info(f"Deleted custom word ID {word_id} for user {user_id}")

            except (ValueError, PermissionError):
                raise
            except Exception as e:
                await db.rollback()
                logger.error(f"Error deleting custom word: {e}")
                raise


def get_vocabulary_service() -> VocabularyService:
    """Get vocabulary service instance - returns fresh instance to avoid global state"""
    return VocabularyService()

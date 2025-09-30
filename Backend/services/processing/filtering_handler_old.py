"""
Subtitle filtering handler service
Extracted from api/routes/processing.py for better separation of concerns
"""

import logging
import time
import uuid
from inspect import isawaitable
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from services.filterservice.direct_subtitle_processor import DirectSubtitleProcessor
from services.filterservice.interface import FilteredSubtitle, FilteredWord, FilteringResult
from services.nlp.lemma_resolver import lemmatize_word
from services.interfaces.handler_interface import IFilteringHandler
from api.models.processing import ProcessingStatus, VocabularyWord
from utils.srt_parser import SRTParser

logger = logging.getLogger(__name__)


class FilteringHandler(IFilteringHandler):
    """Handles subtitle filtering operations for vocabulary extraction"""

    def __init__(self, subtitle_processor: DirectSubtitleProcessor = None):
        self.subtitle_processor = subtitle_processor or DirectSubtitleProcessor()

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the filtering handler"""
        return {
            "service": "FilteringHandler",
            "status": "healthy",
            "subtitle_processor": "available"
        }

    async def handle(
        self,
        task_id: str,
        task_progress: Dict[str, Any],
        **kwargs
    ) -> None:
        """Handle filtering task - delegates to filter_subtitles"""
        await self.filter_subtitles(
            task_id=task_id,
            task_progress=task_progress,
            **kwargs
        )

    def validate_parameters(self, **kwargs) -> bool:
        """Validate input parameters for filtering"""
        required_params = ['srt_path', 'user_id']
        return all(param in kwargs for param in required_params)

    def _update_progress(
        self,
        task_progress: Dict[str, Any],
        task_id: str,
        progress: float,
        current_step: str,
        message: str
    ) -> None:
        """Update progress tracking with consistent pattern"""
        task_progress[task_id].progress = progress
        task_progress[task_id].current_step = current_step
        task_progress[task_id].message = message

    async def filter_subtitles(
        self,
        srt_path: str,
        task_id: str,
        task_progress: Dict[str, Any],
        user_id: str,
        user_level: str = "A1",
        target_language: str = "de"
    ) -> Dict[str, Any]:
        """
        Filter subtitles to extract vocabulary and learning content

        Args:
            srt_path: Path to SRT file
            task_id: Unique task identifier
            task_progress: Progress tracking dictionary
            user_id: User ID for personalized filtering
            user_level: User's language proficiency level
            target_language: Target language for filtering

        Returns:
            Dictionary containing filtering results
        """
        try:
            logger.info(f"Starting filtering task: {task_id}")

            # Initialize progress tracking
            task_progress[task_id] = ProcessingStatus(
                status="processing",
                progress=0.0,
                current_step="Starting filtering...",
                message="Loading subtitle file",
                started_at=int(time.time()),
            )

            # Step 1: Load and parse SRT file
            subtitles = await self._load_and_prepare_subtitles(
                srt_path, task_progress, task_id
            )

            # Step 2: Apply filtering (20-80% progress)
            filtering_result = await self._apply_filtering(
                subtitles,
                task_progress,
                task_id,
                user_id,
                user_level,
                target_language
            )

            # Step 3: Process results (80-95% progress)
            processed_results = await self._process_filtering_results(
                filtering_result,
                task_progress,
                task_id
            )

            # Step 4: Save filtered results
            await self._save_filtered_results(
                processed_results,
                srt_path,
                task_progress,
                task_id
            )

            # Mark as complete
            task_progress[task_id].status = "completed"
            task_progress[task_id].progress = 100.0
            task_progress[task_id].message = "Filtering completed successfully"
            task_progress[task_id].result = processed_results
            task_progress[task_id].completed_at = int(time.time())

            logger.info(f"Filtering task {task_id} completed successfully")
            return processed_results

        except Exception as e:
            logger.error(f"Filtering task {task_id} failed: {e}")
            task_progress[task_id].status = "failed"
            task_progress[task_id].error = str(e)
            task_progress[task_id].message = f"Filtering failed: {str(e)}"
            raise

    async def _load_and_prepare_subtitles(
        self,
        srt_path: str,
        task_progress: Dict[str, Any],
        task_id: str
    ) -> List[FilteredSubtitle]:
        """Load and convert SRT to FilteredSubtitle objects"""
        self._update_progress(
            task_progress, task_id, 10.0,
            "Loading subtitles...", "Parsing subtitle file"
        )

        srt_file = Path(srt_path)
        if not srt_file.exists():
            raise FileNotFoundError(f"SRT file not found: {srt_path}")

        # Parse SRT file
        segments = SRTParser.parse_file(str(srt_file))
        if not segments:
            raise ValueError("No subtitle segments found")

        # Convert to FilteredSubtitle objects
        subtitles = []
        for segment in segments:
            words = self._extract_words_from_text(
                segment.text,
                segment.start_time,
                segment.end_time
            )

            subtitle = FilteredSubtitle(
                original_text=segment.text,
                start_time=segment.start_time,
                end_time=segment.end_time,
                words=words
            )
            subtitles.append(subtitle)

        logger.info(f"Prepared {len(subtitles)} subtitles for filtering")
        return subtitles

    def _extract_words_from_text(
        self,
        text: str,
        start_time: float,
        end_time: float
    ) -> List:
        """Extract words from subtitle text"""
        # This is a simplified version
        # The actual implementation would use the subtitle processor's method
        import re
        word_pattern = re.compile(r'\b\w+\b')
        words = word_pattern.findall(text.lower())

        # Distribute timing evenly among words
        duration = end_time - start_time
        word_duration = duration / max(len(words), 1)

        word_objects = []
        for i, word in enumerate(words):
            word_start = start_time + (i * word_duration)
            word_end = word_start + word_duration
            # Create word object (would use FilteredWord in real implementation)
            word_objects.append({
                "text": word,
                "start_time": word_start,
                "end_time": word_end
            })

        return word_objects

    async def _apply_filtering(
        self,
        subtitles: List[FilteredSubtitle],
        task_progress: Dict[str, Any],
        task_id: str,
        user_id: str,
        user_level: str,
        target_language: str
    ) -> FilteringResult:
        """Apply filtering logic to subtitles"""
        self._update_progress(
            task_progress, task_id, 20.0,
            "Filtering content...", f"Analyzing {len(subtitles)} subtitles"
        )

        # Use the subtitle processor to filter
        user_id_str = str(user_id)

        filtering_result = await self.subtitle_processor.process_subtitles(
            subtitles,
            user_id=user_id_str,
            user_level=user_level,
            language=target_language
        )

        # Update progress
        task_progress[task_id].progress = 80.0
        task_progress[task_id].message = (
            f"Found {len(filtering_result.blocker_words)} vocabulary words"
        )

        return filtering_result

    def _get_or_compute_lemma(
        self,
        word_text: str,
        blocker_text: str,
        target_language: str,
        lemma_cache: Dict[str, Optional[str]]
    ) -> Optional[str]:
        """Get lemma from cache or compute it"""
        resolved_lemma = lemma_cache.get(word_text)
        if word_text not in lemma_cache:
            resolved_lemma = lemmatize_word(blocker_text, target_language)
            lemma_cache[word_text] = resolved_lemma
        return resolved_lemma

    async def _lookup_concept_from_db(
        self,
        candidate_values: Tuple[str, ...],
        target_language: str,
        session
    ) -> Optional[Tuple]:
        """Look up concept from database by candidate forms"""
        from database.models import VocabularyWord
        from sqlalchemy import func, or_, select

        stmt = (
            select(
                VocabularyWord.id,
                VocabularyWord.difficulty_level,
                VocabularyWord.word,
                VocabularyWord.lemma,
            )
            .where(
                VocabularyWord.language == target_language,
                or_(
                    func.lower(VocabularyWord.word).in_(candidate_values),
                    func.lower(VocabularyWord.lemma).in_(candidate_values),
                ),
            )
            .limit(1)
        )

        result = await session.execute(stmt)
        row = result.first()
        if isawaitable(row):
            row = await row
        return row

    def _create_cache_entry(
        self,
        concept_id: Optional[Any],
        level: Optional[str],
        db_word: Optional[str],
        db_lemma: Optional[str],
        resolved_lemma: Optional[str]
    ) -> Dict[str, Optional[Any]]:
        """Create cache entry for concept lookup"""
        return {
            "concept_id": concept_id,
            "level": level,
            "db_word": db_word,
            "db_lemma": db_lemma,
            "resolved_lemma": resolved_lemma,
        }

    def _create_vocabulary_word(
        self,
        blocker_text: str,
        final_lemma: str,
        target_language: str,
        cached_level: Optional[str],
        blocker_metadata: Dict,
        concept_id: Optional[Any],
        return_dict: bool
    ) -> Any:
        """Create VocabularyWord object from blocker and concept info"""
        from database.models import VocabularyWord

        vocab_word = VocabularyWord(
            word=blocker_text,
            lemma=final_lemma,
            language=target_language,
            difficulty_level=(
                cached_level
                or blocker_metadata.get("difficulty_level")
                or "C2"
            ),
            translation_en=""
        )

        if concept_id:
            vocab_word.id = concept_id

        return vocab_word.dict() if return_dict else vocab_word

    async def _build_vocabulary_words(
        self,
        blocker_words: List[FilteredWord],
        target_language: str,
        return_dict: bool = True
    ) -> List[Any]:
        """Convert blocker words to VocabularyWord objects with real concept IDs."""
        from core.database import AsyncSessionLocal

        vocabulary_words: List[Any] = []
        concept_cache: Dict[str, Dict[str, Optional[Any]]] = {}
        lemma_cache: Dict[str, Optional[str]] = {}

        async with AsyncSessionLocal() as session:
            for blocker in blocker_words:
                word_text = blocker.text.lower()

                # Check cache first
                cache_entry = concept_cache.get(word_text)
                if cache_entry is not None:
                    concept_id = cache_entry["concept_id"]
                    cached_level = cache_entry["level"]
                    cached_word = cache_entry["db_word"]
                    cached_lemma = cache_entry["db_lemma"]
                    resolved_lemma = cache_entry.get("resolved_lemma")
                else:
                    # Get or compute lemma
                    resolved_lemma = self._get_or_compute_lemma(
                        word_text, blocker.text, target_language, lemma_cache
                    )

                    # Generate candidate forms for lookup
                    candidate_values = self._generate_candidate_forms(
                        word_text, resolved_lemma, target_language
                    )

                    # Look up concept in database
                    row = await self._lookup_concept_from_db(
                        candidate_values, target_language, session
                    )

                    # Process lookup result
                    if row:
                        concept_uuid = uuid.UUID(str(row[0]))
                        logger.info(
                            "Mapped blocker word '%s' (lemma '%s') -> concept %s (word='%s', lemma='%s', level=%s)",
                            blocker.text,
                            resolved_lemma or word_text,
                            concept_uuid,
                            row[2],
                            row[3],
                            row[1],
                        )
                        concept_id, cached_level, cached_word, cached_lemma = (
                            concept_uuid, row[1], row[2], row[3]
                        )
                    else:
                        logger.warning(
                            "Concept not found for word '%s' (lemma '%s') in language '%s'",
                            blocker.text,
                            resolved_lemma or word_text,
                            target_language,
                        )
                        concept_id, cached_level, cached_word, cached_lemma = (
                            None, None, None, None
                        )

                    # Cache the result
                    concept_cache[word_text] = self._create_cache_entry(
                        concept_id, cached_level, cached_word, cached_lemma, resolved_lemma
                    )

                # Create vocabulary word
                final_lemma = cached_lemma or resolved_lemma or word_text
                vocab_word = self._create_vocabulary_word(
                    blocker.text,
                    final_lemma,
                    target_language,
                    cached_level,
                    blocker.metadata,
                    concept_id,
                    return_dict
                )
                vocabulary_words.append(vocab_word)

        return vocabulary_words

    async def _process_filtering_results(
        self,
        filtering_result: FilteringResult,
        task_progress: Dict[str, Any],
        task_id: str
    ) -> Dict[str, Any]:
        """Process and format filtering results"""
        self._update_progress(
            task_progress, task_id, 85.0,
            "Processing results...", "Formatting vocabulary data"
        )

        target_language = filtering_result.statistics.get("language", "de")

        vocabulary_words = await self._build_vocabulary_words(
            filtering_result.blocker_words,
            target_language,
            return_dict=True
        )

        # Format results
        results = {
            "vocabulary_words": vocabulary_words,
            "learning_subtitles": len(filtering_result.learning_subtitles),
            "total_words": filtering_result.statistics.get("total_words", 0),
            "active_words": filtering_result.statistics.get("active_words", 0),
            "filter_rate": filtering_result.statistics.get("filter_rate", 0),
            "statistics": filtering_result.statistics
        }

        return results

    async def _save_filtered_results(
        self,
        results: Dict[str, Any],
        srt_path: str,
        task_progress: Dict[str, Any],
        task_id: str
    ) -> None:
        """Save filtered results to file"""
        self._update_progress(
            task_progress, task_id, 95.0,
            "Saving results...", "Creating filtered output files"
        )

        # Save vocabulary list
        import json
        output_path = Path(srt_path).with_suffix('.vocabulary.json')

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        task_progress[task_id].result_path = str(output_path)
        logger.info(f"Saved filtering results to {output_path}")

    async def extract_blocking_words(
        self,
        srt_path: str,
        user_id: str,
        user_level: str = "A1"
    ) -> List[VocabularyWord]:
        """
        Extract blocking vocabulary words from subtitles

        Args:
            srt_path: Path to SRT file
            user_id: User ID
            user_level: User's language level

        Returns:
            List of vocabulary words that block comprehension
        """
        # Quick extraction without full progress tracking
        subtitles = await self._load_and_prepare_subtitles(
            srt_path,
            {},  # Empty progress dict
            "quick-extract"
        )

        filtering_result = await self.subtitle_processor.process_subtitles(
            subtitles,
            user_id=str(user_id),
            user_level=user_level,
            language="de"
        )

        target_language = filtering_result.statistics.get("language", "de")

        return await self._build_vocabulary_words(
            filtering_result.blocker_words,
            target_language,
            return_dict=False
        )

    async def refilter_for_translations(
        self,
        srt_path: str,
        user_id: str,
        known_words: List[str],
        user_level: str = "A1",
        target_language: str = "de"
    ) -> Dict[str, Any]:
        """
        Second-pass filtering to determine which subtitles still need translations
        after vocabulary words have been marked as known.

        Args:
            srt_path: Path to SRT file
            user_id: User ID
            known_words: List of words now marked as known
            user_level: User's language level
            target_language: Target language

        Returns:
            Dictionary with subtitle indices that still need translations
        """
        logger.info(f"Refiltering subtitles for user {user_id} with {len(known_words)} known words")

        # Load and parse subtitles
        subtitles = await self._load_and_prepare_subtitles(
            srt_path,
            {},  # Empty progress dict
            "refilter"
        )

        # Get initial filtering result to identify blockers
        filtering_result = await self.subtitle_processor.process_subtitles(
            subtitles,
            user_id=str(user_id),
            user_level=user_level,
            language=target_language
        )

        # Create a set of known words for fast lookup (lowercase for comparison)
        known_words_set = {word.lower() for word in known_words}

        # Determine which subtitle indices still need translations
        needs_translation = []
        for idx, subtitle in enumerate(subtitles):
            # Check if this subtitle has blocking words that are NOT in known_words
            has_unknown_blockers = False

            # Extract words from subtitle text
            subtitle_words = self._extract_words_from_text(
                subtitle.original_text,
                subtitle.start_time,
                subtitle.end_time
            )

            # Check each word in the subtitle
            for word_obj in subtitle_words:
                word_text = word_obj["text"].lower()

                # Check if this word was identified as a blocker
                is_blocker = any(
                    blocker.text.lower() == word_text
                    for blocker in filtering_result.blocker_words
                )

                # If it's a blocker and NOT known, subtitle needs translation
                if is_blocker and word_text not in known_words_set:
                    has_unknown_blockers = True
                    break

            if has_unknown_blockers:
                needs_translation.append(idx)

        # Return result
        result = {
            "total_subtitles": len(subtitles),
            "needs_translation": needs_translation,
            "translation_count": len(needs_translation),
            "known_words_applied": list(known_words),
            "filtering_stats": {
                "total_blockers": len(filtering_result.blocker_words),
                "known_blockers": len([
                    w for w in filtering_result.blocker_words
                    if w.text.lower() in known_words_set
                ]),
                "unknown_blockers": len([
                    w for w in filtering_result.blocker_words
                    if w.text.lower() not in known_words_set
                ])
            }
        }

        logger.info(
            f"Refiltering complete: {result['translation_count']}/{result['total_subtitles']} "
            f"subtitles still need translation"
        )

        return result

    def estimate_duration(self, srt_path: str) -> int:
        """
        Estimate filtering duration in seconds

        Args:
            srt_path: Path to SRT file

        Returns:
            Estimated duration in seconds
        """
        try:
            segments = SRTParser.parse_file(srt_path)
            # Estimate: 0.5 seconds per segment
            return max(20, len(segments) // 2)
        except:
            return 30  # Default estimate

    def _generate_candidate_forms(
        self,
        word_text: str,
        resolved_lemma: Optional[str],
        language: str,
    ) -> Tuple[str, ...]:
        word_text = (word_text or "").strip().lower()
        forms: Set[str] = {word_text}

        if resolved_lemma:
            forms.add(resolved_lemma.strip().lower())

        if language.lower() == "de":
            forms.update(self._german_heuristic_forms(word_text))

        return tuple(sorted({form for form in forms if form}))

    @staticmethod
    def _german_heuristic_forms(word_text: str) -> Set[str]:
        forms: Set[str] = set()

        # Common adjective/adverb endings (comparative/superlative/case inflections)
        adjective_suffixes = (
            "erer",
            "eren",
            "erem",
            "ere",
            "er",
            "em",
            "en",
            "es",
            "e",
            "st",
            "ste",
            "sten",
            "ster",
            "stes",
            "stem",
        )

        for suffix in adjective_suffixes:
            if word_text.endswith(suffix) and len(word_text) - len(suffix) >= 3:
                forms.add(word_text[: -len(suffix)])

        noun_suffixes = ("ern", "er", "en", "e", "n", "s")
        for suffix in noun_suffixes:
            if word_text.endswith(suffix) and len(word_text) - len(suffix) >= 3:
                forms.add(word_text[: -len(suffix)])

        return forms

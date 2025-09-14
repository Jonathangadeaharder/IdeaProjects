"""
Difficulty Level Filter
Identifies words above the user's current level as learning targets
"""

from typing import Set, Optional, Dict, Any
from .interface import FilteredWord, WordStatus
from .filter_chain import BaseSubtitleFilter
from database.database_manager import DatabaseManager

import logging
logger = logging.getLogger(__name__)


class DifficultyLevelFilter(BaseSubtitleFilter):
    """
    Identifies words that are above the user's current level as learning targets.
    Words at or below the user's level are filtered out, words above become "blocking words".
    """
    
    def __init__(self, db_manager: DatabaseManager, user_level: str = "A1", target_language: str = "de"):
        super().__init__()
        self.db_manager = db_manager
        self.user_level = user_level.upper()
        self.target_language = target_language
        
        # Cache for word difficulty levels
        self._word_difficulty_cache: Dict[str, str] = {}
        self._cache_initialized = False
        
        # Level hierarchy (higher number = more difficult)
        self._level_hierarchy = {
            "A1": 1,
            "A2": 2, 
            "B1": 3,
            "B2": 4,
            "C1": 5,
            "C2": 6
        }
        
        # Statistics
        self._words_checked = 0
        self._blocking_words_found = 0
        self._known_level_words_filtered = 0
        self._unknown_words = 0
        
    @property
    def filter_name(self) -> str:
        return f"DifficultyLevelFilter({self.user_level})"
    
    def _initialize_cache(self):
        """Load word difficulty levels from vocabulary database"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT word, difficulty_level 
                    FROM vocabulary 
                    WHERE language = ?
                """, (self.target_language,))
                
                rows = cursor.fetchall()
                self._word_difficulty_cache = {
                    row[0].lower(): row[1].upper() 
                    for row in rows
                }
                
                self._cache_initialized = True
                logger.info(f"Initialized difficulty cache with {len(self._word_difficulty_cache)} words")
                
        except Exception as e:
            logger.error(f"Failed to initialize difficulty cache: {e}")
            self._word_difficulty_cache = {}
            self._cache_initialized = False
    
    def _ensure_cache_initialized(self):
        """Ensure cache is initialized before use"""
        if not self._cache_initialized:
            self._initialize_cache()
    
    def _get_word_difficulty_level(self, word: str) -> Optional[str]:
        """Get difficulty level for a word"""
        self._ensure_cache_initialized()
        return self._word_difficulty_cache.get(word.lower().strip())
    
    def _is_word_above_user_level(self, word: str) -> bool:
        """Check if word is above user's current level"""
        word_level = self._get_word_difficulty_level(word)
        
        if not word_level:
            # Unknown word - could be above user level
            return True
            
        user_level_num = self._level_hierarchy.get(self.user_level, 1)
        word_level_num = self._level_hierarchy.get(word_level, 1)
        
        return word_level_num > user_level_num
    
    def _should_filter_word(self, word: FilteredWord, subtitle) -> bool:
        """
        Filter words that are at or below user's level.
        Words above user's level remain active as "blocking words".
        """
        self._words_checked += 1
        text = word.text.lower().strip()
        
        logger.info(f"[DifficultyFilter] Checking word: '{text}'")
        
        # Skip very short words
        if len(text) < 3:
            logger.info(f"[DifficultyFilter] Filtering short word: '{text}'")
            return True
            
        word_level = self._get_word_difficulty_level(text)
        logger.info(f"[DifficultyFilter] Word '{text}' difficulty level: {word_level}")
        
        if word_level is None:
            # Unknown word - treat as potentially above user level
            self._unknown_words += 1
            logger.info(f"[DifficultyFilter] Unknown word '{text}' - treating as blocking word")
            return False  # Don't filter - keep as blocking word
        
        user_level_num = self._level_hierarchy.get(self.user_level, 1)
        word_level_num = self._level_hierarchy.get(word_level, 1)
        
        if word_level_num > user_level_num:
            # Word is above user level - keep as blocking word
            self._blocking_words_found += 1
            logger.info(f"[DifficultyFilter] ✅ BLOCKING WORD: '{text}' (level {word_level} > {self.user_level})")
            return False  # Don't filter - keep as blocking word
        else:
            # Word is at or below user level - filter it out
            self._known_level_words_filtered += 1
            logger.info(f"[DifficultyFilter] Filtering known level word: '{text}' (level {word_level} <= {self.user_level})")
            return True  # Filter out
    
    def _get_filter_status(self):
        return WordStatus.FILTERED_KNOWN
    
    def _get_filter_reason(self, word: FilteredWord) -> str:
        word_level = self._get_word_difficulty_level(word.text)
        if word_level:
            return f"Word level {word_level} is at or below user level {self.user_level}"
        else:
            return f"Word at or below user level {self.user_level}"
    
    def get_statistics(self):
        base_stats = super().get_statistics()
        base_stats.update({
            "user_level": self.user_level,
            "target_language": self.target_language,
            "words_checked": self._words_checked,
            "blocking_words_found": self._blocking_words_found,
            "known_level_words_filtered": self._known_level_words_filtered,
            "unknown_words": self._unknown_words,
            "cache_size": len(self._word_difficulty_cache),
            "cache_initialized": self._cache_initialized
        })
        return base_stats

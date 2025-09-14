import logging

logger = logging.getLogger(__name__)

"""
Subtitle Filter Chain Implementation
Chain of Command pattern for processing subtitles
"""

from typing import List, Dict, Any
from .interface import ISubtitleFilter, ISubtitleFilterChain, FilteredSubtitle, FilteringResult, FilteredWord, WordStatus


class SubtitleFilterChain(ISubtitleFilterChain):
    """
    Implementation of the subtitle filter chain
    Processes subtitles through a sequence of filters using Chain of Command pattern
    """
    
    def __init__(self):
        self._filters: List[ISubtitleFilter] = []
        self._statistics: Dict[str, Dict[str, Any]] = {}
    
    def add_filter(self, filter_impl: ISubtitleFilter) -> 'SubtitleFilterChain':
        """Add a filter to the chain"""
        self._filters.append(filter_impl)
        return self
    
    def process(self, subtitles: List[FilteredSubtitle]) -> FilteringResult:
        """
        Process subtitles through the entire filter chain
        """
        # Start with input subtitles
        current_subtitles = subtitles.copy()
        
        # Apply each filter in sequence
        for filter_impl in self._filters:
            logger.debug(f"Applying filter: {filter_impl.filter_name}")
            
            # Apply filter
            current_subtitles = filter_impl.filter(current_subtitles)
            
            # Collect statistics
            self._statistics[filter_impl.filter_name] = filter_impl.get_statistics()
        
        # Categorize results after all filters have been applied
        return self._categorize_results(current_subtitles)
    
    def get_filter_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics from all filters in the chain"""
        return self._statistics.copy()
    
    async def process_file(self, srt_file_path: str, user_id: int) -> Dict[str, Any]:
        """
        Process an SRT file through the filter chain
        
        Args:
            srt_file_path: Path to the SRT subtitle file
            user_id: User ID for personalized filtering
            
        Returns:
            Dictionary with filtered results
        """
        try:
            # Import SRT parser and vocabulary model
            from ..utils.srt_parser import SRTParser
            from api.models.vocabulary import VocabularyWord
            import re
            
            logger.info(f"Processing SRT file: {srt_file_path}")
            
            # 1. Parse the SRT file
            srt_segments = SRTParser.parse_file(srt_file_path)
            logger.info(f"Parsed {len(srt_segments)} subtitle segments")
            
            # 2. Convert to FilteredSubtitle objects
            filtered_subtitles = []
            for segment in srt_segments:
                # Extract words from the text
                words = self._extract_words_from_text(segment.text, segment.start_time, segment.end_time)
                
                # Create FilteredSubtitle object
                filtered_subtitle = FilteredSubtitle(
                    original_text=segment.text,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    words=words
                )
                filtered_subtitles.append(filtered_subtitle)
            
            logger.info(f"Created {len(filtered_subtitles)} FilteredSubtitle objects")
            
            # 3. Run through the filter chain
            filtering_result = self.process(filtered_subtitles)
            
            # 4. Convert blocker words to VocabularyWord objects
            blocking_words = []
            for word in filtering_result.blocker_words:
                vocab_word = VocabularyWord(
                    word=word.text,
                    definition="",  # Definition would be filled by vocabulary service
                    difficulty_level="Unknown",  # Would be determined by difficulty analysis
                    known=False
                )
                blocking_words.append(vocab_word)
            
            # 5. Return categorized results
            return {
                "blocking_words": blocking_words,
                "learning_subtitles": filtering_result.learning_subtitles,
                "empty_subtitles": filtering_result.empty_subtitles,
                "statistics": {
                    **filtering_result.statistics,
                    "user_id": user_id,
                    "file_processed": srt_file_path,
                    "segments_parsed": len(srt_segments)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing file {srt_file_path}: {e}", exc_info=True)
            return {
                "blocking_words": [],
                "learning_subtitles": [], 
                "empty_subtitles": [],
                "statistics": {"error": str(e)}
            }
    
    def _categorize_results(self, subtitles: List[FilteredSubtitle]) -> FilteringResult:
        """
        Categorize filtered subtitles into learning content, blockers, and empty
        """
        learning_subtitles = []
        blocker_words = []
        empty_subtitles = []
        
        total_words = 0
        active_words = 0
        filtered_words = 0
        
        for subtitle in subtitles:
            total_words += len(subtitle.words)
            active_words += len(subtitle.active_words)
            filtered_words += len(subtitle.words) - len(subtitle.active_words)
            
            if subtitle.has_learning_content:
                # Subtitle has 2+ active words - good for learning
                learning_subtitles.append(subtitle)
            elif subtitle.is_blocker:
                # Single active word - collect as blocker
                blocker_words.extend(subtitle.active_words)
            else:
                # No active words - empty subtitle
                empty_subtitles.append(subtitle)
        
        # Compile statistics
        statistics = {
            "total_subtitles": len(subtitles),
            "learning_subtitles": len(learning_subtitles),
            "blocker_subtitles": len(blocker_words),
            "empty_subtitles": len(empty_subtitles),
            "total_words": total_words,
            "active_words": active_words,
            "filtered_words": filtered_words,
            "filter_rate": filtered_words / max(total_words, 1),
            "learning_rate": len(learning_subtitles) / max(len(subtitles), 1)
        }
        
        return FilteringResult(
            learning_subtitles=learning_subtitles,
            blocker_words=blocker_words,
            empty_subtitles=empty_subtitles,
            statistics=statistics
        )
    
    def _extract_words_from_text(self, text: str, start_time: float, end_time: float) -> List[FilteredWord]:
        """Extract words from subtitle text and create FilteredWord objects
        
        Args:
            text: Subtitle text
            start_time: Start time of subtitle
            end_time: End time of subtitle
            
        Returns:
            List of FilteredWord objects
        """
        import re
        
        # Simple word extraction - split by whitespace and punctuation
        # This could be enhanced with more sophisticated tokenization
        word_pattern = re.compile(r'\b\w+\b')
        word_matches = word_pattern.finditer(text.lower())
        
        words = []
        total_words = len(list(word_pattern.finditer(text.lower())))
        
        # Estimate timing for each word (simple linear distribution)
        duration = end_time - start_time
        word_duration = duration / max(total_words, 1)
        
        for i, match in enumerate(word_pattern.finditer(text.lower())):
            word_text = match.group()
            word_start = start_time + (i * word_duration)
            word_end = word_start + word_duration
            
            filtered_word = FilteredWord(
                text=word_text,
                start_time=word_start,
                end_time=word_end,
                status=WordStatus.ACTIVE,  # Start as active, filters will modify
                filter_reason=None,
                confidence=None,
                metadata={}
            )
            words.append(filtered_word)
            
        return words


class BaseSubtitleFilter(ISubtitleFilter):
    """
    Base class for subtitle filters with common functionality
    """
    
    def __init__(self):
        self._processed_words = 0
        self._filtered_words = 0
    
    def filter(self, subtitles: List[FilteredSubtitle]) -> List[FilteredSubtitle]:
        """
        Apply filter with statistics tracking
        """
        self._processed_words = 0
        self._filtered_words = 0
        
        for subtitle in subtitles:
            for word in subtitle.words:
                self._processed_words += 1
                
                # Only process words that are still active
                if word.status.value == "active":
                    if self._should_filter_word(word, subtitle):
                        word.status = self._get_filter_status()
                        word.filter_reason = self._get_filter_reason(word)
                        self._filtered_words += 1
        
        return subtitles
    
    def _should_filter_word(self, word: FilteredWord, subtitle: FilteredSubtitle) -> bool:
        """
        Override in subclasses to implement filtering logic
        """
        return False
    
    def _get_filter_status(self):
        """
        Override in subclasses to return appropriate WordStatus
        """
        from .interface import WordStatus
        return WordStatus.FILTERED_OTHER
    
    def _get_filter_reason(self, word: FilteredWord) -> str:
        """
        Override in subclasses to provide filter reason
        """
        return f"Filtered by {self.filter_name}"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics for this filter"""
        return {
            "processed_words": self._processed_words,
            "filtered_words": self._filtered_words,
            "filter_rate": self._filtered_words / max(self._processed_words, 1)
        }
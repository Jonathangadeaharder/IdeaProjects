"""Vocabulary management API routes"""
import logging
import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..models.vocabulary import (
    VocabularyWord, MarkKnownRequest, VocabularyLibraryWord, 
    VocabularyLevel, BulkMarkRequest, VocabularyStats
)
from core.dependencies import get_current_user, get_database_manager, get_subtitle_processor
from core.config import settings
from services.authservice.models import AuthUser
from services.vocabulary_preload_service import VocabularyPreloadService
from services.utils.srt_parser import SRTParser

logger = logging.getLogger(__name__)
router = APIRouter(tags=["vocabulary"])


async def extract_blocking_words_for_segment(
    srt_path: str, start: int, duration: int, user_id: int
) -> List[VocabularyWord]:
    """Extract blocking words from a specific time segment"""
    try:
        # Parse the SRT file
        srt_parser = SRTParser()
        segments = srt_parser.parse_file(srt_path)
        
        # Filter segments within the time range
        end_time = start + duration
        relevant_segments = [
            seg for seg in segments 
            if seg.start_time <= end_time and seg.end_time >= start
        ]
        
        if not relevant_segments:
            logger.warning(f"No segments found for time range {start}-{end_time}")
            return []
        
        # Get subtitle processor for processing
        from core.dependencies import get_subtitle_processor, get_auth_service
        from services.authservice.models import AuthUser
        
        # Get the actual user from database using user_id
        auth_service = get_auth_service()
        try:
            # Get user by ID from database
            with auth_service.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
                user_row = cursor.fetchone()
                
                if user_row:
                    current_user = AuthUser(
                        id=user_row[0],
                        username=user_row[1]
                    )
                else:
                    # Raise error if user not found
                    raise ValueError(f"User with id {user_id} not found in database")
        except Exception as e:
            logger.error(f"Could not get user from database: {e}")
            raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
        
        # Use subtitle processor for vocabulary extraction
        subtitle_processor = get_subtitle_processor()
        
        # Process segments through subtitle processor to get blocking words
        result = await subtitle_processor.process_file(srt_path, user_id)
        
        # Check for processing errors first
        if "error" in result.get("statistics", {}):
            error_msg = result["statistics"]["error"]
            logger.error(f"[VOCABULARY ERROR] Subtitle processing failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Vocabulary extraction failed: {error_msg}")
        
        # Extract blocking words from the result
        blocking_words = result.get("blocking_words", [])
        
        logger.info(f"Found {len(blocking_words)} blocking words for user {user_id} in segment {start}-{end_time}")
        
        # Filter words that fall within our time segment
        # Note: This is a simplified approach - in a more sophisticated implementation,
        # you'd track word timing more precisely
        segment_words = []
        for word in blocking_words:
            # For now, include all blocking words from relevant segments
            # This could be enhanced to check actual word timing
            segment_words.append(word)
        
        return segment_words[:10]  # Limit to 10 words for UI performance
        
    except Exception as e:
        logger.error(f"Error in extract_blocking_words_for_segment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Vocabulary extraction failed: {str(e)}")


@router.get("/stats", response_model=VocabularyStats)
async def get_vocabulary_stats_endpoint(
    current_user: AuthUser = Depends(get_current_user),
    db_manager = Depends(get_database_manager)
):
    """Get vocabulary statistics for the current user"""
    try:
        
        # Get user's vocabulary data from database or file system
        user_vocab_path = settings.get_user_data_path() / str(current_user.id) / "vocabulary"
        
        # Initialize default stats
        stats = VocabularyStats(
            total_words=0,
            known_words=0,
            learning_words=0,
            mastered_words=0,
            words_today=0,
            streak_days=0,
            level_progress=0.0
        )
        
        if user_vocab_path.exists():
            # Count vocabulary files or database entries
            vocab_files = list(user_vocab_path.glob("*.json"))
            stats.total_words = len(vocab_files)
            
            # Calculate known/learning/mastered based on file contents
            known_count = 0
            learning_count = 0
            mastered_count = 0
            
            for vocab_file in vocab_files:
                try:
                    with open(vocab_file, 'r', encoding='utf-8') as f:
                        vocab_data = json.load(f)
                        status = vocab_data.get('status', 'learning')
                        if status == 'known':
                            known_count += 1
                        elif status == 'mastered':
                            mastered_count += 1
                        else:
                            learning_count += 1
                except Exception:
                    learning_count += 1  # Default to learning if file is corrupted
            
            stats.known_words = known_count
            stats.learning_words = learning_count
            stats.mastered_words = mastered_count
            
            # Calculate level progress (percentage of known + mastered words)
            if stats.total_words > 0:
                stats.level_progress = ((known_count + mastered_count) / stats.total_words) * 100
        
        logger.info(f"Retrieved vocabulary stats for user {current_user.id}: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting vocabulary stats for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving vocabulary stats: {str(e)}")


@router.get("/blocking-words")
async def get_blocking_words(
    video_path: str,
    segment_start: int = 0,
    segment_duration: int = 300,  # 5 minutes default
    current_user: AuthUser = Depends(get_current_user)
):
    """Get top blocking words for a video segment"""
    try:
        logger.info(f"Getting blocking words for user {current_user.id}, video: {video_path}")
        
        # Get subtitle file path - handle both relative and full paths
        if video_path.startswith('/'):
            video_file = Path(video_path)
        else:
            video_file = settings.get_videos_path() / video_path
        
        srt_file = video_file.with_suffix(".srt")
        
        # If subtitle file doesn't exist, raise error
        if not srt_file.exists():
            logger.error(f"Subtitle file not found: {srt_file}")
            raise HTTPException(status_code=404, detail="Subtitle file not found")
        
        # Extract blocking words for the specific segment
        blocking_words = await extract_blocking_words_for_segment(
            str(srt_file), segment_start, segment_duration, current_user.id
        )
        
        logger.info(f"Found {len(blocking_words)} blocking words for segment")
        return {"blocking_words": blocking_words[:10]}  # Return top 10
        
    except Exception as e:
        logger.error(f"Error in get_blocking_words: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get blocking words: {str(e)}")


@router.post("/mark-known")
async def mark_word_as_known(
    request: MarkKnownRequest,
    current_user: AuthUser = Depends(get_current_user),
    db_manager = Depends(get_database_manager)
):
    """Mark a word as known or unknown"""
    try:
        logger.info(f"Marking word '{request.word}' as {'known' if request.known else 'unknown'} for user {current_user.id}")
        
        # Use the underlying SQLiteUserVocabularyService directly for simplicity
        from services.dataservice.user_vocabulary_service import SQLiteUserVocabularyService
        vocab_service = SQLiteUserVocabularyService(db_manager)
        
        if request.known:
            success = vocab_service.mark_word_learned(str(current_user.id), request.word, "de")
        else:
            success = vocab_service.remove_word(str(current_user.id), request.word, "de")
        
        logger.info(f"Successfully updated word status: {request.word} -> {request.known}")
        return {"success": success, "word": request.word, "known": request.known}
        
    except Exception as e:
        logger.error(f"Failed to update word: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update word: {str(e)}")


@router.post("/preload")
async def preload_vocabulary(
    current_user: AuthUser = Depends(get_current_user),
    db_manager = Depends(get_database_manager)
):
    """Preload vocabulary data from text files into database (Admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        service = VocabularyPreloadService(db_manager)
        results = service.load_vocabulary_files()
        
        total_loaded = sum(results.values())
        logger.info(f"Preloaded vocabulary: {results}")
        
        return {
            "success": True,
            "message": f"Loaded {total_loaded} words across all levels",
            "levels": results
        }
        
    except Exception as e:
        logger.error(f"Failed to preload vocabulary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to preload vocabulary: {str(e)}")


@router.get("/library/stats")
async def get_vocabulary_stats(
    current_user: AuthUser = Depends(get_current_user),
    db_manager = Depends(get_database_manager)
):
    """Get vocabulary statistics for all levels"""
    try:
        service = VocabularyPreloadService(db_manager)
        
        # Get basic stats
        stats = service.get_vocabulary_stats()
        
        # Add user-specific known word counts
        total_words = 0
        total_known = 0
        
        for level in ["A1", "A2", "B1", "B2"]:
            known_words = service.get_user_known_words(current_user.id, level)
            if level in stats:
                stats[level]["user_known"] = len(known_words)
                total_words += stats[level]["total_words"]
                total_known += len(known_words)
            else:
                stats[level] = {"total_words": 0, "user_known": 0}
        
        return VocabularyStats(
            levels=stats,
            total_words=total_words,
            total_known=total_known
        )
        
    except Exception as e:
        logger.error(f"Failed to get vocabulary stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get vocabulary stats: {str(e)}")


@router.get("/library/{level}")
async def get_vocabulary_level(
    level: str,
    current_user: AuthUser = Depends(get_current_user),
    db_manager = Depends(get_database_manager)
):
    """Get all vocabulary words for a specific level with user's known status"""
    try:
        if level.upper() not in ["A1", "A2", "B1", "B2"]:
            raise HTTPException(status_code=400, detail="Invalid level. Must be A1, A2, B1, or B2")
        
        service = VocabularyPreloadService(db_manager)
        
        # Get words for level
        level_words = service.get_level_words(level.upper())
        
        # Get user's known words for this level
        known_words = service.get_user_known_words(current_user.id, level.upper())
        
        # Combine data
        vocabulary_words = []
        known_count = 0
        
        for word_data in level_words:
            is_known = word_data.get("word", "") in known_words
            if is_known:
                known_count += 1
                
            vocabulary_words.append(VocabularyLibraryWord(
                id=word_data.get("id"),
                word=word_data.get("word", ""),
                difficulty_level=word_data.get("difficulty_level", level.upper()),
                part_of_speech=word_data.get("part_of_speech") or word_data.get("word_type", "noun"),
                definition=word_data.get("definition", ""),
                known=is_known
            ))
        
        return VocabularyLevel(
            level=level.upper(),
            words=vocabulary_words,
            total_count=len(vocabulary_words),
            known_count=known_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get vocabulary level {level}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get vocabulary level: {str(e)}")


@router.post("/library/bulk-mark")
async def bulk_mark_level_known(
    request: BulkMarkRequest,
    current_user: AuthUser = Depends(get_current_user),
    db_manager = Depends(get_database_manager)
):
    """Mark all words in a level as known or unknown"""
    try:
        if request.level.upper() not in ["A1", "A2", "B1", "B2"]:
            raise HTTPException(status_code=400, detail="Invalid level. Must be A1, A2, B1, or B2")
        
        service = VocabularyPreloadService(db_manager)
        success_count = service.bulk_mark_level_known(current_user.id, request.level.upper(), request.known)
        
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
        logger.error(f"Failed to bulk mark {request.level}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to bulk mark words: {str(e)}")
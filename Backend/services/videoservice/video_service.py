"""
Video service for handling video-related business logic
"""
import logging
from pathlib import Path
from typing import List, Dict, Any

from api.models.video import VideoInfo
from api.models.vocabulary import VocabularyWord
from core.config import settings

logger = logging.getLogger(__name__)


class VideoService:
    """Service class for video-related operations"""
    
    def __init__(self, db_manager, auth_service):
        self.db = db_manager
        self.auth_service = auth_service
    
    def get_available_videos(self) -> List[VideoInfo]:
        """Get list of available videos/series"""
        try:
            videos_path = settings.get_videos_path()
            videos = []
            
            logger.info(f"Scanning for videos in: {videos_path}")
            
            if not videos_path.exists():
                logger.warning(f"Videos path does not exist: {videos_path}")
                return videos
            
            # First, scan for video files directly in videos_path
            for video_file in videos_path.glob("*.mp4"):
                # Check for corresponding subtitle file
                srt_file = video_file.with_suffix(".srt")
                has_subtitles = srt_file.exists()
                
                # Extract episode information from filename
                filename = video_file.stem
                episode_info = self._parse_episode_filename(filename)
                
                video_info = VideoInfo(
                    series="Default",
                    season=episode_info.get("season", "1"),
                    episode=episode_info.get("episode", filename),
                    title=episode_info.get("title", filename),
                    path=str(video_file.relative_to(videos_path)),
                    has_subtitles=has_subtitles
                )
                videos.append(video_info)
                logger.debug(f"Added video: {video_info.title}")
            
            # Also scan for series directories
            for series_dir in videos_path.iterdir():
                if series_dir.is_dir():
                    series_name = series_dir.name
                    logger.debug(f"Found series directory: {series_name}")
                    
                    # Scan for video files
                    for video_file in series_dir.glob("*.mp4"):
                        # Check for corresponding subtitle file
                        srt_file = video_file.with_suffix(".srt")
                        has_subtitles = srt_file.exists()
                        
                        # Extract episode information from filename
                        filename = video_file.stem
                        episode_info = self._parse_episode_filename(filename)
                        
                        video_info = VideoInfo(
                            series=series_name,
                            season=episode_info.get("season", "1"),
                            episode=episode_info.get("episode", "Unknown"),
                            title=episode_info.get("title", filename),
                            path=str(video_file.relative_to(videos_path)),
                            has_subtitles=has_subtitles
                        )
                        videos.append(video_info)
                        logger.debug(f"Added video: {video_info.title}")
            
            logger.info(f"Found {len(videos)} videos")
            return videos
            
        except Exception as e:
            logger.error(f"Error scanning videos: {str(e)}", exc_info=True)
            raise Exception(f"Error scanning videos: {str(e)}")
    
    def _parse_episode_filename(self, filename: str) -> Dict[str, str]:
        """Parse episode information from filename"""
        # Simple parsing - can be enhanced
        parts = filename.split()
        episode_info = {"title": filename}
        
        for i, part in enumerate(parts):
            if "episode" in part.lower() and i + 1 < len(parts):
                episode_info["episode"] = parts[i + 1]
            elif "staffel" in part.lower() and i + 1 < len(parts):
                episode_info["season"] = parts[i + 1]
        
        return episode_info
    
    def get_subtitle_file_path(self, subtitle_path: str) -> Path:
        """Convert subtitle path to actual file path, handling Windows absolute paths"""
        videos_root = settings.get_videos_path()
        
        if subtitle_path.startswith(("C:", "D:", "/mnt/c/", "/mnt/d/")) or "\\" in subtitle_path:
            # This is an absolute Windows path - convert to relative
            path_obj = Path(subtitle_path.replace("\\", "/"))
            
            # Find the videos directory in the path and get the relative part
            path_parts = path_obj.parts
            try:
                videos_index = next(i for i, part in enumerate(path_parts) if part.lower() == "videos")
                relative_path = Path(*path_parts[videos_index + 1:])
                subtitle_file = videos_root / relative_path
                logger.info(f"Converted absolute path {subtitle_path} to relative: {relative_path}")
            except (StopIteration, IndexError):
                logger.warning(f"Could not find 'videos' directory in path: {subtitle_path}")
                subtitle_file = videos_root / Path(subtitle_path).name
        else:
            # Regular relative path handling
            subtitle_file = videos_root / subtitle_path
        
        return subtitle_file
    
    def get_video_file_path(self, series: str, episode: str) -> Path:
        """Get video file path for a series and episode"""
        videos_path = settings.get_videos_path() / series
        if not videos_path.exists():
            raise Exception(f"Series '{series}' not found")
        
        # Find matching video file
        for video_file in videos_path.glob("*.mp4"):
            # More flexible matching - check if episode number is in filename
            # This handles both "1" matching "Episode 1" and full episode names
            filename_lower = video_file.name.lower()
            episode_lower = episode.lower()
            
            # Try different matching patterns
            matches = (
                f"episode {episode_lower}" in filename_lower or  # "episode 1"
                f"episode_{episode_lower}" in filename_lower or  # "episode_1"
                f"e{episode_lower}" in filename_lower or         # "e1"
                episode_lower in filename_lower                  # direct match
            )
            
            if matches:
                return video_file
        
        raise Exception(f"Episode '{episode}' not found in series '{series}'")
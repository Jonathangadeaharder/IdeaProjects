"""
Video service for handling video-related business logic
"""
import logging
from pathlib import Path

from api.models.video import VideoInfo
from core.config import settings

logger = logging.getLogger(__name__)


class VideoService:
    """Service class for video-related operations"""

    def __init__(self, db_manager, auth_service):
        self.db = db_manager
        self.auth_service = auth_service

    def get_available_videos(self) -> list[VideoInfo]:
        """Get list of available videos/series"""
        try:
            videos_path = settings.get_videos_path()
            videos = []

            logger.info(f"Scanning for videos in: {videos_path}")
            logger.info(f"Videos path absolute: {videos_path.resolve()}")

            if not videos_path.exists():
                logger.error(f"Videos path does not exist: {videos_path}")
                logger.error(f"Attempted absolute path: {videos_path.resolve()}")
                return videos

            if not videos_path.is_dir():
                logger.error(f"Videos path exists but is not a directory: {videos_path}")
                return videos

            # Check if directory is accessible
            try:
                list(videos_path.iterdir())
            except PermissionError:
                logger.error(f"Permission denied accessing videos directory: {videos_path}")
                return videos
            except Exception as e:
                logger.error(f"Error accessing videos directory {videos_path}: {e}")
                return videos

            # First, scan for video files directly in videos_path
            direct_videos = list(videos_path.glob("*.mp4"))
            logger.info(f"Found {len(direct_videos)} direct video files in {videos_path}")

            for video_file in direct_videos:
                try:
                    # Check for corresponding subtitle file
                    srt_file = video_file.with_suffix(".srt")
                    has_subtitles = srt_file.exists()

                    # Extract episode information from filename
                    filename = video_file.stem
                    episode_info = self._parse_episode_filename(filename)

                    # Ensure episode field doesn't exceed 20 character limit
                    episode = episode_info.get("episode", filename)
                    if len(episode) > 20:
                        episode = episode[:17] + "..."

                    video_info = VideoInfo(
                        series="Default",
                        season=episode_info.get("season", "1"),
                        episode=episode,
                        title=episode_info.get("title", filename),
                        path=str(video_file.relative_to(videos_path)),
                        has_subtitles=has_subtitles
                    )
                    videos.append(video_info)
                    logger.info(f"Added direct video: {video_info.title} (series: {video_info.series})")
                except Exception as e:
                    logger.error(f"Error processing direct video file {video_file}: {e}")

            # Also scan for series directories
            series_dirs = [d for d in videos_path.iterdir() if d.is_dir()]
            logger.info(f"Found {len(series_dirs)} series directories: {[d.name for d in series_dirs]}")

            for series_dir in series_dirs:
                try:
                    series_name = series_dir.name
                    logger.info(f"Scanning series directory: {series_name}")

                    # Scan for video files in series directory
                    series_videos = list(series_dir.glob("*.mp4"))
                    logger.info(f"Found {len(series_videos)} videos in series '{series_name}'")

                    for video_file in series_videos:
                        try:
                            # Check for corresponding subtitle file
                            srt_file = video_file.with_suffix(".srt")
                            has_subtitles = srt_file.exists()

                            # Extract episode information from filename
                            filename = video_file.stem
                            episode_info = self._parse_episode_filename(filename)

                            # Ensure episode field doesn't exceed 20 character limit
                            episode = episode_info.get("episode", "Unknown")
                            if len(episode) > 20:
                                episode = episode[:17] + "..."

                            video_info = VideoInfo(
                                series=series_name,
                                season=episode_info.get("season", "1"),
                                episode=episode,
                                title=episode_info.get("title", filename),
                                path=str(video_file.relative_to(videos_path)),
                                has_subtitles=has_subtitles
                            )
                            videos.append(video_info)
                            logger.info(f"Added series video: {video_info.title} (series: {video_info.series}, episode: {video_info.episode})")
                        except Exception as e:
                            logger.error(f"Error processing video file {video_file} in series {series_name}: {e}")
                except Exception as e:
                    logger.error(f"Error processing series directory {series_dir}: {e}")

            logger.info(f"Total videos found: {len(videos)}")
            if len(videos) == 0:
                logger.warning("No videos were found! Check directory structure and file permissions.")
                logger.info("Expected structure: videos/[SeriesName]/episode.mp4 or videos/episode.mp4")

            return videos

        except Exception as e:
            logger.error(f"Error scanning videos: {e!s}", exc_info=True)
            raise Exception(f"Error scanning videos: {e!s}")

    def _parse_episode_filename(self, filename: str) -> dict[str, str]:
        """Parse episode information from filename using regex patterns"""
        import re

        episode_info = {"title": filename}

        # Handle empty or very short filenames
        if not filename or len(filename.strip()) < 2:
            return episode_info

        # Episode patterns (case insensitive) - handle spaces, underscores, dots
        episode_patterns = [
            r'episode[\s_\.]*(\d+)',  # "Episode 5", "Episode_7", "episode.15"
            r'ep[\s_\.]*(\d+)',       # "Ep 5", "Ep_7", "ep.15"
            r'e(\d+)',                # "E5"
        ]

        # Season patterns (case insensitive) - handle spaces, underscores, dots
        season_patterns = [
            r'season[\s_\.]*(\d+)',   # "Season 3", "Season_3", "season.3"
            r'staffel[\s_\.]*(\d+)',  # "Staffel 3", "Staffel_3" (German)
            r's(\d+)',                # "S3"
        ]

        # Search for episode numbers
        for pattern in episode_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                episode_info["episode"] = match.group(1)
                break

        # Search for season numbers
        for pattern in season_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                episode_info["season"] = match.group(1)
                break

        # Only include episode/season keys if we found actual numbers
        # Remove if only keywords without numbers were found
        if "episode" in episode_info and not episode_info["episode"].isdigit():
            del episode_info["episode"]
        if "season" in episode_info and not episode_info["season"].isdigit():
            del episode_info["season"]

        return episode_info

    def scan_videos_directory(self) -> dict[str, any]:
        """Scan and return detailed information about the videos directory"""
        try:
            videos_path = settings.get_videos_path()

            result = {
                "videos_path": str(videos_path),
                "videos_path_absolute": str(videos_path.resolve()),
                "path_exists": videos_path.exists(),
                "is_directory": videos_path.is_dir() if videos_path.exists() else False,
                "direct_videos": [],
                "series_directories": [],
                "total_videos": 0,
                "errors": []
            }

            logger.info(f"Detailed scan of videos directory: {videos_path}")

            if not videos_path.exists():
                error_msg = f"Videos directory does not exist: {videos_path}"
                logger.error(error_msg)
                result["errors"].append(error_msg)
                return result

            if not videos_path.is_dir():
                error_msg = f"Videos path exists but is not a directory: {videos_path}"
                logger.error(error_msg)
                result["errors"].append(error_msg)
                return result

            # Scan direct video files
            try:
                direct_videos = list(videos_path.glob("*.mp4"))
                result["direct_videos"] = [str(v.name) for v in direct_videos]
                result["total_videos"] += len(direct_videos)
                logger.info(f"Found {len(direct_videos)} direct videos")
            except Exception as e:
                error_msg = f"Error scanning direct videos: {e}"
                logger.error(error_msg)
                result["errors"].append(error_msg)

            # Scan series directories
            try:
                for item in videos_path.iterdir():
                    if item.is_dir():
                        series_info = {
                            "name": item.name,
                            "path": str(item),
                            "videos": []
                        }

                        try:
                            series_videos = list(item.glob("*.mp4"))
                            series_info["videos"] = [v.name for v in series_videos]
                            result["total_videos"] += len(series_videos)
                            logger.info(f"Found {len(series_videos)} videos in series '{item.name}'")
                        except Exception as e:
                            error_msg = f"Error scanning series {item.name}: {e}"
                            logger.error(error_msg)
                            result["errors"].append(error_msg)

                        result["series_directories"].append(series_info)
            except Exception as e:
                error_msg = f"Error scanning series directories: {e}"
                logger.error(error_msg)
                result["errors"].append(error_msg)

            logger.info(f"Scan complete. Total videos: {result['total_videos']}")
            return result

        except Exception as e:
            logger.error(f"Fatal error during video scan: {e}", exc_info=True)
            return {
                "error": f"Fatal error during scan: {e}",
                "videos_path": str(settings.get_videos_path()) if settings else "Unknown"
            }

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
        from fastapi import HTTPException
        
        videos_path = settings.get_videos_path() / series
        if not videos_path.exists():
            raise HTTPException(status_code=404, detail=f"Series '{series}' not found")

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

        raise HTTPException(status_code=404, detail=f"Episode '{episode}' not found in series '{series}'")

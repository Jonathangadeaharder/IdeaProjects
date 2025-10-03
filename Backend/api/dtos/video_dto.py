"""
Video Data Transfer Objects
API request/response models for video management
"""

from pydantic import BaseModel, Field


class VideoInfoDTO(BaseModel):
    """DTO for video information"""

    series: str = Field(..., description="Series or show name")
    season: str = Field(..., description="Season number")
    episode: str = Field(..., description="Episode number")
    title: str = Field(..., description="Episode title")
    path: str = Field(..., description="Relative file path")
    has_subtitles: bool = Field(default=False, description="Whether subtitles exist")
    duration: float | None = Field(None, description="Video duration in seconds")


class ProcessingStatusDTO(BaseModel):
    """DTO for video processing status"""

    status: str = Field(..., description="Processing status (pending, processing, completed, failed)")
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="Progress percentage (0-100)")
    current_step: str | None = Field(None, description="Current processing step description")
    message: str | None = Field(None, description="Status message or error description")
    video_path: str | None = Field(None, description="Path to processed video")
    subtitle_path: str | None = Field(None, description="Path to generated subtitles")
    translation_path: str | None = Field(None, description="Path to translation subtitles")
    vocabulary_count: int | None = Field(None, description="Number of vocabulary words extracted")

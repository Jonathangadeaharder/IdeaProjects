"""
SRT/Subtitle Data Transfer Objects
API request/response models for subtitle management
"""

from pydantic import BaseModel, Field


class SRTSegmentDTO(BaseModel):
    """DTO for SRT subtitle segment"""

    index: int = Field(..., ge=1, description="Segment index number")
    start_time: str = Field(..., description="Start timestamp (HH:MM:SS,mmm)")
    end_time: str = Field(..., description="End timestamp (HH:MM:SS,mmm)")
    text: str = Field(..., description="Subtitle text content")


class ParseSRTRequest(BaseModel):
    """DTO for SRT parsing request"""

    srt_content: str = Field(..., min_length=1, description="SRT file content to parse")


class ParseSRTResponse(BaseModel):
    """DTO for SRT parsing response"""

    segments: list[SRTSegmentDTO] = Field(..., description="Parsed subtitle segments")
    total_segments: int = Field(..., ge=0, description="Total number of segments")


class ConvertToSRTRequest(BaseModel):
    """DTO for converting segments to SRT format"""

    segments: list[SRTSegmentDTO] = Field(..., description="Segments to convert to SRT")

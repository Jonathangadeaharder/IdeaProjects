"""
API Data Transfer Objects

Centralized location for all API request/response models.
Follow naming convention: EntityNameDTO for responses, EntityNameRequest for requests.
"""

from .auth_dto import LoginDTO, PasswordChangeDTO, RegisterDTO, TokenDTO, UserDTO, UserUpdateDTO
from .game_dto import AnswerResultDTO, GameSessionDTO, StartGameRequest, SubmitAnswerRequest
from .progress_dto import DailyProgressDTO, UserProgressDTO
from .srt_dto import ConvertToSRTRequest, ParseSRTRequest, ParseSRTResponse, SRTSegmentDTO
from .user_profile_dto import (
    LanguagePreferencesDTO,
    UpdateProfileRequest,
    UserProfileDTO,
    UserSettingsDTO,
)
from .video_dto import ProcessingStatusDTO, VideoInfoDTO
from .vocabulary_dto import (
    VocabularyLibraryDTO,
    VocabularyWordDTO,
)

__all__ = [
    # Auth DTOs
    "LoginDTO",
    "RegisterDTO",
    "UserDTO",
    "TokenDTO",
    "PasswordChangeDTO",
    "UserUpdateDTO",
    # Video DTOs
    "VideoInfoDTO",
    "ProcessingStatusDTO",
    # Vocabulary DTOs
    "VocabularyWordDTO",
    "VocabularyLibraryDTO",
    # Progress DTOs
    "UserProgressDTO",
    "DailyProgressDTO",
    # User Profile DTOs
    "UserProfileDTO",
    "LanguagePreferencesDTO",
    "UserSettingsDTO",
    "UpdateProfileRequest",
    # SRT DTOs
    "SRTSegmentDTO",
    "ParseSRTRequest",
    "ParseSRTResponse",
    "ConvertToSRTRequest",
    # Game DTOs
    "GameSessionDTO",
    "StartGameRequest",
    "SubmitAnswerRequest",
    "AnswerResultDTO",
]

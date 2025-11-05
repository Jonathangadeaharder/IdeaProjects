"""
User Profile Data Transfer Objects
API request/response models for user profile management
"""

from pydantic import BaseModel, ConfigDict, Field


class LanguagePreferencesDTO(BaseModel):
    """DTO for user language preferences"""

    model_config = ConfigDict(from_attributes=True)

    native_language: str = Field(default="en", max_length=5, description="User's native language code")
    target_language: str = Field(default="de", max_length=5, description="Language being learned")
    interface_language: str | None = Field(None, max_length=5, description="UI language preference")


class UserProfileDTO(BaseModel):
    """DTO for complete user profile"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="User ID")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    is_active: bool = Field(default=True, description="Account active status")
    native_language: str = Field(default="en", description="Native language")
    target_language: str = Field(default="de", description="Target language")
    chunk_duration_minutes: int = Field(
        default=20, ge=5, le=20, description="Video chunk duration (5, 10, or 20 minutes)"
    )
    level: str | None = Field(None, description="Current CEFR level")
    created_at: str | None = Field(None, description="Account creation date (ISO format)")
    last_login: str | None = Field(None, description="Last login timestamp (ISO format)")


class UserSettingsDTO(BaseModel):
    """DTO for user settings"""

    model_config = ConfigDict(from_attributes=True)

    daily_goal: int | None = Field(None, ge=1, le=1000, description="Daily words goal")
    reminder_enabled: bool = Field(default=False, description="Enable daily reminders")
    reminder_time: str | None = Field(None, description="Reminder time (HH:MM format)")
    show_translations: bool = Field(default=True, description="Show translations by default")
    auto_play_audio: bool = Field(default=True, description="Auto-play word pronunciation")
    theme: str = Field(default="light", description="UI theme (light/dark)")


class UpdateProfileRequest(BaseModel):
    """DTO for profile update request"""

    email: str | None = Field(None, description="New email address")
    native_language: str | None = Field(None, max_length=5, description="Native language")
    target_language: str | None = Field(None, max_length=5, description="Target language")
    chunk_duration_minutes: int | None = Field(
        None, ge=5, le=20, description="Video chunk duration (5, 10, or 20 minutes)"
    )
    level: str | None = Field(None, description="CEFR level")

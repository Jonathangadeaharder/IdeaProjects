"""
Authentication Data Transfer Objects
Clean API representations for auth operations
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserDTO(BaseModel):
    """DTO for user representation"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False
    native_language: Optional[str] = None
    target_language: Optional[str] = None
    level: Optional[str] = None


class TokenDTO(BaseModel):
    """DTO for authentication token response"""
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    user: Optional[UserDTO] = None


class RegisterDTO(BaseModel):
    """DTO for user registration request"""
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)
    native_language: Optional[str] = None
    target_language: Optional[str] = None


class LoginDTO(BaseModel):
    """DTO for login request"""
    model_config = ConfigDict(from_attributes=True)

    username: str
    password: str


class PasswordChangeDTO(BaseModel):
    """DTO for password change request"""
    model_config = ConfigDict(from_attributes=True)

    current_password: str
    new_password: str = Field(min_length=8)


class UserUpdateDTO(BaseModel):
    """DTO for user profile update"""
    model_config = ConfigDict(from_attributes=True)

    email: Optional[EmailStr] = None
    native_language: Optional[str] = None
    target_language: Optional[str] = None
    level: Optional[str] = None

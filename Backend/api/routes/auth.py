"""
Authentication API routes
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException
from pydantic import BaseModel

from core.auth import current_active_user
from core.exceptions import AuthenticationError
from database.models import User
from services.authservice.token_service import TokenService

from ..models.auth import UserResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["authentication"])


# Note: Core authentication endpoints (register, login, logout) are handled by FastAPI-Users


class TokenRefreshResponse(BaseModel):
    """Response model for token refresh"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.get("/me", response_model=UserResponse, name="auth_get_current_user")
async def get_current_user_info(current_user: Annotated[User, Depends(current_active_user)]):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_superuser=current_user.is_superuser,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
        last_login=current_user.last_login.isoformat() if current_user.last_login else None,
    )


@router.post("/token/refresh", response_model=TokenRefreshResponse, name="auth_refresh_token")
async def refresh_access_token(refresh_token: str = Cookie(None, alias="refresh_token")):
    """
    Refresh access token using refresh token from cookie

    This endpoint exchanges a valid refresh token for a new access token.
    The refresh token should be stored in an HTTP-only cookie for security.

    Returns:
        TokenRefreshResponse: New access token with expiration info

    Raises:
        HTTPException: 401 if refresh token is invalid or expired
    """
    if not refresh_token:
        logger.warning("Token refresh attempted without refresh token")
        raise HTTPException(status_code=401, detail="Refresh token required")

    try:
        # Validate refresh token and generate new access token
        new_access_token = TokenService.refresh_access_token(refresh_token)

        logger.info("Access token refreshed successfully")

        return TokenRefreshResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=TokenService.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        )

    except AuthenticationError as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token. Please login again.",
        ) from e

"""
Custom logout endpoint with token blacklisting
"""
import logging
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

from core.config import settings
from core.auth import current_active_user
from core.token_blacklist import token_blacklist
from database.models import User

logger = logging.getLogger(__name__)
router = APIRouter(tags=["authentication"])

security = HTTPBearer()


@router.post("/logout", status_code=204, name="auth_logout")
async def logout(
    current_user: Annotated[User, Depends(current_active_user)],
    token: Annotated[str, Depends(security)]
):
    """
    Logout current user by blacklisting their JWT token
    """
    try:
        logger.info(f"Logout called for user {current_user.id}")
        
        # Extract the actual token from the HTTPAuthorizationCredentials
        if hasattr(token, 'credentials'):
            token_str = token.credentials
        else:
            token_str = token
        
        logger.info(f"Token to blacklist: {token_str[:20]}...")
        
        # Decode token to get expiration time
        try:
            payload = jwt.decode(token_str, settings.secret_key, algorithms=["HS256"])
            exp_timestamp = payload.get("exp")
            expires_at = datetime.utcfromtimestamp(exp_timestamp) if exp_timestamp else None
            logger.info(f"Token expires at: {expires_at}")
        except JWTError as e:
            # If we can't decode the token, still blacklist it with default expiration
            expires_at = datetime.utcnow() + timedelta(hours=24)
            logger.warning(f"Failed to decode token: {e}, using default expiration")
        
        # Add token to blacklist
        result = await token_blacklist.add_token(token_str, expires_at)
        logger.info(f"Token blacklist result: {result}")
        
        logger.info(f"User {current_user.id} logged out successfully")
        
        # Return 204 No Content (successful logout)
        return None
        
    except Exception as e:
        logger.error(f"Logout error for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
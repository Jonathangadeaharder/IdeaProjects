"""
Authentication Audit Logger

Comprehensive audit logging for all authentication-related events.
Tracks security events for compliance, monitoring, and incident investigation.

Usage Example:
    ```python
    from fastapi import Request
    audit = AuditLogger(db)

    # Log successful login
    await audit.log_login_success(
        user_id=1,
        username="alice",
        request=request
    )

    # Log failed login
    await audit.log_login_failure(
        username="alice",
        reason="invalid_password",
        request=request
    )

    # Log token theft detection
    await audit.log_token_theft(
        user_id=1,
        username="alice",
        family_id="abc-123",
        request=request
    )
    ```

Security Features:
    - Records all authentication events
    - Captures IP address and user agent
    - Tracks success/failure with detailed reasons
    - Supports deleted user tracking (denormalized username)
    - Indexed for fast querying

Thread Safety:
    Yes. All operations use async database transactions.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging_config import get_logger
from core.transaction import transactional
from database.models import AuthAuditLog

UTC = timezone.utc
logger = get_logger(__name__)


class AuditLogger:
    """
    Service for logging authentication audit events

    Records all authentication-related activities for security monitoring,
    compliance, and incident investigation.

    Attributes:
        db (AsyncSession): Database session for persistence
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _extract_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
        """
        Extract IP address and user agent from request

        Args:
            request: FastAPI request object

        Returns:
            Tuple of (ip_address, user_agent)
        """
        ip_address = None
        if request.client:
            ip_address = request.client.host

        user_agent = request.headers.get("user-agent")

        return ip_address, user_agent

    @transactional
    async def log_event(
        self,
        event_type: str,
        success: bool,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        event_detail: Optional[str] = None,
        failure_reason: Optional[str] = None,
        request: Optional[Request] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """
        Log generic authentication event

        Args:
            event_type: Type of event (e.g., "login_success", "token_refresh")
            success: Was the operation successful?
            user_id: User ID (if known)
            username: Username (for correlation with deleted users)
            event_detail: Additional details (JSON or text)
            failure_reason: Why did it fail? (if applicable)
            request: FastAPI request (for extracting IP/user agent)
            ip_address: Override IP address (if request not available)
            user_agent: Override user agent (if request not available)
        """
        # Extract client info from request if provided
        if request:
            extracted_ip, extracted_ua = self._extract_client_info(request)
            ip_address = ip_address or extracted_ip
            user_agent = user_agent or extracted_ua

        # Create audit log entry
        audit_entry = AuthAuditLog(
            user_id=user_id,
            username=username,
            event_type=event_type,
            event_detail=event_detail,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
            timestamp=datetime.now(UTC),
        )

        self.db.add(audit_entry)
        await self.db.flush()

        # Log to application logs as well
        log_level = logger.info if success else logger.warning
        log_level(
            f"AUTH AUDIT: {event_type} - "
            f"user={username or user_id or 'unknown'} "
            f"success={success} "
            f"ip={ip_address or 'unknown'} "
            f"{f'reason={failure_reason}' if failure_reason else ''}"
        )

    async def log_login_success(
        self,
        user_id: int,
        username: str,
        request: Request,
        event_detail: Optional[str] = None,
    ):
        """
        Log successful login event

        Args:
            user_id: ID of authenticated user
            username: Username of authenticated user
            request: FastAPI request
            event_detail: Optional additional details
        """
        await self.log_event(
            event_type="login_success",
            success=True,
            user_id=user_id,
            username=username,
            event_detail=event_detail,
            request=request,
        )

    async def log_login_failure(
        self,
        username: str,
        reason: str,
        request: Request,
        event_detail: Optional[str] = None,
    ):
        """
        Log failed login attempt

        Args:
            username: Attempted username
            reason: Why login failed (e.g., "invalid_password", "user_not_found")
            request: FastAPI request
            event_detail: Optional additional details
        """
        await self.log_event(
            event_type="login_failure",
            success=False,
            username=username,
            failure_reason=reason,
            event_detail=event_detail,
            request=request,
        )

    async def log_token_refresh_success(
        self,
        user_id: int,
        username: str,
        request: Request,
        generation: Optional[int] = None,
    ):
        """
        Log successful token refresh

        Args:
            user_id: User ID
            username: Username
            request: FastAPI request
            generation: Token generation number (if applicable)
        """
        detail = f"generation={generation}" if generation is not None else None
        await self.log_event(
            event_type="token_refresh_success",
            success=True,
            user_id=user_id,
            username=username,
            event_detail=detail,
            request=request,
        )

    async def log_token_refresh_failure(
        self,
        reason: str,
        request: Request,
        username: Optional[str] = None,
        user_id: Optional[int] = None,
    ):
        """
        Log failed token refresh

        Args:
            reason: Why refresh failed (e.g., "expired_token", "invalid_token")
            request: FastAPI request
            username: Username (if known)
            user_id: User ID (if known)
        """
        await self.log_event(
            event_type="token_refresh_failure",
            success=False,
            user_id=user_id,
            username=username,
            failure_reason=reason,
            request=request,
        )

    async def log_token_theft(
        self,
        user_id: int,
        username: str,
        family_id: str,
        request: Request,
        generation: Optional[int] = None,
    ):
        """
        Log token theft detection (critical security event)

        Args:
            user_id: User ID whose tokens were compromised
            username: Username
            family_id: Token family ID that was revoked
            request: FastAPI request
            generation: Token generation that was reused
        """
        detail = f"family_id={family_id}"
        if generation is not None:
            detail += f", reused_generation={generation}"

        await self.log_event(
            event_type="token_theft_detected",
            success=False,  # Security incident = failure
            user_id=user_id,
            username=username,
            event_detail=detail,
            failure_reason="token_reuse_detected",
            request=request,
        )

        # Also log critical security event
        logger.critical(
            f"SECURITY ALERT: Token theft detected for user {username} (ID: {user_id}). "
            f"Family {family_id} revoked. IP: {request.client.host if request.client else 'unknown'}"
        )

    async def log_logout(
        self,
        user_id: int,
        username: str,
        request: Request,
        family_id: Optional[str] = None,
    ):
        """
        Log user logout

        Args:
            user_id: User ID
            username: Username
            request: FastAPI request
            family_id: Token family ID that was revoked (if applicable)
        """
        detail = f"family_id={family_id}" if family_id else None
        await self.log_event(
            event_type="logout",
            success=True,
            user_id=user_id,
            username=username,
            event_detail=detail,
            request=request,
        )

    async def log_password_change(
        self,
        user_id: int,
        username: str,
        request: Request,
        revoked_token_count: Optional[int] = None,
    ):
        """
        Log password change event

        Args:
            user_id: User ID
            username: Username
            request: FastAPI request
            revoked_token_count: Number of tokens revoked due to password change
        """
        detail = f"revoked_tokens={revoked_token_count}" if revoked_token_count else None
        await self.log_event(
            event_type="password_change",
            success=True,
            user_id=user_id,
            username=username,
            event_detail=detail,
            request=request,
        )

    async def log_account_lockout(
        self,
        username: str,
        reason: str,
        request: Request,
        user_id: Optional[int] = None,
    ):
        """
        Log account lockout (e.g., too many failed attempts)

        Args:
            username: Username
            reason: Why account was locked
            request: FastAPI request
            user_id: User ID (if known)
        """
        await self.log_event(
            event_type="account_lockout",
            success=False,
            user_id=user_id,
            username=username,
            failure_reason=reason,
            request=request,
        )

        logger.warning(
            f"SECURITY: Account lockout for {username}. Reason: {reason}. "
            f"IP: {request.client.host if request.client else 'unknown'}"
        )

    async def log_registration(
        self,
        user_id: int,
        username: str,
        email: str,
        request: Request,
    ):
        """
        Log new user registration

        Args:
            user_id: New user ID
            username: New username
            email: New user email
            request: FastAPI request
        """
        await self.log_event(
            event_type="registration",
            success=True,
            user_id=user_id,
            username=username,
            event_detail=f"email={email}",
            request=request,
        )

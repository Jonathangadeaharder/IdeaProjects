"""
Password validation and hashing service
Enforces strong password policy for LangPlug
"""

import re

from passlib.context import CryptContext

# Initialize password context with Argon2 (more secure than bcrypt)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class PasswordValidator:
    """
    Enforce strong password policy

    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - Not in common passwords list
    """

    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True

    # Common passwords to block (top 100 most common)
    # Includes variations that meet complexity requirements (12+ chars, upper/lower/digit/special)
    COMMON_PASSWORDS = {
        "password123",
        "password123!",
        "password1234!",  # Meets complexity (12 chars, has special)
        "admin123",
        "admin123!",
        "admin1234567",
        "admin1234567!",  # Meets complexity (13 chars, has special)
        "welcome123",
        "welcome123!",
        "welcome1234!",
        "qwerty123",
        "qwerty123!",
        "letmein123",
        "123456789012",
        "password1234",
        "changeme123!",
        "default123!",
        "langplug123",
        "langplug123!",
    }

    @classmethod
    def validate(cls, password: str) -> tuple[bool, str]:
        """
        Validate password against policy.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
            error_message is empty string if valid
        """
        # Check minimum length
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters"

        # Check uppercase requirement
        if cls.REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"

        # Check lowercase requirement
        if cls.REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"

        # Check digit requirement
        if cls.REQUIRE_DIGITS and not re.search(r"\d", password):
            return False, "Password must contain at least one digit"

        # Check special character requirement
        if cls.REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character (!@#$%^&*...)"

        # Check against common passwords
        if cls._is_common_password(password):
            return False, "Password is too common, please choose a stronger password"

        return True, ""

    @staticmethod
    def _is_common_password(password: str) -> bool:
        """Check if password is in common passwords list"""
        return password.lower() in PasswordValidator.COMMON_PASSWORDS

    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hash password using Argon2

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        return pwd_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to compare

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def needs_rehash(cls, hashed_password: str) -> bool:
        """
        Check if password hash needs to be updated

        Args:
            hashed_password: Existing password hash

        Returns:
            True if hash should be regenerated with current settings
        """
        return pwd_context.needs_update(hashed_password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Convenience function for password validation

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    return PasswordValidator.validate(password)


def hash_password(password: str) -> str:
    """
    Convenience function for password hashing

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return PasswordValidator.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Convenience function for password verification

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if match, False otherwise
    """
    return PasswordValidator.verify_password(plain_password, hashed_password)

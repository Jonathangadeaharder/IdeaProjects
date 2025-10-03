"""
Unit tests for PasswordValidator

Tests password strength requirements, common password blocking, and hashing
"""

from services.authservice.password_validator import PasswordValidator


class TestPasswordValidation:
    """Test password strength validation rules"""

    def test_validate_minimum_length_too_short(self):
        """Passwords shorter than 12 characters should be rejected"""
        is_valid, error = PasswordValidator.validate("Short1!")
        assert is_valid is False
        assert "12 characters" in error

    def test_validate_minimum_length_exactly_12(self):
        """Password with exactly 12 characters should pass length check"""
        # This will fail other checks, but should pass length
        password = "a" * 12
        is_valid, error = PasswordValidator.validate(password)
        # Will fail for other reasons, but not length
        assert "12 characters" not in error

    def test_validate_requires_uppercase(self):
        """Password without uppercase should be rejected"""
        is_valid, error = PasswordValidator.validate("lowercase123!")
        assert is_valid is False
        assert "uppercase" in error.lower()

    def test_validate_requires_lowercase(self):
        """Password without lowercase should be rejected"""
        is_valid, error = PasswordValidator.validate("UPPERCASE123!")
        assert is_valid is False
        assert "lowercase" in error.lower()

    def test_validate_requires_digit(self):
        """Password without digit should be rejected"""
        is_valid, error = PasswordValidator.validate("NoDigitsHere!")
        assert is_valid is False
        assert "digit" in error.lower()

    def test_validate_requires_special_character(self):
        """Password without special character should be rejected"""
        is_valid, error = PasswordValidator.validate("NoSpecial123")
        assert is_valid is False
        assert "special character" in error.lower()

    def test_validate_strong_password_success(self):
        """Strong password meeting all requirements should pass"""
        is_valid, error = PasswordValidator.validate("SecurePass123!")
        assert is_valid is True
        assert error == ""

    def test_validate_various_special_characters(self):
        """Password with different special characters should pass"""
        special_chars = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "?"]
        for char in special_chars:
            password = f"SecurePass123{char}"
            is_valid, error = PasswordValidator.validate(password)
            assert is_valid is True, f"Failed with special char: {char}, error: {error}"


class TestCommonPasswordBlocking:
    """Test common password detection and blocking"""

    def test_validate_blocks_common_password_lowercase(self):
        """Common passwords should be blocked (case-insensitive)"""
        # "password1234" is in COMMON_PASSWORDS, meets length (12), needs complexity
        is_valid, error = PasswordValidator.validate("Password1234!")
        assert is_valid is False
        assert "common" in error.lower()

    def test_validate_blocks_common_password_uppercase(self):
        """Common passwords should be blocked regardless of case"""
        # Case variation of password1234 with complexity (has lowercase 'p')
        is_valid, error = PasswordValidator.validate("pASSWORD1234!")
        assert is_valid is False
        assert "common" in error.lower()

    def test_validate_blocks_common_password_mixed_case(self):
        """Common passwords with mixed case should be blocked"""
        # Mixed case variation
        is_valid, error = PasswordValidator.validate("PaSsWoRd1234!")
        assert is_valid is False
        assert "common" in error.lower()

    def test_validate_blocks_admin_password(self):
        """Admin variations should be blocked"""
        # "admin1234567" is in COMMON_PASSWORDS (12 chars)
        is_valid, error = PasswordValidator.validate("Admin1234567!")
        assert is_valid is False
        assert "common" in error.lower()

    def test_validate_blocks_welcome_password(self):
        """Welcome variations should be blocked"""
        # "welcome1234!" is in COMMON_PASSWORDS (12 chars)
        is_valid, error = PasswordValidator.validate("Welcome1234!")
        assert is_valid is False
        assert "common" in error.lower()

    def test_validate_blocks_langplug_password(self):
        """Application-specific common passwords should be blocked"""
        # "langplug123!" is in COMMON_PASSWORDS (12 chars)
        is_valid, error = PasswordValidator.validate("Langplug123!")
        assert is_valid is False
        assert "common" in error.lower()

    def test_validate_allows_similar_to_common(self):
        """Passwords similar but not identical to common ones should pass"""
        # password123 is common, but SecurePassword123! is not
        is_valid, error = PasswordValidator.validate("SecurePassword123!")
        assert is_valid is True


class TestPasswordHashing:
    """Test password hashing and verification with Argon2"""

    def test_hash_password_returns_non_empty_string(self):
        """Hashing should return a non-empty hash string"""
        hashed = PasswordValidator.hash_password("SecurePass123!")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_different_each_time(self):
        """Hashing same password twice should produce different hashes (salt)"""
        password = "SecurePass123!"
        hash1 = PasswordValidator.hash_password(password)
        hash2 = PasswordValidator.hash_password(password)

        assert hash1 != hash2  # Different due to random salt

    def test_hash_password_contains_argon2_identifier(self):
        """Hash should contain Argon2 identifier"""
        hashed = PasswordValidator.hash_password("SecurePass123!")
        # Argon2 hashes start with $argon2
        assert hashed.startswith("$argon2")

    def test_verify_password_correct_password(self):
        """Verify should return True for correct password"""
        password = "SecurePass123!"
        hashed = PasswordValidator.hash_password(password)

        assert PasswordValidator.verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """Verify should return False for incorrect password"""
        password = "SecurePass123!"
        wrong_password = "WrongPass123!"
        hashed = PasswordValidator.hash_password(password)

        assert PasswordValidator.verify_password(wrong_password, hashed) is False

    def test_verify_password_case_sensitive(self):
        """Password verification should be case-sensitive"""
        password = "SecurePass123!"
        hashed = PasswordValidator.hash_password(password)

        # Wrong case should fail
        assert PasswordValidator.verify_password("securepass123!", hashed) is False
        assert PasswordValidator.verify_password("SECUREPASS123!", hashed) is False

    def test_verify_password_empty_string(self):
        """Verify should handle empty password gracefully"""
        hashed = PasswordValidator.hash_password("SecurePass123!")

        assert PasswordValidator.verify_password("", hashed) is False


class TestPasswordRehashing:
    """Test password rehashing detection"""

    def test_needs_rehash_with_current_hash(self):
        """Current Argon2 hash should not need rehashing"""
        password = "SecurePass123!"
        hashed = PasswordValidator.hash_password(password)

        # Newly created hash should not need rehashing
        assert PasswordValidator.needs_rehash(hashed) is False


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_validate_exactly_minimum_length_with_all_requirements(self):
        """12-character password with all requirements should pass"""
        is_valid, error = PasswordValidator.validate("SecurePass1!")  # Exactly 12 chars
        assert is_valid is True

    def test_validate_very_long_password(self):
        """Very long password should be accepted"""
        long_password = "SecurePassword123!" * 10  # 180 characters
        is_valid, error = PasswordValidator.validate(long_password)
        assert is_valid is True

    def test_validate_only_special_characters_with_requirements(self):
        """Password with multiple special characters should pass"""
        is_valid, error = PasswordValidator.validate("S3cure!@#$%^Pass")
        assert is_valid is True

    def test_validate_unicode_characters(self):
        """Password with Unicode characters should be validated"""
        # Contains uppercase, lowercase, digit, special, and Unicode
        password = "SecurePass123!мир"
        is_valid, error = PasswordValidator.validate(password)
        # Should pass validation (Unicode chars don't break rules)
        assert is_valid is True

    def test_hash_empty_password(self):
        """Hashing empty password should work (validation happens separately)"""
        hashed = PasswordValidator.hash_password("")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_verify_special_characters_in_password(self):
        """Passwords with special chars should hash and verify correctly"""
        password = r"P@ssw0rd!#$%^&*()"
        hashed = PasswordValidator.hash_password(password)

        assert PasswordValidator.verify_password(password, hashed) is True


class TestValidationReturnFormat:
    """Test validation return format consistency"""

    def test_validate_success_returns_tuple(self):
        """Successful validation should return (True, '')"""
        is_valid, error = PasswordValidator.validate("SecurePass123!")
        assert isinstance(is_valid, bool)
        assert isinstance(error, str)
        assert is_valid is True
        assert error == ""

    def test_validate_failure_returns_tuple(self):
        """Failed validation should return (False, error_message)"""
        is_valid, error = PasswordValidator.validate("short")
        assert isinstance(is_valid, bool)
        assert isinstance(error, str)
        assert is_valid is False
        assert len(error) > 0

    def test_validate_error_messages_are_descriptive(self):
        """Error messages should clearly describe the issue"""
        test_cases = [
            ("short", "12 characters"),
            ("nouppercase123!", "uppercase"),
            ("NOLOWERCASE123!", "lowercase"),
            ("NoDigitsHere!", "digit"),
            ("NoSpecial123", "special"),
            ("Password1234!", "common"),  # Meets complexity but is common
        ]

        for password, expected_keyword in test_cases:
            is_valid, error = PasswordValidator.validate(password)
            assert is_valid is False
            assert expected_keyword.lower() in error.lower(), f"Expected '{expected_keyword}' in error for '{password}'"

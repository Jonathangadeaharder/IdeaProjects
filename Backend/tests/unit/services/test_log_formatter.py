"""
Test suite for LogFormatter
Tests log formatting and output functionality
"""

import pytest
import json
import logging
from unittest.mock import Mock

from services.logging.log_formatter import (
    LogFormatterService,
    StructuredLogFormatter,
    log_formatter_service
)

# Import enums and models from the correct location
try:
    from services.logging.log_formatter import LogLevel, LogFormat, LogContext, LogRecord
except ImportError:
    # Define minimal versions for testing if not available
    from enum import Enum
    class LogLevel(str, Enum):
        DEBUG = "DEBUG"
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"
    class LogFormat(str, Enum):
        PLAIN = "plain"
        STRUCTURED = "structured"
    LogContext = dict
    LogRecord = dict


class TestLogLevel:
    """Test LogLevel enumeration"""

    def test_log_level_values(self):
        """Test log level enum values"""
        assert LogLevel.DEBUG.value == logging.DEBUG
        assert LogLevel.INFO.value == logging.INFO
        assert LogLevel.WARNING.value == logging.WARNING
        assert LogLevel.ERROR.value == logging.ERROR
        assert LogLevel.CRITICAL.value == logging.CRITICAL


class TestLogFormat:
    """Test LogFormat enumeration"""

    def test_log_format_values(self):
        """Test log format enum values"""
        assert LogFormat.SIMPLE.value == "simple"
        assert LogFormat.DETAILED.value == "detailed"
        assert LogFormat.JSON.value == "json"
        assert LogFormat.STRUCTURED.value == "structured"


class TestLogContext:
    """Test LogContext data class"""

    def test_log_context_initialization(self):
        """Test log context initialization"""
        context = LogContext()
        assert context.user_id == ""
        assert context.request_id == ""
        assert context.session_id == ""
        assert context.operation == ""

    def test_log_context_with_values(self):
        """Test log context with values"""
        context = LogContext(
            user_id="user123",
            request_id="req456",
            session_id="session789",
            operation="test_operation"
        )
        assert context.user_id == "user123"
        assert context.request_id == "req456"
        assert context.session_id == "session789"
        assert context.operation == "test_operation"


class TestLogRecord:
    """Test LogRecord data class"""

    def test_log_record_initialization(self):
        """Test log record initialization"""
        record = LogRecord()
        assert record.timestamp == ""
        assert record.level == ""
        assert record.logger_name == ""
        assert record.message == ""
        assert isinstance(record.context, LogContext)
        assert isinstance(record.extra, dict)

    def test_log_record_with_values(self):
        """Test log record with values"""
        context = LogContext(user_id="user123")
        extra = {"custom_field": "value"}

        record = LogRecord(
            timestamp="2023-01-01T00:00:00",
            level="INFO",
            logger_name="test_logger",
            message="Test message",
            context=context,
            extra=extra
        )

        assert record.timestamp == "2023-01-01T00:00:00"
        assert record.level == "INFO"
        assert record.logger_name == "test_logger"
        assert record.message == "Test message"
        assert record.context.user_id == "user123"
        assert record.extra["custom_field"] == "value"


class TestStructuredLogFormatter:
    """Test StructuredLogFormatter"""

    def test_initialization(self):
        """Test formatter initialization"""
        formatter = StructuredLogFormatter()
        assert formatter.include_extra_fields is True

    def test_initialization_no_extra_fields(self):
        """Test formatter initialization without extra fields"""
        formatter = StructuredLogFormatter(include_extra_fields=False)
        assert formatter.include_extra_fields is False

    def test_format_basic_record(self):
        """Test formatting basic log record"""
        formatter = StructuredLogFormatter()

        # Create mock log record
        record = Mock()
        record.created = 1672531200.0  # 2023-01-01 00:00:00
        record.levelname = "INFO"
        record.name = "test_logger"
        record.getMessage.return_value = "Test message"
        record.module = "test_module"
        record.funcName = "test_function"
        record.lineno = 42

        # Add context attributes directly to record
        record.user_id = 'user123'
        record.request_id = 'req456'
        record.session_id = ''
        record.operation = ''

        result = formatter.format(record)

        # Parse JSON result
        log_data = json.loads(result)

        # Assert basic fields
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test_logger"
        assert log_data["message"] == "Test message"
        assert log_data["module"] == "test_module"
        assert log_data["function"] == "test_function"
        assert log_data["line"] == 42

        # Assert context
        assert "context" in log_data
        assert log_data["context"]["user_id"] == "user123"
        assert log_data["context"]["request_id"] == "req456"

    def test_format_record_no_context(self):
        """Test formatting record with no context"""
        formatter = StructuredLogFormatter()

        # Create mock log record with no context
        record = Mock()
        record.created = 1672531200.0
        record.levelname = "INFO"
        record.name = "test_logger"
        record.getMessage.return_value = "Test message"
        record.module = "test_module"
        record.funcName = "test_function"
        record.lineno = 42

        # Set context attributes to empty to avoid context section
        record.user_id = ""
        record.request_id = ""
        record.session_id = ""
        record.operation = ""

        result = formatter.format(record)
        log_data = json.loads(result)

        # Should not have context section
        assert "context" not in log_data


class TestLogFormatter:
    """Test LogFormatter service"""

    def test_initialization(self):
        """Test service initialization"""
        service = LogFormatter()
        assert service is not None
        assert len(service.formatters) == 4  # All LogFormat types

    def test_get_formatter_simple(self):
        """Test getting simple formatter"""
        service = LogFormatter()
        formatter = service.get_formatter(LogFormat.SIMPLE)

        assert isinstance(formatter, logging.Formatter)
        assert formatter._fmt == '%(levelname)s - %(message)s'

    def test_get_formatter_detailed(self):
        """Test getting detailed formatter"""
        service = LogFormatter()
        formatter = service.get_formatter(LogFormat.DETAILED)

        assert isinstance(formatter, logging.Formatter)
        assert '%(asctime)s' in formatter._fmt
        assert '%(name)s' in formatter._fmt

    def test_get_formatter_json(self):
        """Test getting JSON formatter"""
        service = LogFormatter()
        formatter = service.get_formatter(LogFormat.JSON)

        assert isinstance(formatter, StructuredLogFormatter)
        assert formatter.include_extra_fields is True

    def test_get_formatter_structured(self):
        """Test getting structured formatter"""
        service = LogFormatter()
        formatter = service.get_formatter(LogFormat.STRUCTURED)

        assert isinstance(formatter, StructuredLogFormatter)
        assert formatter.include_extra_fields is False

    def test_get_formatter_invalid(self):
        """Test getting formatter with invalid format"""
        service = LogFormatter()

        # Create mock invalid format
        invalid_format = Mock()
        invalid_format.name = "INVALID"

        formatter = service.get_formatter(invalid_format)

        # Should return detailed formatter as default
        assert isinstance(formatter, logging.Formatter)
        assert '%(asctime)s' in formatter._fmt

    def test_format_message(self):
        """Test message formatting"""
        service = LogFormatter()

        context = LogContext(user_id="user123", operation="test")
        extra = {"custom": "data"}

        result = service.format_message(
            "Test message",
            LogLevel.INFO,
            "test_logger",
            context,
            extra
        )

        assert isinstance(result, LogRecord)
        assert result.level == "INFO"
        assert result.logger_name == "test_logger"
        assert result.message == "Test message"
        assert result.context.user_id == "user123"
        assert result.extra["custom"] == "data"

    def test_format_message_defaults(self):
        """Test message formatting with defaults"""
        service = LogFormatter()

        result = service.format_message("Test message", LogLevel.ERROR)

        assert isinstance(result, LogRecord)
        assert result.level == "ERROR"
        assert result.logger_name == ""
        assert result.message == "Test message"
        assert isinstance(result.context, LogContext)
        assert result.extra == {}

    def test_mask_sensitive_data(self):
        """Test sensitive data masking"""
        service = LogFormatter()

        data = {
            "username": "john_doe",
            "password": "secret123",
            "api_key": "abc123xyz",
            "email": "john@example.com"
        }

        sensitive_fields = ["password", "api_key"]

        result = service.mask_sensitive_data(data, sensitive_fields)

        assert result["username"] == "john_doe"
        assert result["password"] == "***MASKED***"
        assert result["api_key"] == "***MASKED***"
        assert result["email"] == "john@example.com"

    def test_mask_sensitive_data_empty_fields(self):
        """Test sensitive data masking with empty fields list"""
        service = LogFormatter()

        data = {"password": "secret123"}

        result = service.mask_sensitive_data(data, [])

        assert result["password"] == "secret123"

    async def test_health_check(self):
        """Test service health check"""
        service = LogFormatter()
        result = await service.health_check()

        assert result["service"] == "LogFormatter"
        assert result["status"] == "healthy"
        assert "formatters" in result

    async def test_initialize(self):
        """Test service initialization"""
        service = LogFormatter()
        await service.initialize()
        # Should complete without error

    async def test_cleanup(self):
        """Test service cleanup"""
        service = LogFormatter()
        await service.cleanup()
        # Should complete without error
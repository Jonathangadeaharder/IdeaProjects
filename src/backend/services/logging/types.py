"""
Logging type definitions and enumerations
Shared types for the logging service components
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LogLevel(Enum):
    """Log level enumeration"""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogFormat(Enum):
    """Log format enumeration"""

    SIMPLE = "simple"
    DETAILED = "detailed"
    JSON = "json"
    STRUCTURED = "structured"


@dataclass
class LogConfig:
    """Configuration for logging service"""

    # Basic settings
    level: LogLevel = LogLevel.INFO
    format_type: LogFormat = LogFormat.DETAILED

    # Output destinations
    console_enabled: bool = True
    file_enabled: bool = True

    # File settings
    log_file_path: str = "logs/a1decider.log"
    max_file_size_mb: int = 10
    backup_count: int = 5

    # Advanced settings
    include_timestamps: bool = True
    include_caller_info: bool = False
    include_thread_info: bool = False
    include_process_info: bool = False

    # Service-specific settings
    log_database_queries: bool = False
    log_authentication_events: bool = True
    log_filter_operations: bool = False
    log_user_actions: bool = True
    mask_sensitive_fields: list = field(default_factory=list)


@dataclass
class LogContext:
    """Context information for structured logging"""

    user_id: str | None = None
    session_id: str | None = None
    request_id: str | None = None
    correlation_id: str | None = None


@dataclass
class LogRecord:
    """Custom log record for structured logging"""

    timestamp: Any
    level: str
    message: str
    module: str | None = None
    function: str | None = None
    line: int | None = None
    context: LogContext | None = None
    extra_data: dict | None = None

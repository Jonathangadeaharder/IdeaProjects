"""
Tests for JSONFormatter and setup_logging in core.logging.
"""
from __future__ import annotations

import json
import logging
from core.logging_config import JSONFormatter, setup_logging


def test_json_formatter_serializes_record():
    formatter = JSONFormatter()
    logger = logging.getLogger("test.logger")
    record = logger.makeRecord(name="test.logger", level=logging.INFO, fn=__file__, lno=10, msg="hello", args=(), exc_info=None)
    # Add a custom attribute to exercise extra-field serialization
    record.user = "alice"
    out = formatter.format(record)
    data = json.loads(out)
    assert data["level"] == "INFO"
    assert data["message"] == "hello"
    assert "timestamp" in data
    assert data["user"] == "alice"


def test_setup_logging_returns_log_file_path():
    log_file = setup_logging()
    from pathlib import Path
    assert isinstance(log_file, Path)
    # Test that logging works after setup
    logger = logging.getLogger(__name__)
    logger.info("ping")

"""
Tests for Settings CORS origin parsing behavior.
"""
from __future__ import annotations

import os
import pytest

from core.config import Settings


def test_cors_origins_parsing_csv():
    out = Settings.parse_cors_origins("http://a.com,http://b.com")
    assert out == ["http://a.com", "http://b.com"]


def test_cors_origins_parsing_json():
    out = Settings.parse_cors_origins('["http://x", "http://y"]')
    assert out == ["http://x", "http://y"]

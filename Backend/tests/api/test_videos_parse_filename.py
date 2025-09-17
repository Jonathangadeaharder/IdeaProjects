"""
Unit tests for parse_episode_filename helper in videos route.
"""
from __future__ import annotations

import pytest


def test_parse_episode_filename_basic():
    from api.routes.videos import parse_episode_filename
    info = parse_episode_filename("Episode 1 Staffel 2 My Show")
    assert info.get("episode") == "1"
    assert info.get("season") == "2"
    assert info.get("title").startswith("Episode 1")


def test_parse_episode_filename_missing_tokens():
    from api.routes.videos import parse_episode_filename
    info = parse_episode_filename("Pilot")
    assert info.get("episode") is None or info.get("episode") == "Pilot"
    assert info.get("title") == "Pilot"


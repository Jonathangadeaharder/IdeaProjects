"""
Tests for Settings path helpers (videos, data, database path).
"""
from __future__ import annotations

from pathlib import Path

from core.config import Settings


def test_get_videos_path_override(tmp_path: Path):
    s = Settings(videos_path=str(tmp_path))
    assert s.get_videos_path() == tmp_path


def test_get_database_path_sqlite_url(tmp_path: Path):
    db = tmp_path / "test.db"
    s = Settings(database_url=f"sqlite:///{db}")
    assert s.get_database_path() == db


def test_get_data_path_override_creates(tmp_path: Path):
    target = tmp_path / "d"
    s = Settings(data_path=str(target))
    p = s.get_data_path()
    assert p == target
    assert p.exists() and p.is_dir()


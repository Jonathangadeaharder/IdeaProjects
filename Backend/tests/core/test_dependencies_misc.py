"""
Misc small tests for core.dependencies utilities.
"""
from __future__ import annotations

from core.dependencies import get_task_progress_registry


def test_get_task_progress_registry_singleton():
    a = get_task_progress_registry()
    b = get_task_progress_registry()
    assert a is b
    key = "k"
    a[key] = 1
    assert b[key] == 1


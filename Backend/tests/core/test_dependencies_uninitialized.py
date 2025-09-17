"""
Coverage for get_database_manager/get_auth_service uninitialized error paths.
"""
from __future__ import annotations

import importlib
import pytest


def test_uninitialized_services_raise_runtime_error():
    deps = importlib.import_module('core.dependencies')
    # Backup and clear registry
    backup = deps._service_registry.copy()
    try:
        deps._service_registry.clear()
        with pytest.raises(RuntimeError):
            deps.get_database_manager()
        with pytest.raises(RuntimeError):
            deps.get_auth_service()
    finally:
        deps._service_registry.clear()
        deps._service_registry.update(backup)


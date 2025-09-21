"""Integration tests for vocabulary endpoints with minimal mocking."""
from __future__ import annotations

import pytest

from tests.auth_helpers import AuthTestHelperAsync


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_Whenvocabulary_statsCalled_ThenReturnslevels(async_client):
    from services.vocabulary_preload_service import get_vocabulary_preload_service
    
    flow = await AuthTestHelperAsync.register_and_login_async(async_client)

    class FakeService:
        async def get_vocabulary_stats(self, db=None):
            return {"A1": {"total_words": 2}}
            
        async def get_user_known_words(self, user_id, level, db=None):
            return set()
    
    # Override the dependency instead of patching
    fake_service = FakeService()
    async_client._transport.app.dependency_overrides[get_vocabulary_preload_service] = lambda: fake_service
    
    try:
        response = await async_client.get(
            "/api/vocabulary/library/stats", headers=flow["headers"]
        )

        assert response.status_code == 200
        assert response.json()["levels"]["A1"]["total_words"] == 2
    finally:
        # Clean up dependency override
        del async_client._transport.app.dependency_overrides[get_vocabulary_preload_service]


@pytest.mark.anyio
@pytest.mark.timeout(30)
async def test_Whenbulk_mark_level_uses_serviceCalled_ThenSucceeds(async_client):
    from services.vocabulary_preload_service import get_vocabulary_preload_service
    
    flow = await AuthTestHelperAsync.register_and_login_async(async_client)

    class FakeService:
        def __init__(self):
            self.bulk_mark_called = False
            self.call_args = None
            
        async def bulk_mark_level_known(self, user_id, level, known, db=None):
            self.bulk_mark_called = True
            self.call_args = (user_id, level, known)
            return 3
    
    # Override the dependency instead of patching
    fake_service = FakeService()
    async_client._transport.app.dependency_overrides[get_vocabulary_preload_service] = lambda: fake_service
    
    try:
        response = await async_client.post(
            "/api/vocabulary/library/bulk-mark",
            json={"level": "A1", "known": True},
            headers=flow["headers"],
        )

        assert response.status_code == 200
        assert fake_service.bulk_mark_called
        assert fake_service.call_args[1] == "A1"  # level
        assert fake_service.call_args[2] is True  # known
    finally:
        # Clean up dependency override
        del async_client._transport.app.dependency_overrides[get_vocabulary_preload_service]

"""High-level workflow smoke tests."""

from __future__ import annotations

import pytest

from tests.helpers import AsyncAuthHelper


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_Whenfull_user_workflowCalled_ThenSucceeds(async_client):
    helper = AsyncAuthHelper(async_client)

    user, token, _headers = await helper.create_authenticated_user()

    profile = await helper.verify_token(token)
    assert profile["username"] == user.username

    result = await helper.logout_user(token)
    assert result["success"] is True

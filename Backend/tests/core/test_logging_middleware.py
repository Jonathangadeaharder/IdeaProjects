"""
Unit tests for LoggingMiddleware to ensure header is added and no body consumption.
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx
from contextlib import asynccontextmanager

from core.middleware import LoggingMiddleware


@pytest.mark.asyncio
async def test_logging_middleware_adds_header():
    app = FastAPI()

    @asynccontextmanager
    async def no_lifespan(_app):
        yield
    app.router.lifespan_context = no_lifespan

    app.add_middleware(LoggingMiddleware)

    @app.get("/ping")
    async def ping():
        return JSONResponse({"ok": True})

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        r = await client.get("/ping")
        assert r.status_code == 200
        assert "X-Process-Time" in r.headers
        # Body should be intact
        assert r.json()["ok"] is True


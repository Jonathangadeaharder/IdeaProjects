#!/usr/bin/env python3
"""
LangPlug - German Language Learning Platform
Entry point for the FastAPI server
"""

import uvicorn
from core.app import create_app
from core.config import settings

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        reload_dirs=[str(settings.get_data_path().parent)]
    )
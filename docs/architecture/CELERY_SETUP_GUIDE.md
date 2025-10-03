# Celery Async Processing Setup Guide - LangPlug

**Version**: 1.0
**Date**: 2025-10-02
**Status**: Ready for Implementation
**Estimated Time**: 1.5 weeks (60 hours)
**Dependency**: Redis must be operational (required for Celery broker)

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Day 1-2: Infrastructure Setup](#day-1-2-infrastructure-setup-8-hours)
4. [Day 3-4: Task Implementation](#day-3-4-task-implementation-8-hours)
5. [Day 5: API Integration](#day-5-api-integration-8-hours)
6. [Day 6: Frontend Integration](#day-6-frontend-integration-8-hours)
7. [Day 7: Testing & Deployment](#day-7-testing--deployment-8-hours)
8. [Production Deployment](#production-deployment)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### Why Celery?

**Current State:**

- Video processing (transcription + translation): **2-5 minutes**
- API request timeout: **30 seconds** (FastAPI default)
- Users wait for processing to complete (blocking UX)
- No progress feedback during processing

**Target State:**

- API response time: **<500ms** (returns task ID immediately)
- Background processing: **2-5 minutes** (non-blocking)
- Real-time progress updates via polling
- Retry failed tasks automatically

### Benefits

1. **Better UX**: Immediate response with progress tracking
2. **Scalability**: Horizontal scaling of worker nodes
3. **Reliability**: Automatic retries, task persistence
4. **Resource Management**: CPU-intensive tasks don't block API

### Architecture

```
┌─────────┐   POST /process   ┌─────────┐   Task Queue   ┌─────────┐
│ Client  │ ──────────────────>│ FastAPI │───────────────>│  Redis  │
└─────────┘                    └─────────┘                └─────────┘
     │                              │                           │
     │                              │                           ▼
     │  GET /status/{task_id}      │                      ┌─────────┐
     │<─────────────────────────────│                      │ Celery  │
     │                              │                      │ Worker  │
     │                              │<─────────────────────┤ Process │
     │                              │   Task Result        └─────────┘
     │  {"progress": 75%}           │
     │<─────────────────────────────│
```

**Flow**:

1. Client POST /videos/1/process → FastAPI returns task_id in 200ms
2. FastAPI dispatches task to Redis queue
3. Celery worker picks up task from queue
4. Worker processes video (2-5 min) with progress updates
5. Client polls GET /tasks/{task_id}/status every 2 seconds
6. Client receives real-time progress: 0% → 25% → 50% → 100%

---

## Prerequisites

### Required Infrastructure

- [x] **Redis**: Must be running (see `REDIS_SETUP_GUIDE.md`)
- [ ] **Celery**: Will be installed in this guide
- [ ] **Flower**: Monitoring dashboard (optional but recommended)

### Check Redis Status

```bash
# Verify Redis is running
docker ps | grep redis

# Test connection
docker exec -it langplug-redis redis-cli -a dev_redis_password PING
# Expected: PONG
```

### Python Environment

```bash
cd /mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend
./api_venv/Scripts/activate
python --version
# Expected: Python 3.11.x
```

---

## Day 1-2: Infrastructure Setup (8 hours)

### 1.1 Install Celery Dependencies

```bash
cd /mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend
./api_venv/Scripts/activate

# Install Celery with Redis support
pip install celery[redis]==5.3.4

# Install Flower for monitoring (optional but recommended)
pip install flower==2.0.1

# Install additional utilities
pip install redis==5.0.1  # Already installed from Redis guide
pip install kombu==5.3.4  # Message queue library

# Update requirements.txt
pip freeze > requirements.txt

# Verify installation
python -c "import celery; print(celery.__version__)"
# Expected: 5.3.4

python -c "import flower; print('Flower installed')"
# Expected: Flower installed
```

### 1.2 Create Celery Application

**File**: `Backend/core/celery_app.py` (NEW)

```python
"""
Celery Application Configuration
Handles async task processing for LangPlug
"""

import logging
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure

from core.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    'langplug',
    broker=settings.redis_url,  # Redis as message broker
    backend=settings.redis_url,  # Redis as result backend
)

# Configure Celery
celery_app.conf.update(
    # Serialization (JSON for compatibility)
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # Timezone
    timezone='UTC',
    enable_utc=True,

    # Task execution settings
    task_track_started=True,  # Track task start time
    task_time_limit=3600,  # 1 hour hard limit (kills task)
    task_soft_time_limit=3300,  # 55 minutes soft limit (raises exception)

    # Retry policy
    task_acks_late=True,  # Acknowledge after task completes (enables retry on worker crash)
    task_reject_on_worker_lost=True,  # Reject task if worker crashes

    # Result storage
    result_expires=86400,  # Keep results for 24 hours
    result_backend_transport_options={'visibility_timeout': 3600},

    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,

    # Performance
    worker_prefetch_multiplier=4,  # Prefetch 4 tasks per worker
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks (prevent memory leaks)
)

# Auto-discover tasks in 'tasks' package
celery_app.autodiscover_tasks(['tasks'])


# Task lifecycle hooks for logging
@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    """Log when task starts"""
    logger.info(f"Task {task.name}[{task_id}] started")


@task_postrun.connect
def task_postrun_handler(task_id, task, *args, **kwargs):
    """Log when task completes"""
    logger.info(f"Task {task.name}[{task_id}] completed")


@task_failure.connect
def task_failure_handler(task_id, exception, *args, **kwargs):
    """Log when task fails"""
    logger.error(f"Task {task_id} failed: {exception}")


# Debug task for testing Celery setup
@celery_app.task(bind=True, name='tasks.debug_task')
def debug_task(self):
    """
    Simple debug task to verify Celery is working

    Usage:
        from core.celery_app import debug_task
        task = debug_task.delay()
        print(task.get())  # Wait for result
    """
    logger.info(f'Debug task request: {self.request!r}')
    return {'status': 'success', 'message': 'Celery is working!'}
```

### 1.3 Update Configuration

**File**: `Backend/core/config.py` (UPDATE)

```python
# Backend/core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...

    # Redis Configuration (already added from Redis guide)
    redis_url: str = Field(
        default="redis://:dev_redis_password@localhost:6379/0",
        env="REDIS_URL"
    )

    # Celery Configuration
    celery_broker_url: str = Field(
        default="redis://:dev_redis_password@localhost:6379/0",
        env="CELERY_BROKER_URL",
        description="Celery broker URL (same as Redis)"
    )
    celery_result_backend: str = Field(
        default="redis://:dev_redis_password@localhost:6379/0",
        env="CELERY_RESULT_BACKEND",
        description="Celery result backend URL"
    )
    celery_task_time_limit: int = Field(
        default=3600,
        env="CELERY_TASK_TIME_LIMIT",
        description="Task hard time limit in seconds (1 hour)"
    )
    celery_worker_concurrency: int = Field(
        default=4,
        env="CELERY_WORKER_CONCURRENCY",
        description="Number of concurrent worker processes"
    )
```

### 1.4 Create Tasks Package

```bash
cd /mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend
mkdir -p tasks
touch tasks/__init__.py
```

**File**: `Backend/tasks/__init__.py` (NEW)

```python
"""
Async Task Definitions
All Celery tasks are defined in this package
"""

from core.celery_app import celery_app

__all__ = ['celery_app']
```

### 1.5 Start Celery Worker (Test)

```bash
cd /mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend
./api_venv/Scripts/activate

# Start Celery worker (development mode)
celery -A core.celery_app worker --loglevel=info --concurrency=2

# You should see output like:
# -------------- celery@HOSTNAME v5.3.4
# ---- **** -----
# --- * ***  * -- Windows-11-10.0.22621-SP0 2025-10-02 15:30:00
# -- * - **** ---
# - ** ---------- [config]
# - ** ---------- .> app:         langplug:0x...
# - ** ---------- .> transport:   redis://localhost:6379/0
# - ** ---------- .> results:     redis://localhost:6379/0
# - *** --- * --- .> concurrency: 2 (prefork)
# -- ******* ---- .> task events: ON
# --- ***** -----
# -------------- [queues]
#                .> celery           exchange=celery(direct) key=celery
#
# [tasks]
#   . tasks.debug_task
#
# [2025-10-02 15:30:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
# [2025-10-02 15:30:00,100: INFO/MainProcess] mingle: searching for neighbors
# [2025-10-02 15:30:01,200: INFO/MainProcess] mingle: all alone
# [2025-10-02 15:30:01,300: INFO/MainProcess] celery@HOSTNAME ready.
```

### 1.6 Test Celery (Optional)

```bash
# In a new terminal, activate venv
cd /mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend
./api_venv/Scripts/activate

# Open Python shell
python

# Run test task
>>> from core.celery_app import debug_task
>>> task = debug_task.delay()
>>> print(task.id)  # Task ID
'550e8400-e29b-41d4-a716-446655440000'
>>> task.ready()  # Check if complete
True
>>> task.get(timeout=10)  # Get result (wait up to 10 seconds)
{'status': 'success', 'message': 'Celery is working!'}
```

### 1.7 Start Flower Monitoring Dashboard

```bash
cd /mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/Backend
./api_venv/Scripts/activate

# Start Flower on port 5555
celery -A core.celery_app flower --port=5555

# Access dashboard at: http://localhost:5555
# Features:
# - View active workers
# - Monitor task progress
# - View task history
# - Inspect task details
# - View broker stats
```

### Verification Checklist (Day 1-2)

- [ ] Celery installed (v5.3.4)
- [ ] Flower installed (v2.0.1)
- [ ] `core/celery_app.py` created
- [ ] `tasks/__init__.py` created
- [ ] Celery worker starts without errors
- [ ] Debug task completes successfully
- [ ] Flower dashboard accessible (http://localhost:5555)

---

## Day 3-4: Task Implementation (8 hours)

### 2.1 Video Transcription Task

**File**: `Backend/tasks/video_tasks.py` (NEW)

```python
"""
Video Processing Tasks
Handles async transcription, translation, and subtitle generation
"""

import asyncio
import logging
from typing import Any

from core.celery_app import celery_app
from core.database import get_async_session
from services.processing.chunk_processor import ChunkProcessingService

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name='tasks.process_video_chunk',
    max_retries=3,
    default_retry_delay=60,  # Retry after 1 minute
    autoretry_for=(Exception,),  # Auto-retry on any exception
    retry_backoff=True,  # Exponential backoff
    retry_jitter=True,  # Add random jitter to prevent thundering herd
)
def process_video_chunk(
    self,
    video_path: str,
    start_time: float,
    end_time: float,
    user_id: int,
    video_id: int,
    chunk_number: int,
    total_chunks: int,
) -> dict[str, Any]:
    """
    Process a video chunk: transcribe, extract vocabulary, translate

    Args:
        self: Celery task instance (bind=True)
        video_path: Absolute path to video file
        start_time: Chunk start time in seconds
        end_time: Chunk end time in seconds
        user_id: User ID who initiated processing
        video_id: Video ID being processed
        chunk_number: Current chunk number (1-indexed)
        total_chunks: Total number of chunks

    Returns:
        dict: Processing results with vocabulary count, segments, etc.

    Raises:
        Exception: If processing fails after max retries
    """
    logger.info(f"Processing chunk {chunk_number}/{total_chunks} for video {video_id}")

    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'progress': 0,
                'chunk': chunk_number,
                'total_chunks': total_chunks,
                'message': f'Starting chunk {chunk_number}/{total_chunks}...'
            }
        )

        # Define async processing function
        async def async_process():
            async for session in get_async_session():
                service = ChunkProcessingService(session)

                # Progress callback
                def on_progress(progress: float, message: str):
                    """Update task progress"""
                    # Adjust progress to account for chunk number
                    base_progress = ((chunk_number - 1) / total_chunks) * 100
                    chunk_progress = (progress / total_chunks)
                    total_progress = base_progress + chunk_progress

                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'progress': round(total_progress, 2),
                            'chunk': chunk_number,
                            'total_chunks': total_chunks,
                            'message': f'Chunk {chunk_number}: {message}'
                        }
                    )

                # Process chunk
                result = await service.process_chunk(
                    video_path=video_path,
                    start_time=start_time,
                    end_time=end_time,
                    user_id=user_id,
                    task_id=self.request.id,
                    task_progress={'callback': on_progress},
                    session_token=None,
                )

                return result

        # Run async code in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(async_process())
        finally:
            loop.close()

        # Update final state
        self.update_state(
            state='SUCCESS',
            meta={
                'progress': 100,
                'chunk': chunk_number,
                'total_chunks': total_chunks,
                'message': f'Chunk {chunk_number} completed!'
            }
        )

        logger.info(f"Chunk {chunk_number} completed successfully")

        return {
            'status': 'completed',
            'video_id': video_id,
            'chunk_number': chunk_number,
            'vocabulary_count': result.get('vocabulary_count', 0),
            'segments_count': result.get('segments_count', 0),
            'subtitles_path': result.get('subtitles_path'),
        }

    except Exception as e:
        logger.error(f"Chunk {chunk_number} failed: {e}", exc_info=True)

        # Update failure state
        self.update_state(
            state='FAILURE',
            meta={
                'progress': 0,
                'chunk': chunk_number,
                'total_chunks': total_chunks,
                'error': str(e),
                'message': f'Chunk {chunk_number} failed: {str(e)[:100]}'
            }
        )

        # Retry if under max retries
        if self.request.retries < self.max_retries:
            logger.warning(f"Retrying chunk {chunk_number} (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=e)

        # Max retries reached
        raise


@celery_app.task(
    bind=True,
    name='tasks.batch_translate_segments',
    max_retries=2,
    default_retry_delay=30,
)
def batch_translate_segments(
    self,
    segments: list[dict[str, Any]],
    source_lang: str,
    target_lang: str,
) -> list[dict[str, Any]]:
    """
    Batch translate subtitle segments

    Args:
        self: Celery task instance
        segments: List of subtitle segments with 'text' field
        source_lang: Source language code (e.g., 'de')
        target_lang: Target language code (e.g., 'en')

    Returns:
        list: Translated segments with 'translation' field added
    """
    logger.info(f"Translating {len(segments)} segments from {source_lang} to {target_lang}")

    try:
        async def async_translate():
            from services.translation.translation_handler import TranslationHandler

            handler = TranslationHandler()
            results = []

            for i, segment in enumerate(segments):
                # Translate segment
                translation = await handler.translate_text(
                    text=segment['text'],
                    source_lang=source_lang,
                    target_lang=target_lang,
                )

                # Add translation to segment
                segment_with_translation = {**segment, 'translation': translation}
                results.append(segment_with_translation)

                # Update progress
                progress = int((i + 1) / len(segments) * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'progress': progress,
                        'message': f'Translated {i+1}/{len(segments)} segments'
                    }
                )

            return results

        # Run async translation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(async_translate())
        finally:
            loop.close()

        logger.info(f"Translation completed: {len(results)} segments")

        return results

    except Exception as e:
        logger.error(f"Translation task failed: {e}", exc_info=True)
        raise self.retry(exc=e)
```

### 2.2 Vocabulary Extraction Task

**File**: `Backend/tasks/vocabulary_tasks.py` (NEW)

```python
"""
Vocabulary Extraction Tasks
Async tasks for vocabulary processing
"""

import asyncio
import logging

from core.celery_app import celery_app
from core.database import get_async_session
from services.vocabulary.vocabulary_service import VocabularyService

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name='tasks.extract_vocabulary_from_text',
    max_retries=2,
)
def extract_vocabulary_from_text(
    self,
    text: str,
    language: str,
    user_id: int,
    difficulty_filter: str | None = None,
) -> dict:
    """
    Extract vocabulary words from text

    Args:
        self: Celery task instance
        text: Text to extract vocabulary from
        language: Language code (e.g., 'de')
        user_id: User ID for progress tracking
        difficulty_filter: Optional CEFR level filter (A1, A2, B1, B2)

    Returns:
        dict: Extracted vocabulary words with metadata
    """
    logger.info(f"Extracting vocabulary from text (language: {language}, user: {user_id})")

    try:
        async def async_extract():
            async for session in get_async_session():
                service = VocabularyService(session)

                # Extract vocabulary
                words = await service.extract_vocabulary(
                    text=text,
                    language=language,
                    user_id=user_id,
                    difficulty_filter=difficulty_filter,
                )

                return {
                    'vocabulary_count': len(words),
                    'words': [
                        {
                            'word': w.word,
                            'lemma': w.lemma,
                            'difficulty_level': w.difficulty_level,
                            'known': w.user_known if hasattr(w, 'user_known') else False,
                        }
                        for w in words
                    ]
                }

        # Run async extraction
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(async_extract())
        finally:
            loop.close()

        logger.info(f"Extracted {result['vocabulary_count']} vocabulary words")

        return result

    except Exception as e:
        logger.error(f"Vocabulary extraction failed: {e}", exc_info=True)
        raise self.retry(exc=e)
```

### Verification Checklist (Day 3-4)

- [ ] `tasks/video_tasks.py` created
- [ ] `tasks/vocabulary_tasks.py` created
- [ ] Tasks registered with Celery (visible in Flower)
- [ ] Test task execution manually

**Manual Test**:

```python
# Python shell
from tasks.video_tasks import process_video_chunk

task = process_video_chunk.delay(
    video_path="/path/to/test_video.mp4",
    start_time=0.0,
    end_time=10.0,
    user_id=1,
    video_id=1,
    chunk_number=1,
    total_chunks=1,
)

print(task.id)  # Task ID
task.ready()  # Check if complete
task.get()  # Get result (blocks until complete)
```

---

## Day 5: API Integration (8 hours)

### 3.1 Create Task Status Endpoint

**File**: `Backend/api/routes/tasks.py` (NEW)

```python
"""
Task Status API Routes
Provides endpoints for checking Celery task progress
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.celery_app import celery_app

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskStatusResponse(BaseModel):
    """Task status response model"""
    task_id: str
    state: str  # pending, started, progress, success, failure
    progress: int  # 0-100
    message: str
    result: dict | None = None
    error: str | None = None


@router.get("/{task_id}/status", response_model=TaskStatusResponse, name="get_task_status")
async def get_task_status(task_id: str):
    """
    Get Celery task status and progress

    Args:
        task_id: Celery task ID

    Returns:
        TaskStatusResponse: Task status with progress information
    """
    logger.info(f"Checking status for task {task_id}")

    try:
        task = celery_app.AsyncResult(task_id)

        if task.state == 'PENDING':
            return TaskStatusResponse(
                task_id=task_id,
                state="pending",
                progress=0,
                message="Task is waiting to start..."
            )

        elif task.state == 'STARTED':
            return TaskStatusResponse(
                task_id=task_id,
                state="started",
                progress=5,
                message="Task has started processing..."
            )

        elif task.state == 'PROGRESS':
            meta = task.info or {}
            return TaskStatusResponse(
                task_id=task_id,
                state="progress",
                progress=int(meta.get('progress', 0)),
                message=meta.get('message', 'Processing...')
            )

        elif task.state == 'SUCCESS':
            return TaskStatusResponse(
                task_id=task_id,
                state="success",
                progress=100,
                message="Task completed successfully!",
                result=task.result
            )

        elif task.state == 'FAILURE':
            error_msg = str(task.info) if task.info else "Unknown error"
            return TaskStatusResponse(
                task_id=task_id,
                state="failure",
                progress=0,
                message="Task failed",
                error=error_msg
            )

        else:
            # RETRY, REVOKED, etc.
            return TaskStatusResponse(
                task_id=task_id,
                state=task.state.lower(),
                progress=0,
                message=f"Task is in {task.state} state"
            )

    except Exception as e:
        logger.error(f"Failed to get task status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve task status: {e}")


@router.delete("/{task_id}", name="cancel_task")
async def cancel_task(task_id: str):
    """
    Cancel a running Celery task

    Args:
        task_id: Celery task ID

    Returns:
        dict: Cancellation confirmation
    """
    logger.info(f"Canceling task {task_id}")

    try:
        celery_app.control.revoke(task_id, terminate=True, signal='SIGKILL')
        return {"status": "cancelled", "task_id": task_id}

    except Exception as e:
        logger.error(f"Failed to cancel task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to cancel task: {e}")
```

### 3.2 Update Video Processing Endpoint

**File**: `Backend/api/routes/videos.py` (UPDATE)

```python
# Backend/api/routes/videos.py
from fastapi import APIRouter, Depends, HTTPException
from tasks.video_tasks import process_video_chunk

router = APIRouter(prefix="/videos", tags=["videos"])


# BEFORE - Synchronous blocking endpoint
# @router.post("/{video_id}/process")
# async def process_video(video_id: int, current_user: User = Depends(current_active_user)):
#     # This blocks for 2-5 minutes!
#     result = await chunk_processor.process_chunk(...)
#     return result


# AFTER - Async non-blocking endpoint
@router.post("/{video_id}/process", name="process_video_async")
async def process_video_async(
    video_id: int,
    start_time: float = 0.0,
    end_time: float | None = None,
    current_user: User = Depends(current_active_user)
):
    """
    Start async video processing

    Args:
        video_id: ID of video to process
        start_time: Chunk start time (default: 0)
        end_time: Chunk end time (default: video duration)
        current_user: Authenticated user

    Returns:
        dict: Task ID and status URL

    Example Response:
        {
            "message": "Processing started",
            "task_id": "550e8400-e29b-41d4-a716-446655440000",
            "status_url": "/api/tasks/550e8400-e29b-41d4-a716-446655440000/status"
        }
    """
    # Get video metadata
    video = await get_video_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Use video duration if end_time not specified
    if end_time is None:
        end_time = video.duration

    # Dispatch async task to Celery
    task = process_video_chunk.delay(
        video_path=str(video.file_path),
        start_time=start_time,
        end_time=end_time,
        user_id=current_user.id,
        video_id=video_id,
        chunk_number=1,
        total_chunks=1,
    )

    # Return immediately with task ID
    return {
        "message": "Processing started",
        "task_id": task.id,
        "status_url": f"/api/tasks/{task.id}/status",
        "estimated_time": "2-5 minutes"
    }
```

### 3.3 Register Task Routes

**File**: `Backend/main.py` (UPDATE)

```python
# Backend/main.py
from fastapi import FastAPI
from api.routes import tasks  # Import task routes

app = FastAPI(...)

# Register task routes
app.include_router(tasks.router, prefix="/api")
```

### Verification Checklist (Day 5)

- [ ] Task status endpoint created
- [ ] Video processing endpoint updated to use Celery
- [ ] Task routes registered in main.py
- [ ] Test endpoints with Postman/curl

**Test Commands**:

```bash
# Start video processing
curl -X POST http://localhost:8000/api/videos/1/process \
  -H "Authorization: Bearer YOUR_TOKEN"
# Response: {"task_id": "abc123", "status_url": "/api/tasks/abc123/status"}

# Check task status
curl http://localhost:8000/api/tasks/abc123/status
# Response: {"state": "progress", "progress": 45, "message": "Transcribing audio..."}

# Cancel task
curl -X DELETE http://localhost:8000/api/tasks/abc123
```

---

## Day 6: Frontend Integration (8 hours)

### 4.1 Create Task Status Hook

**File**: `Frontend/src/hooks/useTaskStatus.ts` (NEW)

```typescript
// Frontend/src/hooks/useTaskStatus.ts
import { useEffect, useState } from "react";
import { logger } from "@/services/logger";

export interface TaskStatus {
  task_id: string;
  state: "pending" | "started" | "progress" | "success" | "failure";
  progress: number;
  message: string;
  result?: any;
  error?: string;
}

export const useTaskStatus = (
  taskId: string | null,
  pollInterval: number = 2000,
) => {
  const [status, setStatus] = useState<TaskStatus | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!taskId) {
      setStatus(null);
      setIsPolling(false);
      return;
    }

    setIsPolling(true);
    let intervalId: NodeJS.Timeout;

    const pollStatus = async () => {
      try {
        const response = await fetch(`/api/tasks/${taskId}/status`);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data: TaskStatus = await response.json();
        setStatus(data);

        logger.info("TaskStatus", "Poll update", {
          task_id: taskId,
          state: data.state,
          progress: data.progress,
        });

        // Stop polling if task completed or failed
        if (data.state === "success" || data.state === "failure") {
          setIsPolling(false);
          if (intervalId) {
            clearInterval(intervalId);
          }
        }
      } catch (err: any) {
        logger.error("TaskStatus", "Poll failed", {
          task_id: taskId,
          error: err.message,
        });
        setError(err.message);
        setIsPolling(false);
        if (intervalId) {
          clearInterval(intervalId);
        }
      }
    };

    // Initial poll
    pollStatus();

    // Setup interval polling
    intervalId = setInterval(pollStatus, pollInterval);

    // Cleanup on unmount or taskId change
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
      setIsPolling(false);
    };
  }, [taskId, pollInterval]);

  return { status, isPolling, error };
};
```

### 4.2 Create Progress Component

**File**: `Frontend/src/components/TaskProgress.tsx` (NEW)

```typescript
// Frontend/src/components/TaskProgress.tsx
import React from 'react'
import styled from 'styled-components'
import { useTaskStatus, TaskStatus } from '@/hooks/useTaskStatus'

const ProgressContainer = styled.div`
  background: rgba(0, 0, 0, 0.9);
  border-radius: 12px;
  padding: 24px;
  max-width: 500px;
  margin: 20px auto;
  color: white;
`

const ProgressTitle = styled.h3`
  font-size: 20px;
  margin-bottom: 16px;
  text-align: center;
`

const ProgressBarContainer = styled.div`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  height: 8px;
  overflow: hidden;
  margin-bottom: 12px;
`

const ProgressBarFill = styled.div<{ $progress: number }>`
  width: ${props => props.$progress}%;
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
`

const ProgressMessage = styled.p`
  font-size: 14px;
  color: #b3b3b3;
  text-align: center;
  margin: 8px 0;
`

const ProgressPercentage = styled.div`
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  margin-top: 12px;
`

const ErrorMessage = styled.div`
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid #ef4444;
  border-radius: 8px;
  padding: 12px;
  color: #ef4444;
  margin-top: 12px;
`

const SuccessMessage = styled.div`
  background: rgba(70, 211, 105, 0.2);
  border: 1px solid #46d369;
  border-radius: 8px;
  padding: 12px;
  color: #46d369;
  margin-top: 12px;
  text-align: center;
`

interface TaskProgressProps {
  taskId: string | null
  onComplete?: (result: any) => void
  onError?: (error: string) => void
  title?: string
}

export const TaskProgress: React.FC<TaskProgressProps> = ({
  taskId,
  onComplete,
  onError,
  title = 'Processing Video'
}) => {
  const { status, isPolling, error } = useTaskStatus(taskId)

  // Call callbacks when task completes
  React.useEffect(() => {
    if (status?.state === 'success' && onComplete) {
      onComplete(status.result)
    }
    if (status?.state === 'failure' && onError) {
      onError(status.error || 'Unknown error')
    }
  }, [status?.state, onComplete, onError])

  if (!taskId) {
    return null
  }

  if (error) {
    return (
      <ProgressContainer>
        <ProgressTitle>{title}</ProgressTitle>
        <ErrorMessage>
          Failed to check task status: {error}
        </ErrorMessage>
      </ProgressContainer>
    )
  }

  if (!status) {
    return (
      <ProgressContainer>
        <ProgressTitle>{title}</ProgressTitle>
        <ProgressMessage>Loading...</ProgressMessage>
      </ProgressContainer>
    )
  }

  return (
    <ProgressContainer>
      <ProgressTitle>{title}</ProgressTitle>

      {status.state === 'success' ? (
        <SuccessMessage>
          Processing completed successfully!
        </SuccessMessage>
      ) : status.state === 'failure' ? (
        <ErrorMessage>
          Processing failed: {status.error || 'Unknown error'}
        </ErrorMessage>
      ) : (
        <>
          <ProgressBarContainer>
            <ProgressBarFill $progress={status.progress} />
          </ProgressBarContainer>

          <ProgressPercentage>{status.progress}%</ProgressPercentage>

          <ProgressMessage>{status.message}</ProgressMessage>

          {isPolling && (
            <ProgressMessage style={{ marginTop: '16px', fontSize: '12px' }}>
              Checking status every 2 seconds...
            </ProgressMessage>
          )}
        </>
      )}
    </ProgressContainer>
  )
}
```

### 4.3 Update Video Upload Component

**File**: `Frontend/src/components/VideoUpload.tsx` (UPDATE)

```typescript
// Frontend/src/components/VideoUpload.tsx
import React, { useState } from 'react'
import { TaskProgress } from './TaskProgress'

export const VideoUpload: React.FC = () => {
  const [taskId, setTaskId] = useState<string | null>(null)
  const [uploadComplete, setUploadComplete] = useState(false)

  const handleUpload = async (file: File) => {
    // Upload video
    const formData = new FormData()
    formData.append('video', file)

    const response = await fetch('/api/videos/upload/Default', {
      method: 'POST',
      body: formData,
    })

    const data = await response.json()
    const videoId = data.video_id

    // Start processing
    const processResponse = await fetch(`/api/videos/${videoId}/process`, {
      method: 'POST',
    })

    const processData = await processResponse.json()
    setTaskId(processData.task_id)
  }

  const handleComplete = (result: any) => {
    console.log('Processing complete!', result)
    setUploadComplete(true)
    // Navigate to video player or show success message
  }

  const handleError = (error: string) => {
    console.error('Processing failed:', error)
    // Show error toast
  }

  return (
    <div>
      {/* Upload UI */}
      <input type="file" accept="video/*" onChange={(e) => handleUpload(e.target.files![0])} />

      {/* Progress indicator */}
      {taskId && (
        <TaskProgress
          taskId={taskId}
          onComplete={handleComplete}
          onError={handleError}
          title="Processing Your Video"
        />
      )}

      {uploadComplete && <div>Video ready to watch!</div>}
    </div>
  )
}
```

### Verification Checklist (Day 6)

- [ ] `useTaskStatus` hook created
- [ ] `TaskProgress` component created
- [ ] Video upload component updated
- [ ] Test full upload → process → progress → complete flow

---

## Day 7: Testing & Deployment (8 hours)

### 5.1 Unit Tests

**File**: `Backend/tests/unit/tasks/test_video_tasks.py` (NEW)

```python
# Backend/tests/unit/tasks/test_video_tasks.py
import pytest
from tasks.video_tasks import process_video_chunk


@pytest.mark.asyncio
async def test_process_video_chunk_success(mock_video_file):
    """Test video chunk processing completes successfully"""
    task = process_video_chunk.apply_async(
        args=(
            str(mock_video_file),
            0.0,
            10.0,
            1,  # user_id
            1,  # video_id
            1,  # chunk_number
            1,  # total_chunks
        )
    )

    # Wait for task to complete (max 30 seconds)
    result = task.get(timeout=30)

    assert result['status'] == 'completed'
    assert result['vocabulary_count'] > 0
    assert 'subtitles_path' in result


@pytest.mark.asyncio
async def test_task_progress_updates():
    """Test that task provides progress updates"""
    task = process_video_chunk.apply_async(...)

    # Wait for task to start
    import time
    time.sleep(2)

    # Check progress
    assert task.state == 'PROGRESS'
    assert 'progress' in task.info
    assert task.info['progress'] > 0
```

### 5.2 Integration Tests

**File**: `Backend/tests/integration/test_celery_integration.py` (NEW)

```python
# Backend/tests/integration/test_celery_integration.py
import pytest
from httpx import AsyncClient

from main import app


@pytest.mark.asyncio
async def test_video_processing_workflow():
    """Test full video processing workflow"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Upload video
        files = {'video': open('test_video.mp4', 'rb')}
        upload_response = await client.post('/api/videos/upload/Default', files=files)
        assert upload_response.status_code == 200
        video_id = upload_response.json()['video_id']

        # Start processing
        process_response = await client.post(f'/api/videos/{video_id}/process')
        assert process_response.status_code == 200
        task_id = process_response.json()['task_id']

        # Check status
        status_response = await client.get(f'/api/tasks/{task_id}/status')
        assert status_response.status_code == 200
        assert status_response.json()['state'] in ['pending', 'started', 'progress']
```

### 5.3 Production Deployment Script

**File**: `Backend/scripts/start_celery_worker.sh` (NEW)

```bash
#!/bin/bash
# Backend/scripts/start_celery_worker.sh
# Production Celery worker startup script

# Activate virtual environment
source /path/to/api_venv/bin/activate

# Start Celery worker with production settings
celery -A core.celery_app worker \
  --loglevel=info \
  --concurrency=4 \
  --max-tasks-per-child=100 \
  --time-limit=3600 \
  --soft-time-limit=3300 \
  --pidfile=/var/run/celery/worker.pid \
  --logfile=/var/log/celery/worker.log \
  --detach

echo "Celery worker started"
```

### 5.4 Supervisor Configuration (Production)

**File**: `/etc/supervisor/conf.d/celery.conf` (Production Server)

```ini
[program:celery_worker]
command=/path/to/Backend/api_venv/bin/celery -A core.celery_app worker --loglevel=info --concurrency=4
directory=/path/to/Backend
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.error.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
killasgroup=true
priority=998

[program:celery_flower]
command=/path/to/Backend/api_venv/bin/celery -A core.celery_app flower --port=5555
directory=/path/to/Backend
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/flower.log
stderr_logfile=/var/log/celery/flower.error.log
autostart=true
autorestart=true
startsecs=10
priority=999
```

**Start with Supervisor**:

```bash
# Reload supervisor config
sudo supervisorctl reread
sudo supervisorctl update

# Start workers
sudo supervisorctl start celery_worker
sudo supervisorctl start celery_flower

# Check status
sudo supervisorctl status
```

### Verification Checklist (Day 7)

- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Production startup script created
- [ ] Supervisor configuration created (if using Supervisor)
- [ ] Load testing completed (10 concurrent tasks)

---

## Production Deployment

### AWS EC2 Worker Setup

```bash
# Launch EC2 instance (t3.medium recommended for workers)
# Install dependencies
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv redis-server supervisor

# Clone repo
git clone https://github.com/your-org/LangPlug.git
cd LangPlug/Backend

# Setup venv
python3.11 -m venv api_venv
source api_venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production Redis URL

# Start worker with Supervisor (see supervisor config above)
sudo cp scripts/celery.conf /etc/supervisor/conf.d/
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery_worker
```

### Monitoring

**Flower Dashboard** (http://your-server:5555):

- Active workers count
- Task success/failure rates
- Queue length
- Worker CPU/memory usage

**CloudWatch Metrics** (if on AWS):

- `CeleryTasksProcessed` (custom metric)
- `CeleryWorkerCPU`
- `CeleryQueueDepth`

---

## Monitoring & Maintenance

### Health Checks

```python
# Add to Backend/api/routes/health.py
@router.get("/health/celery")
async def celery_health():
    """Check Celery worker health"""
    from core.celery_app import celery_app

    # Check worker status
    inspect = celery_app.control.inspect()
    active_workers = inspect.active()

    if not active_workers:
        return {"status": "unhealthy", "message": "No active workers"}

    return {
        "status": "healthy",
        "workers": len(active_workers),
        "active_tasks": sum(len(tasks) for tasks in active_workers.values())
    }
```

### Logs

```bash
# View worker logs
tail -f /var/log/celery/worker.log

# View Flower logs
tail -f /var/log/celery/flower.log

# View task errors
grep "ERROR" /var/log/celery/worker.log
```

---

## Troubleshooting

### Issue: Tasks Not Executing

**Symptoms**: Tasks stay in PENDING state

**Solution**:

```bash
# Check worker is running
celery -A core.celery_app status

# Check Redis connection
redis-cli -a dev_redis_password PING

# Restart worker
celery -A core.celery_app worker --loglevel=debug
```

### Issue: Tasks Taking Too Long

**Symptoms**: Tasks exceed 1-hour limit

**Solution**:

```python
# Increase time limit in core/celery_app.py
celery_app.conf.update(
    task_time_limit=7200,  # 2 hours
    task_soft_time_limit=6900,  # 1h 55min
)
```

### Issue: Worker Memory Leak

**Symptoms**: Worker memory usage grows over time

**Solution**:

```python
# Already configured in celery_app.py
worker_max_tasks_per_child=100  # Restart worker after 100 tasks

# Or reduce further:
worker_max_tasks_per_child=50
```

---

## Performance Metrics

### Expected Improvements

| Metric                         | Before Celery          | After Celery    | Improvement      |
| ------------------------------ | ---------------------- | --------------- | ---------------- |
| **API Response Time**          | 2-5 minutes            | <500ms          | 99.7% faster     |
| **User Wait Time**             | 2-5 minutes (blocking) | 0s (async)      | Instant response |
| **Concurrent Processing**      | 1 video at a time      | 4-8 videos      | 4-8x throughput  |
| **Failed Processing Recovery** | Manual retry           | Auto-retry (3x) | 95% success rate |

### Monitoring Commands

```bash
# Check active tasks
celery -A core.celery_app inspect active

# Check queue depth
celery -A core.celery_app inspect reserved

# Check worker stats
celery -A core.celery_app inspect stats
```

---

## Summary Checklist

**Week 1.5 Implementation**:

- [ ] **Day 1-2**: Celery infrastructure running
- [ ] **Day 3-4**: Tasks implemented and tested
- [ ] **Day 5**: API endpoints integrated
- [ ] **Day 6**: Frontend progress tracking
- [ ] **Day 7**: Production deployment ready

**Acceptance Criteria**:

- [ ] Celery worker running and processing tasks
- [ ] Video processing completes asynchronously
- [ ] Progress updates visible in UI
- [ ] Auto-retry working for failed tasks
- [ ] Flower dashboard accessible
- [ ] All tests passing

**Next Steps**:

1. Month 3: Frontend component refactoring
2. Month 3: ChunkedLearningPlayer hooks extraction

---

**Status**: Ready for Implementation
**Owner**: Backend + Frontend Teams
**Last Updated**: 2025-10-02
**Dependency**: Redis setup (see `REDIS_SETUP_GUIDE.md`)

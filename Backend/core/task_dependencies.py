"""Task and lifecycle dependencies for FastAPI"""

from .logging_config import get_logger

logger = get_logger(__name__)

# Global task progress registry for background tasks
_task_progress_registry: dict = {}


def get_task_progress_registry() -> dict:
    """
    Get task progress registry for background tasks

    Note:
        Returns reference to global registry without caching.
        Previously used @lru_cache which caused test state pollution.
    """
    return _task_progress_registry


async def init_services():
    """Initialize all services on startup"""
    logger.info("[STARTUP] Initializing services...")
    logger.info("[STARTUP] This may take 5-10 minutes on first run to download AI models")

    # Initialize database tables
    logger.info("[STARTUP] Step 1/4: Initializing database...")
    from .database import init_db

    await init_db()
    logger.info("[STARTUP] Database initialized successfully")

    # Initialize transcription service
    logger.info("[STARTUP] Step 2/4: Initializing transcription service...")
    logger.info("[STARTUP] Using model: whisper-tiny (smallest, fastest model)")
    from .service_dependencies import get_transcription_service

    get_transcription_service()
    logger.info("[STARTUP] Transcription service ready")

    # Initialize translation service
    logger.info("[STARTUP] Step 3/4: Initializing translation service...")
    logger.info("[STARTUP] Using model: opus-de-es (fast model)")
    from .service_dependencies import get_translation_service

    get_translation_service()
    logger.info("[STARTUP] Translation service ready")

    # Initialize task progress registry
    logger.info("[STARTUP] Step 4/4: Initializing task registry...")
    get_task_progress_registry()

    logger.info("[STARTUP] All services initialized successfully!")
    logger.info("[STARTUP] Server is ready to handle requests")


async def cleanup_services():
    """Cleanup services on shutdown"""
    logger.info("Cleaning up services...")

    # Close database engine
    from .database import engine

    await engine.dispose()

    # Clear task progress registry content (not cache, as we removed @lru_cache)
    _task_progress_registry.clear()

    logger.info("Service cleanup complete")


__all__ = ["cleanup_services", "get_task_progress_registry", "init_services"]

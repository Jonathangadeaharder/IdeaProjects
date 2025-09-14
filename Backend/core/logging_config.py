"""
Logging configuration for LangPlug Backend
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from .config import settings


class SafeConsoleHandler(logging.StreamHandler):
    """A console handler that safely writes messages even if the console encoding
    can't represent certain characters (e.g., emojis on Windows cp1252).
    """
    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            stream = self.stream
            enc = getattr(stream, "encoding", None) or sys.getdefaultencoding() or "utf-8"
            try:
                stream.write(msg + self.terminator)
            except UnicodeEncodeError:
                safe_msg = msg.encode(enc, errors="replace").decode(enc, errors="replace")
                stream.write(safe_msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


def setup_logging():
    """Setup file logging configuration"""
    
    # Create logs directory
    logs_path = settings.get_logs_path()
    logs_path.mkdir(exist_ok=True)
    
    # Create log filename with date
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = logs_path / f"langplug-backend-{today}.log"
    
    # Ensure log file is writable
    try:
        log_file.touch(exist_ok=True)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n=== Backend logging started at {datetime.now().isoformat()} ===\n")
    except Exception as e:
        print(f"WARNING: Cannot write to log file {log_file}: {e}")
        # Fall back to logs in current directory
        log_file = Path(f"langplug-backend-{today}.log")
        print(f"Using fallback log file: {log_file.absolute()}")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    if settings.log_format == "json":
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": "%(lineno)d"}',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Console handler (still useful for development), safe for non-ASCII
    console_handler = SafeConsoleHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("🚀 BACKEND STARTUP - Logging initialized")
    logger.info(f"📁 Log file: {log_file.absolute()}")
    logger.info(f"📊 Log level: {settings.log_level}")
    logger.info(f"📄 Log format: {settings.log_format}")
    logger.info(f"🔧 Videos path: {settings.get_videos_path()}")
    logger.info(f"💾 Data path: {settings.get_data_path()}")
    
    # Test log write
    logger.debug("Debug logging test")
    logger.info("Info logging test")
    logger.warning("Warning logging test")
    
    return log_file


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)

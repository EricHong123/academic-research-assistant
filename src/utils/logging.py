"""Logging configuration for Academic Research Assistant."""
import logging
import sys
import json
from datetime import datetime
from typing import Any
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data)


class RequestLogger:
    """Request logger with correlation IDs."""

    def __init__(self):
        self.logger = logging.getLogger("ara.requests")

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: str | None = None,
        extra: dict[str, Any] | None = None,
    ):
        """Log HTTP request."""
        self.logger.info(
            f"{method} {path} {status_code} {duration_ms:.2f}ms",
            extra={
                "request": {
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "user_id": user_id,
                },
                **(extra or {}),
            },
        )


def setup_logging(level: str = "INFO", log_file: str | None = None):
    """Setup logging configuration."""
    # Create logger
    logger = logging.getLogger("ara")
    logger.setLevel(getattr(logging, level.upper()))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Use JSON formatter for production
    formatter = JSONFormatter()
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Default logger instance
logger = logging.getLogger("ara")

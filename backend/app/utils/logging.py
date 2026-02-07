"""
Structured logging with request correlation.

Usage:
    from app.utils.logging import get_logger, request_id_var

    logger = get_logger(__name__)
    logger.info("event_name", extra_key="value")
"""

import logging
import json
import uuid
from contextvars import ContextVar
from typing import Any
from datetime import datetime

# Request context for correlation
request_id_var: ContextVar[str] = ContextVar('request_id', default='')


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        if hasattr(record, 'extra'):
            log_entry.update(record.extra)
        return json.dumps(log_entry)


def get_logger(name: str) -> logging.Logger:
    """Get a structured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


def set_request_id(request_id: str | None = None) -> str:
    """Set the request ID for correlation.

    Args:
        request_id: Request ID to set, or generate UUID if None

    Returns:
        The request ID that was set
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id


def get_request_id() -> str:
    """Get the current request ID."""
    return request_id_var.get()

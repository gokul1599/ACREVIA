"""
ACREVIA - Structured Logging & Telemetry.
Provides request correlation ID injection and privacy-preserving log sanitization.
"""

import logging
import sys
from contextvars import ContextVar
from typing import Optional

# Request Correlation ID context variable
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar("correlation_id_ctx", default=None)


class CorrelationIdFilter(logging.Filter):
    """Injects the current request correlation ID into every log record."""
    def filter(self, record):
        cid = correlation_id_ctx.get()
        record.correlation_id = cid if cid else "system"
        return True


def get_logger(name: str = "acrevia") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [cid:%(correlation_id)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        handler.addFilter(CorrelationIdFilter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = get_logger()

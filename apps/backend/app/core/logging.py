import logging
import sys
from typing import cast

import structlog
from structlog.typing import Processor


def configure_logging(*, log_level: str, json_logs: bool) -> None:
    """Configure structured logging for the application.

    Local development uses a human-readable console renderer by default.
    Production can enable JSON logs with LOG_JSON=true.
    """
    level = _to_logging_level(log_level)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
        force=True,
    )

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer: Processor = (
        cast(Processor, structlog.processors.JSONRenderer())
        if json_logs
        else cast(Processor, structlog.dev.ConsoleRenderer())
    )

    structlog.configure(
        processors=[*shared_processors, renderer],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )


def _to_logging_level(log_level: str) -> int:
    """Convert a string log level into a stdlib logging level."""
    normalized_level = log_level.upper().strip()

    return logging.getLevelNamesMapping().get(normalized_level, logging.INFO)
"""Logging configuration for the AI Video Search Engine.

This module configures loguru to provide structured, production-grade logging,
including console outputs and rotating file logs for different concern areas
(app.log, metadata.log, errors.log). It also intercepts standard library
logs from libraries like uvicorn.
"""

import sys
import logging
from pathlib import Path
from typing import Union
from loguru import logger
from app.core.config import settings


class InterceptHandler(logging.Handler):
    """Custom standard library logging handler that redirects all records to Loguru.

    This ensures third-party logs (e.g., uvicorn, fastapi) are formatted and
    processed using loguru's unified formatting pipeline.
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level: Union[str, int] = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message to preserve correct code location
        frame = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def metadata_log_filter(record) -> bool:
    """Filter that routes logs with `context="metadata"` to metadata.log.

    Usage: logger.bind(context="metadata").info("Some metadata operation")
    """
    return record["extra"].get("context") == "metadata"


def setup_logging() -> None:
    """Initialize and configure the loguru logging framework.

    Configures:
    1. Console logging (formatted text or JSON).
    2. File logging:
       - app.log (general application logs, global LOG_LEVEL and above)
       - errors.log (system errors and warnings, WARNING and above)
       - metadata.log (specific domain logs for metadata processing)
    3. Standard library logging interception (intercepts uvicorn and other framework logs).
    """
    # Create logs directory if it doesn't exist
    logs_path = Path(settings.LOGS_DIR)
    logs_path.mkdir(parents=True, exist_ok=True)

    # Remove all default handlers (specifically the default console handler)
    logger.remove()

    def safe_add(*args, **kwargs):
        try:
            return logger.add(*args, **kwargs)
        except Exception:
            # Fallback for restricted/sandboxed environments where multiprocessing queues (CreateNamedPipe) fail
            if kwargs.get("enqueue"):
                kwargs["enqueue"] = False
                return logger.add(*args, **kwargs)
            raise

    # Define standard format configurations
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    json_format = "{message}"  # If serialized, loguru manages the structure

    # 1. Configure Console Handler
    if settings.LOG_FORMAT == "json":
        safe_add(
            sys.stdout,
            level=settings.LOG_LEVEL,
            format=json_format,
            serialize=True,
            enqueue=True,
        )
    else:
        safe_add(
            sys.stdout,
            level=settings.LOG_LEVEL,
            format=log_format,
            colorize=True,
            enqueue=True,
        )

    # Rotation configurations
    rotation_limit = "10 MB"
    retention_count = 10

    # 2. Configure file handler for app.log (Global logs)
    safe_add(
        logs_path / "app.log",
        level=settings.LOG_LEVEL,
        format=json_format if settings.LOG_FORMAT == "json" else log_format,
        serialize=(settings.LOG_FORMAT == "json"),
        rotation=rotation_limit,
        retention=retention_count,
        enqueue=True,
    )

    # 3. Configure file handler for errors.log (WARNING and ERROR logs)
    safe_add(
        logs_path / "errors.log",
        level="WARNING",
        format=json_format if settings.LOG_FORMAT == "json" else log_format,
        serialize=(settings.LOG_FORMAT == "json"),
        rotation=rotation_limit,
        retention=retention_count,
        enqueue=True,
    )

    # 4. Configure file handler for metadata.log (Specialized metadata operation logs)
    safe_add(
        logs_path / "metadata.log",
        level=settings.LOG_LEVEL,
        filter=metadata_log_filter,
        format=json_format if settings.LOG_FORMAT == "json" else log_format,
        serialize=(settings.LOG_FORMAT == "json"),
        rotation=rotation_limit,
        retention=retention_count,
        enqueue=True,
    )

    # 5. Intercept standard library logging
    # List of frameworks we want to route through our production logger
    intercept_loggers = (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for logger_name in intercept_loggers:
        mod_logger = logging.getLogger(logger_name)
        mod_logger.handlers = [InterceptHandler()]
        mod_logger.propagate = False
        # Set level based on settings configuration, but disable uvicorn access logs 
        # below WARNING because request_logging_middleware handles request logging.
        if logger_name == "uvicorn.access":
            mod_logger.setLevel(logging.WARNING)
        else:
            mod_logger.setLevel(logging.getLevelName(settings.LOG_LEVEL))

    logger.info("Production-grade logging layer successfully initialized")

"""Structured logging configuration for Luminote."""

import logging
import sys

from app.config import get_settings

# Module-level logger for app
logger = logging.getLogger("app")


def setup_logging() -> None:
    """Configure structured logging.

    Sets up logging with appropriate level and format.
    """
    settings = get_settings()

    # Configure logging format
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Set up logger for the app
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"app.{name}")

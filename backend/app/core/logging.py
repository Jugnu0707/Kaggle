"""Standard Python logging configuration for the Oz AI backend."""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger with console output at INFO level."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger


def setup_logging() -> None:
    """Configure the root logger for application-wide console output."""
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

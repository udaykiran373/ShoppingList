"""
Structured logging utility for the Shopping List API.
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Create and return a structured logger.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger

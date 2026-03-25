import logging

from flask import Flask


def configure_logging(app: Flask) -> None:
    """Configure structured Python logging for NutriTrack.

    Sets up a 'nutritrack' logger with INFO level and a StreamHandler.
    Skips adding a handler if one already exists to prevent duplicates
    during testing.
    """
    logger = logging.getLogger("nutritrack")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.info("NutriTrack application started")

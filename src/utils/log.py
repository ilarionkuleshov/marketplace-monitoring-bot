"""Logging utilities."""

import logging

from settings import general_settings


def configure_logging() -> None:
    """Configures root logger."""
    console_handler = logging.StreamHandler()
    console_handler.setLevel(general_settings().LOG_LEVEL)

    formatter = logging.Formatter("%(asctime)s <%(name)s> %(levelname)s: %(message)s")
    console_handler.setFormatter(formatter)

    logging.root.addHandler(console_handler)
    logging.root.setLevel(console_handler.level)

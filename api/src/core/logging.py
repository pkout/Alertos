"""
Utilities for logging.
"""

import logging

from core import config

def get_logger(mod_name):
    """Returns a standardized logger.

    Example: get_logger(__name__)
    """
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(config.Logging.Format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, config.Logging.Level))

    return logger

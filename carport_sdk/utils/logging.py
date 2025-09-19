"""
Logging utilities for CarPort SDK.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "carport_sdk", level: int = logging.INFO) -> logging.Logger:
    """
    Setup a logger with standard configuration.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    logger.setLevel(level)
    return logger


def get_logger(name: str = "carport_sdk") -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
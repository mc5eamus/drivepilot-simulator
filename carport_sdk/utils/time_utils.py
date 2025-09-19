"""
Time utilities for CarPort SDK.
"""

import time
from datetime import datetime, timedelta
from typing import Optional


def get_timestamp() -> datetime:
    """Get current timestamp."""
    return datetime.now()


def format_duration(seconds: float) -> str:
    """
    Format duration in a human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def time_since(timestamp: datetime) -> float:
    """
    Calculate time elapsed since a timestamp.

    Args:
        timestamp: Starting timestamp

    Returns:
        Elapsed time in seconds
    """
    return (datetime.now() - timestamp).total_seconds()


def sleep_ms(milliseconds: int):
    """
    Sleep for specified milliseconds.

    Args:
        milliseconds: Sleep duration in milliseconds
    """
    time.sleep(milliseconds / 1000.0)

"""
Time helper utilities for timestamp conversions and formatting.
"""

from datetime import datetime
from typing import Union

def to_iso8601(ts: Union[int, float]) -> str:
    """
    Converts a Unix timestamp to ISO 8601 string.
    """
    return datetime.utcfromtimestamp(ts).isoformat() + 'Z' 
"""
completeness.py — Verify pagination logic completeness.
"""

import logging

logger = logging.getLogger(__name__)

def verify_pagination_completeness(expected_count: int, actual_count: int) -> bool:
    """
    Check if the number of parsed items matches expected (if known).
    """
    if expected_count > 0 and actual_count < expected_count:
        logger.warning(f"Thiếu dữ liệu: Dự kiến {expected_count}, thực tế {actual_count}")
        return False
    return True

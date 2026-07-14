"""
page_validator.py — Validate page structures to detect parser breakages.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def validate_page_data(data: list, has_schema_error: bool) -> bool:
    """
    Check if the page parsing was successful.
    """
    if has_schema_error:
        logger.error("Page schema validation failed: table detector reported error.")
        return False
        
    if not data:
        # It's possible for a page to be empty ("Đang cập nhật")
        # In a real scenario, we might want to distinguish between "empty" and "broken"
        logger.warning("Page contains no valid data rows.")
        return True
        
    return True

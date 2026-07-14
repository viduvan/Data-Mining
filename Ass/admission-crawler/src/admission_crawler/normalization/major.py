"""
major.py — Major code and name extraction.
"""

from typing import Tuple, Optional
import re
from admission_crawler.normalization.text import normalize_text, clean_dashes

def extract_major_info(major_raw: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract major code and name.
    Often format is "7480201 - Công nghệ thông tin"
    Returns: (code, name)
    """
    if not major_raw:
        return None, None
        
    cleaned = clean_dashes(major_raw).strip()
    
    # Try to find standard format: CODE - NAME
    # Assume code is 6-10 characters, usually digits or letters
    match = re.match(r"^([a-zA-Z0-9_]{4,15})\s*-\s*(.+)$", cleaned)
    
    if match:
        code = match.group(1).strip().upper()
        name = match.group(2).strip()
        return code, name
        
    # If no dash, it's just the name
    return None, cleaned

"""
university.py — University normalization.
"""

from typing import Tuple, Optional
import re
from admission_crawler.normalization.text import clean_dashes

def extract_university_info(university_raw: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract university code and name if present in raw string.
    Often format: "QHI - Đại học Công nghệ - ĐHQGHN" or just "Đại học Bách Khoa Hà Nội"
    Returns: (code, name)
    """
    if not university_raw:
        return None, None
        
    cleaned = clean_dashes(university_raw).strip()
    
    # Try to find standard format: CODE - NAME
    # Assume code is 2-6 characters
    match = re.match(r"^([a-zA-Z0-9]{2,6})\s*-\s*(.+)$", cleaned)
    
    if match:
        code = match.group(1).strip().upper()
        name = match.group(2).strip()
        return code, name
        
    # Just name
    return None, cleaned

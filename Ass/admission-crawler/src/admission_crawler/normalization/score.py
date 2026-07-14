"""
score.py — Score normalization and scale detection.
"""

from decimal import Decimal, InvalidOperation
from typing import Tuple, Optional
import re

def parse_score(score_raw: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Attempt to parse a score string into a Decimal string and determine its scale.
    Returns: (score_decimal_str, score_scale)
    """
    if not score_raw:
        return None, "unknown"
        
    score_clean = score_raw.strip().lower()
    
    # Handle text values
    if score_clean in ["-", "không tuyển", "đang cập nhật", "xét học bạ", "thực hành"]:
        return None, "unknown"
        
    # Try parsing
    try:
        # Some scores might use comma instead of dot
        normalized_str = score_clean.replace(",", ".")
        # Remove non-numeric characters except dot
        normalized_str = re.sub(r"[^\d.]", "", normalized_str)
        
        if not normalized_str:
            return None, "unknown"
            
        score_val = Decimal(normalized_str)
        
        # Determine scale
        scale = "unknown"
        if 0 < score_val <= 30:
            scale = "30"
        elif 30 < score_val <= 40:
            scale = "40"
        elif 40 < score_val <= 100:
            scale = "100"
        elif 100 < score_val <= 150:
            scale = "150"
        elif 150 < score_val <= 1200:
            scale = "1200"
        elif 1200 < score_val <= 1500:
            scale = "1500"
            
        return str(score_val), scale
        
    except InvalidOperation:
        return None, "unknown"

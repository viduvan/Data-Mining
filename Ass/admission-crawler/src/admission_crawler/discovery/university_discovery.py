"""
university_discovery.py — Filter and process discovered universities.
"""

from typing import List, Dict, Any
from admission_crawler.config import settings

def filter_by_province(universities: List[Dict[str, Any]], target_province: str = settings.app.province_filter) -> List[Dict[str, Any]]:
    """
    Keep only universities where the province exactly matches target_province
    (after normalization).
    """
    filtered = []
    target_lower = target_province.lower()
    
    for uni in universities:
        province_raw = uni.get("province_raw")
        if province_raw and province_raw.lower() == target_lower:
            filtered.append(uni)
            
    return filtered

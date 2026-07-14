"""
subject_combination.py — Extract subject combos using regex.
"""

import re
from typing import List
from admission_crawler.constants import SUBJECT_COMBO_PATTERN

def extract_subject_combinations(text: str) -> List[str]:
    """
    Find all subject combinations (e.g. A00, D01) in the text.
    Returns a sorted list of unique combinations.
    """
    if not text:
        return []
        
    # Match the pattern \b[A-Z]\d{2}\b
    # Uppercase the text first just in case
    matches = re.findall(SUBJECT_COMBO_PATTERN, text.upper())
    
    # Deduplicate and sort
    return sorted(list(set(matches)))

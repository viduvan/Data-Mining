"""
admission_method.py — Rule-based classification of admission methods.
"""

from typing import Tuple
from admission_crawler.constants import METHOD_KEYWORDS
from admission_crawler.normalization.text import normalize_text

def classify_admission_method(major_raw: str, subject_raw: str, note_raw: str) -> Tuple[str, float, str]:
    """
    Classify the admission method based on keywords.
    Returns: (method, confidence, matched_rule)
    """
    combined_text = f"{normalize_text(major_raw)} | {normalize_text(subject_raw)} | {normalize_text(note_raw)}"
    
    if "đgnl đhqghn" in combined_text:
        return "dgnl_dhqg", 1.0, "đgnl đhqghn"

    # Simple rule-based matching
    best_match = "unknown"
    best_confidence = 0.0
    matched_rule = ""
    
    for method, keywords in METHOD_KEYWORDS.items():
        for keyword in keywords:
            if keyword in combined_text:
                # Direct match
                best_match = method
                best_confidence = 1.0
                matched_rule = keyword
                break
        if best_confidence == 1.0:
            break
            
    # If no explicit rule matched, but subject combination looks like THPT exam
    # and no contradictory notes, we could apply a heuristic, 
    # but the instructions say "không mặc định mọi row là thpt_exam".
    # So we leave it as unknown if no keyword matches.
            
    return best_match, best_confidence, matched_rule

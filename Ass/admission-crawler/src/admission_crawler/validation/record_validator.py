"""
record_validator.py — Validate individual parsed records.
"""

from typing import Dict, Any, List

def is_valid_cutoff_record(record: Dict[str, Any]) -> bool:
    """Check if a raw cutoff record has minimum required fields."""
    # Must have major name
    if not record.get("major_name_raw"):
        return False
        
    # Valid records must have some score or combination info
    # Even if score is None, if there's an admission method hint, it's valid
    # But if everything except name is None/empty, it's suspect
    if not any([
        record.get("cutoff_score_raw"), 
        record.get("subject_combination_raw"),
        record.get("note_raw")
    ]):
        return False
        
    return True

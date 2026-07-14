"""
text.py — Text normalization utilities.
"""

import unicodedata
import re

def normalize_text(text: str) -> str:
    """
    Standardize text for comparison and storage.
    - NFC normalization
    - Trim whitespace
    - Lowercase
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()

def clean_dashes(text: str) -> str:
    """Normalize em-dash, en-dash to standard hyphen."""
    if not text:
        return ""
    text = text.replace("–", "-").replace("—", "-")
    return text

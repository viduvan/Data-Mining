"""
common.py — Common parsing utilities.
"""

import html
import unicodedata
import re
from typing import Optional
from bs4 import BeautifulSoup, Tag

def clean_text(value: Optional[str]) -> Optional[str]:
    """
    Clean HTML text:
    - unescape HTML entities
    - normalize Unicode to NFC
    - replace non-breaking spaces
    - collapse multiple whitespaces
    """
    if not value:
        return None
        
    value = html.unescape(value)
    value = unicodedata.normalize("NFC", value)
    value = value.replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value)
    value = value.strip()
    
    return value if value else None

def extract_text_without_xem(cell: Tag) -> str:
    """
    Extract text from a table cell, removing any <a> tags containing "Xem".
    This prevents "(Xem)" from becoming part of the major name.
    """
    # Create a copy so we don't modify the original soup
    import copy
    cell_copy = copy.copy(cell)
    
    # Find and remove "Xem" links
    for a_tag in cell_copy.find_all('a'):
        text = a_tag.get_text(strip=True).lower()
        if text == "xem" or text == "(xem)":
            a_tag.decompose()
            
    # Now get the cleaned text
    return clean_text(cell_copy.get_text(separator=' '))

def find_link_in_cell(cell: Tag) -> Optional[str]:
    """Find the first href in a cell."""
    a_tag = cell.find('a', href=True)
    if a_tag:
        return a_tag['href']
    return None

"""
year_index.py — Handles crawling the index of universities for a specific year.
"""

import logging
from typing import List, Dict, Any
from admission_crawler.config import settings
from admission_crawler.discovery.pagination import canonicalize_url, extract_pagination_links

logger = logging.getLogger(__name__)

def get_base_index_url(year: int) -> str:
    """Get the base index URL for a given year."""
    path = settings.targets.index_path_template.format(year=year)
    return canonicalize_url(path)

# Actual crawling logic will be orchestrated by pipelines, 
# this module provides helper structures.

"""
table_detector.py — Heuristic table detector.
"""

from typing import Dict, Set, Tuple, Optional
from bs4 import BeautifulSoup, Tag
from admission_crawler.parsers.common import clean_text


def normalize_header(text: str) -> str:
    return text.lower().strip() if text else ""


def score_table(table: Tag, expected_aliases: Dict[str, Set[str]]) -> Tuple[float, Dict[str, int]]:
    """Score a table and map expected column names to header indexes."""
    header_row = table.find("tr")
    headers = header_row.find_all(["th", "td"]) if header_row else table.find_all("th")
    if not headers:
        return 0.0, {}

    header_texts = [normalize_header(clean_text(header.get_text())) for header in headers]
    matched_cols = {}
    for key, aliases in expected_aliases.items():
        for index, header in enumerate(header_texts):
            if header in aliases:
                matched_cols[key] = index
                break

    for key, aliases in expected_aliases.items():
        if key in matched_cols:
            continue
        candidates = [
            (len(alias), index)
            for index, header in enumerate(header_texts)
            for alias in aliases
            if alias in header
        ]
        if candidates:
            matched_cols[key] = max(candidates)[1]

    score = len(matched_cols) / len(expected_aliases) if expected_aliases else 0.0
    return score, matched_cols


def find_best_table(soup: BeautifulSoup, expected_aliases: Dict[str, Set[str]], min_score: float = 0.5) -> Tuple[Optional[Tag], Dict[str, int]]:
    """Find the table that best matches the expected headers."""
    best_table = None
    best_score = -1.0
    best_mapping = {}
    for table in soup.find_all("table"):
        score, mapping = score_table(table, expected_aliases)
        if score > best_score:
            best_table, best_score, best_mapping = table, score, mapping
    return (best_table, best_mapping) if best_score >= min_score else (None, {})

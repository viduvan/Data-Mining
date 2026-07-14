"""
university_parser.py — Parse the university detail page (list of majors).
"""

import logging
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup

from admission_crawler.parsers.common import clean_text, extract_text_without_xem, find_link_in_cell
from admission_crawler.parsers.table_detector import find_best_table
from admission_crawler.constants import DETAIL_TABLE_HEADERS

logger = logging.getLogger(__name__)

def parse_university_page(html: str) -> Tuple[List[Dict[str, Any]], bool, Dict[str, Any]]:
    """
    Parse the detail page to extract majors and cutoffs.
    Returns: (list_of_cutoffs, has_schema_error, metadata)
    """
    soup = BeautifulSoup(html, 'lxml')
    
    # Try to extract metadata from the top (usually above the table)
    metadata = {}
    
    # Use table detector
    table, col_map = find_best_table(soup, DETAIL_TABLE_HEADERS, min_score=0.66) # require at least 4/6 columns
    
    if not table:
        # Sometimes there's no data yet "Đang cập nhật"
        if "đang cập nhật" in clean_text(soup.get_text()).lower():
            logger.info("Trang chưa có dữ liệu điểm chuẩn (đang cập nhật).")
            return [], False, metadata
            
        logger.error("Không tìm thấy bảng điểm chuẩn hợp lệ trên trang chi tiết.")
        return [], True, metadata
        
    required_cols = {"major"}
    if not required_cols.issubset(col_map.keys()):
        logger.error(f"Bảng thiếu cột bắt buộc. Các cột tìm thấy: {col_map.keys()}")
        return [], True, metadata

    cutoffs = []
    
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) <= max(col_map.values()) if col_map.values() else 0:
            continue
            
        m_cell = cells[col_map["major"]]
        if m_cell.name == 'th' and "ngành" in clean_text(m_cell.get_text()).lower():
            continue
            
        stt_raw = clean_text(cells[col_map["stt"]].get_text()) if "stt" in col_map else None
        stt = int(stt_raw) if stt_raw and stt_raw.isdigit() else None
        
        # Remove "Xem" link from major name text
        major_raw = extract_text_without_xem(m_cell)
        major_url = find_link_in_cell(m_cell)
        
        score_raw = clean_text(cells[col_map["score"]].get_text()) if "score" in col_map else None
        level_raw = clean_text(cells[col_map["level"]].get_text()) if "level" in col_map else None
        subject_raw = clean_text(cells[col_map["subject_group"]].get_text()) if "subject_group" in col_map else None
        note_raw = clean_text(cells[col_map["note"]].get_text()) if "note" in col_map else None
        
        if not major_raw:
            continue
            
        cutoffs.append({
            "source_row_stt": stt,
            "major_name_raw": major_raw,
            "cutoff_score_raw": score_raw,
            "education_level_raw": level_raw,
            "subject_combination_raw": subject_raw,
            "note_raw": note_raw,
            "major_detail_url": major_url,
            # We don't hash here, hash later in pipeline
        })
        
    return cutoffs, False, metadata

"""
index_parser.py — Parse the year index page (list of universities).
"""

import logging
from typing import List, Dict, Any, Tuple
from bs4 import BeautifulSoup

from admission_crawler.parsers.common import clean_text, find_link_in_cell
from admission_crawler.parsers.table_detector import find_best_table
from admission_crawler.constants import INDEX_TABLE_HEADERS

logger = logging.getLogger(__name__)

def parse_index_page(html: str) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Parse the index page to extract a list of universities.
    Returns: (list_of_universities, has_schema_error)
    """
    soup = BeautifulSoup(html, 'lxml')
    
    # Use table detector
    table, col_map = find_best_table(soup, INDEX_TABLE_HEADERS, min_score=0.75) # require at least 3/4 columns
    
    if not table:
        logger.error("Không tìm thấy bảng danh sách trường hợp lệ trên trang index.")
        return [], True
        
    required_cols = {"university"}
    if not required_cols.issubset(col_map.keys()):
        logger.error(f"Bảng thiếu cột bắt buộc. Các cột tìm thấy: {col_map.keys()}")
        return [], True

    universities = []
    
    # Process rows
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all(['td', 'th'])
        # Skip rows that don't match our column count (likely nested tables or weird headers)
        if len(cells) <= max(col_map.values()) if col_map.values() else 0:
            continue
            
        # If the university cell is a 'th' and it's a header row, skip
        u_cell = cells[col_map["university"]]
        if u_cell.name == 'th' and "trường" in clean_text(u_cell.get_text()).lower():
            continue
            
        stt_raw = clean_text(cells[col_map["stt"]].get_text()) if "stt" in col_map else None
        stt = int(stt_raw) if stt_raw and stt_raw.isdigit() else None
        
        name_raw = clean_text(u_cell.get_text())
        detail_url = find_link_in_cell(u_cell)
        
        code_raw = clean_text(cells[col_map["university_code"]].get_text()) if "university_code" in col_map else None
        province_raw = clean_text(cells[col_map["province"]].get_text()) if "province" in col_map else None
        
        if not name_raw:
            continue
            
        universities.append({
            "source_stt": stt,
            "university_name_raw": name_raw,
            "university_code_raw": code_raw,
            "province_raw": province_raw,
            "detail_url": detail_url
        })
        
    return universities, False

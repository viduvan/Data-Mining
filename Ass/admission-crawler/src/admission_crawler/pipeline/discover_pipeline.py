"""
discover_pipeline.py — Orchestrates the discovery of universities from index pages.
"""

import logging
from typing import List, Dict, Any
import hashlib

from admission_crawler.http.client import CrawlerClient
from admission_crawler.storage.repositories import CrawlRepository
from admission_crawler.storage.raw_html_store import save_raw_html
from admission_crawler.discovery.year_index import get_base_index_url
from admission_crawler.discovery.pagination import extract_pagination_links
from admission_crawler.discovery.university_discovery import filter_by_province
from admission_crawler.parsers.index_parser import parse_index_page

logger = logging.getLogger(__name__)

def run_discovery(year: int, client: CrawlerClient, repo: CrawlRepository, run_id: int) -> List[Dict[str, Any]]:
    """
    Discover all universities in Hanoi for the given year.
    Handles pagination.
    """
    base_url = get_base_index_url(year)
    urls_to_visit = [base_url]
    visited_urls = set()
    
    all_hanoi_unis = []
    
    while urls_to_visit:
        current_url = urls_to_visit.pop(0)
        if current_url in visited_urls:
            continue
            
        logger.info(f"Khám phá trang danh sách: {current_url}")
        status, html, err = client.fetch(current_url, year)
        visited_urls.add(current_url)
        
        if err or not html:
            logger.error(f"Bỏ qua trang do lỗi: {err}")
            continue
            
        content_hash = hashlib.sha256(html.encode('utf-8')).hexdigest()
        save_raw_html(year, content_hash, html)
        
        page_record = repo.save_source_page(
            run_id=run_id,
            url=current_url,
            year=year,
            page_type="index",
            http_status=status,
            content_hash=content_hash
        )
        
        unis, schema_err = parse_index_page(html)
        if not schema_err:
            hanoi_unis = filter_by_province(unis)
            for u in hanoi_unis:
                u["year"] = year
                repo.save_university_raw(page_record.source_page_id, run_id, u)
            all_hanoi_unis.extend(hanoi_unis)
            
        # Extract pagination
        new_links = extract_pagination_links(html, current_url)
        for link in new_links:
            if link not in visited_urls and link not in urls_to_visit:
                urls_to_visit.append(link)
                
    logger.info(f"Tổng cộng tìm thấy {len(all_hanoi_unis)} trường ở Hà Nội năm {year}")
    return all_hanoi_unis

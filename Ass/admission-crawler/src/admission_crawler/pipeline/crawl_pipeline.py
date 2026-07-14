"""
crawl_pipeline.py — Orchestrates fetching detail pages for discovered universities.
"""

import logging
import hashlib

from admission_crawler.http.client import CrawlerClient
from admission_crawler.storage.repositories import CrawlRepository
from admission_crawler.storage.raw_html_store import save_raw_html
from admission_crawler.discovery.pagination import canonicalize_url, extract_pagination_links
from admission_crawler.parsers.university_parser import parse_university_page
from admission_crawler.validation.record_validator import is_valid_cutoff_record
from admission_crawler.config import settings

logger = logging.getLogger(__name__)


def run_university_crawl(
    uni_raw_db_id: str,
    start_url: str,
    year: int,
    client: CrawlerClient,
    repo: CrawlRepository,
    run_id: str,
) -> int:
    """Crawl all detail pages for one university."""
    canon_start = canonicalize_url(start_url)
    urls_to_visit = [canon_start]
    visited_urls = set()
    records_saved = 0
    university = repo.get_university_raw(uni_raw_db_id)
    if not university:
        raise ValueError(f"Unknown university_raw_id={uni_raw_db_id}")

    while urls_to_visit:
        current_url = urls_to_visit.pop(0)
        if current_url in visited_urls:
            continue

        logger.info("Crawl chi tiết: %s", current_url)
        status, html, err = client.fetch(current_url, year)
        visited_urls.add(current_url)
        if err or not html:
            logger.error("Lỗi khi crawl %s: %s", current_url, err)
            continue

        content_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()
        save_raw_html(year, content_hash, html)
        page_record = repo.save_source_page(
            run_id=run_id,
            url=current_url,
            year=year,
            page_type="detail",
            http_status=status,
            content_hash=content_hash,
        )

        cutoffs, schema_err, _ = parse_university_page(html)
        if not schema_err:
            for cutoff in cutoffs:
                if not is_valid_cutoff_record(cutoff):
                    continue
                fingerprint_source = "|".join(
                    str(value or "") for value in (
                        year,
                        university.university_code_raw,
                        cutoff.get("major_name_raw"),
                        cutoff.get("subject_combination_raw"),
                        cutoff.get("cutoff_score_raw"),
                    )
                )
                cutoff.update({
                    "record_fingerprint": hashlib.md5(
                        fingerprint_source.encode("utf-8")
                    ).hexdigest(),
                    "year": year,
                    "university_name_raw": university.university_name_raw,
                    "university_code_raw": university.university_code_raw,
                    "province_raw": university.province_raw,
                    "source_url": current_url,
                    "content_sha256": content_hash,
                    "parser_version": settings.app.parser_version,
                })
                if repo.save_cutoff_raw(
                    uni_raw_db_id, page_record.source_page_id, run_id, cutoff
                ):
                    records_saved += 1

        for link in extract_pagination_links(html, current_url):
            if link not in visited_urls and link not in urls_to_visit:
                urls_to_visit.append(link)

    return records_saved

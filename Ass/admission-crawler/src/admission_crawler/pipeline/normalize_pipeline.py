"""
normalize_pipeline.py — Transforms raw records into normalized facts.
"""

import logging
from sqlalchemy.orm import Session
from admission_crawler.storage.models import CrawlRun, UniversityRaw, CutoffRaw
from admission_crawler.storage.repositories import CrawlRepository
from admission_crawler.normalization.text import normalize_text
from admission_crawler.normalization.score import parse_score
from admission_crawler.normalization.major import extract_major_info
from admission_crawler.normalization.university import extract_university_info
from admission_crawler.normalization.subject_combination import extract_subject_combinations
from admission_crawler.normalization.admission_method import classify_admission_method

logger = logging.getLogger(__name__)

def run_normalization(db_session: Session, repo: CrawlRepository, run_id: int):
    """
    Query raw cutoffs from the database (for this run) and normalize them.
    """
    run = db_session.get(CrawlRun, run_id)
    if not run or not run.years:
        raise ValueError(f"Không tìm thấy năm crawl cho run_id={run_id}")

    raw_records = db_session.query(CutoffRaw, UniversityRaw).join(
        UniversityRaw, CutoffRaw.university_raw_id == UniversityRaw.university_raw_id
    ).filter(CutoffRaw.year.in_(run.years)).all()
    
    logger.info(f"Đang chuẩn hóa {len(raw_records)} bản ghi raw.")
    
    success_count = 0
    
    for raw_cutoff, raw_uni in raw_records:
        uni_name_raw = raw_uni.university_name_raw.replace(" (Xem)", "").strip()
        major_name_raw = raw_cutoff.major_name_raw.replace(" (Xem)", "").strip()
        
        uni_code, uni_name = extract_university_info(uni_name_raw)
        major_code, major_name = extract_major_info(major_name_raw)
        
        score_val, score_scale = parse_score(raw_cutoff.cutoff_score_raw)
        
        method, conf, rule = classify_admission_method(
            major_name_raw, 
            raw_cutoff.subject_combination_raw, 
            raw_cutoff.note_raw
        )
        
        # We might have multiple subject combinations. 
        # Usually, one row applies to all mentioned combos. We could split, 
        # but the schema implies storing them as JSON array or comma separated.
        combos = extract_subject_combinations(raw_cutoff.subject_combination_raw)
        
        normalized_data = {
            "year": raw_cutoff.year,
            "university_code": uni_code or raw_uni.university_code_raw,
            "university_name": (uni_name or "")[:255],
            "province": raw_uni.province_raw,
            "major_name": major_name_raw,
            "major_name_normalized": major_name,
            "admission_method": method,
            "subject_combinations": combos,
            "cutoff_score": str(score_val) if score_val is not None else None,
            "score_scale": score_scale,
            "education_level": normalize_text(raw_cutoff.education_level_raw),
            "source_url": raw_cutoff.source_url,
            "parser_version": raw_cutoff.parser_version,
        }
            
        norm_rec = repo.save_normalized_cutoff(raw_cutoff.cutoff_raw_id, normalized_data)
        if norm_rec:
            success_count += 1
            
    logger.info(f"Đã chuẩn hóa và lưu {success_count} bản ghi.")
    return success_count

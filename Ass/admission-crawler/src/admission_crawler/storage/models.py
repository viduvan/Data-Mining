"""
models.py — SQLAlchemy ORM models.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, ForeignKey, UniqueConstraint, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class CrawlRun(Base):
    __tablename__ = 'crawl_runs'
    
    crawl_run_id = Column(String, primary_key=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String)
    years = Column(JSON)
    province_filter = Column(String)
    config_json = Column(JSON)
    code_version = Column(String)
    host = Column(String)
    total_requested = Column(Integer, default=0)
    total_success = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    total_records = Column(Integer, default=0)
    stop_reason = Column(String, nullable=True)

class SourcePage(Base):
    __tablename__ = 'source_pages'
    
    source_page_id = Column(String, primary_key=True)
    crawl_run_id = Column(String, ForeignKey('crawl_runs.crawl_run_id'))
    canonical_url = Column(String, nullable=False)
    url_hash = Column(String, nullable=False, unique=True)
    page_type = Column(String)
    year = Column(Integer, nullable=True)
    university_code = Column(String, nullable=True)
    page_index = Column(Integer, default=0)
    status = Column(String)
    http_status = Column(Integer, nullable=True)
    requested_at = Column(DateTime, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    etag = Column(String, nullable=True)
    last_modified = Column(String, nullable=True)
    content_sha256 = Column(String, nullable=True)
    parser_version = Column(String, nullable=True)
    error_type = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    retry_count = Column(Integer, default=0)

class UniversityRaw(Base):
    __tablename__ = 'universities_raw'
    
    university_raw_id = Column(String, primary_key=True)
    crawl_run_id = Column(String)
    year = Column(Integer)
    source_stt = Column(Integer, nullable=True)
    university_name_raw = Column(String)
    university_code_raw = Column(String)
    province_raw = Column(String)
    detail_url = Column(String)
    source_page_id = Column(String)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('year', 'university_code_raw', 'detail_url', name='uix_univ_raw_year_code_url'),
    )

class CutoffRaw(Base):
    __tablename__ = 'cutoffs_raw'
    
    cutoff_raw_id = Column(String, primary_key=True)
    crawl_run_id = Column(String)
    source_page_id = Column(String)
    university_raw_id = Column(String, ForeignKey('universities_raw.university_raw_id'), nullable=True)
    year = Column(Integer)
    university_name_raw = Column(String)
    university_code_raw = Column(String)
    province_raw = Column(String)
    source_row_stt = Column(Integer, nullable=True)
    major_name_raw = Column(String)
    cutoff_score_raw = Column(String, nullable=True)
    education_level_raw = Column(String, nullable=True)
    subject_combination_raw = Column(String, nullable=True)
    note_raw = Column(String, nullable=True)
    major_detail_url = Column(String, nullable=True)
    source_url = Column(String)
    crawled_at = Column(DateTime, default=datetime.utcnow)
    content_sha256 = Column(String, nullable=True)
    parser_version = Column(String, nullable=True)
    record_fingerprint = Column(String)
    review_required = Column(Boolean, default=False)
    
    __table_args__ = (
        UniqueConstraint('year', 'university_code_raw', 'record_fingerprint', name='uix_cutoff_raw_year_code_fingerprint'),
    )

class CutoffNormalized(Base):
    __tablename__ = 'cutoffs_normalized'
    
    cutoff_id = Column(String, primary_key=True)
    cutoff_raw_id = Column(String, ForeignKey('cutoffs_raw.cutoff_raw_id'))
    year = Column(Integer)
    university_code = Column(String)
    university_name = Column(String)
    province = Column(String)
    major_name = Column(String)
    major_name_normalized = Column(String)
    cutoff_score = Column(String, nullable=True) # Decimal as String
    score_scale = Column(String, nullable=True)
    education_level = Column(String, nullable=True)
    admission_method = Column(String, nullable=True)
    subject_combinations = Column(JSON, nullable=True)
    program_type = Column(String, nullable=True)
    normalization_status = Column(String, nullable=True)
    normalization_confidence = Column(Float, nullable=True)
    review_required = Column(Boolean, default=False)
    source_url = Column(String, nullable=True)
    crawled_at = Column(DateTime, nullable=True)
    parser_version = Column(String, nullable=True)

class UrlCache(Base):
    __tablename__ = 'url_cache'
    
    url_hash = Column(String, primary_key=True)
    canonical_url = Column(String)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    etag = Column(String, nullable=True)
    last_modified = Column(String, nullable=True)
    http_status = Column(Integer, nullable=True)
    html_path = Column(String, nullable=True)

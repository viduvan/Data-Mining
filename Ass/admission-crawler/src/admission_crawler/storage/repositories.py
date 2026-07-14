"""
repositories.py — Data access layer for SQLAlchemy models.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging
from datetime import datetime

from admission_crawler.storage.models import (
    CrawlRun, SourcePage, UniversityRaw,
    CutoffRaw, CutoffNormalized
)

logger = logging.getLogger(__name__)


class CrawlRepository:
    def __init__(self, session: Session):
        self.session = session

    def start_run(self, parameters: Dict[str, Any]) -> CrawlRun:
        import uuid
        run = CrawlRun(
            crawl_run_id=str(uuid.uuid4()),
            years=parameters.get("years", []),
            config_json=parameters,
            status="running"
        )
        self.session.add(run)
        self.session.commit()
        return run

    def finish_run(self, run_id: str, status: str, errors_count: int = 0) -> None:
        run = self.session.get(CrawlRun, run_id)
        if run:
            run.status = status
            run.total_failed = (run.total_failed or 0) + errors_count
            run.finished_at = datetime.utcnow()
            self.session.commit()

    def get_university_raw(self, university_raw_id: str) -> Optional[UniversityRaw]:
        return self.session.get(UniversityRaw, university_raw_id)

    def save_source_page(self, run_id: str, url: str, year: int, page_type: str, http_status: int, content_hash: str) -> SourcePage:
        import uuid
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        existing = self.session.query(SourcePage).filter_by(url_hash=url_hash).first()
        if existing:
            return existing

        page = SourcePage(
            source_page_id=str(uuid.uuid4()),
            crawl_run_id=run_id,
            canonical_url=url,
            url_hash=url_hash,
            year=year,
            page_type=page_type,
            http_status=http_status,
            content_sha256=content_hash
        )
        self.session.add(page)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            return self.session.query(SourcePage).filter_by(url_hash=url_hash).one()
        return page

    def save_university_raw(self, page_id: str, run_id: str, data: Dict[str, Any]) -> UniversityRaw:
        import uuid
        uni = UniversityRaw(
            university_raw_id=str(uuid.uuid4()),
            source_page_id=page_id,
            crawl_run_id=run_id,
            **data
        )
        self.session.add(uni)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            return self.session.query(UniversityRaw).filter_by(
                year=data["year"],
                university_code_raw=data.get("university_code_raw"),
                detail_url=data.get("detail_url"),
            ).one()
        return uni

    def save_cutoff_raw(
        self, uni_id: str, page_id: str, run_id: str, data: Dict[str, Any]
    ) -> Optional[CutoffRaw]:
        import uuid
        try:
            cutoff = CutoffRaw(
                cutoff_raw_id=str(uuid.uuid4()),
                university_raw_id=uni_id,
                source_page_id=page_id,
                crawl_run_id=run_id,
                **data
            )
            self.session.add(cutoff)
            self.session.commit()
            return cutoff
        except IntegrityError:
            self.session.rollback()
            logger.debug("Skipping duplicate raw record: %s", data.get("record_fingerprint"))
            return None

    def save_normalized_cutoff(self, raw_id: str, data: Dict[str, Any]) -> Optional[CutoffNormalized]:
        if self.session.query(CutoffNormalized).filter_by(cutoff_raw_id=raw_id).first():
            return None

        import uuid
        try:
            norm = CutoffNormalized(
                cutoff_id=str(uuid.uuid4()),
                cutoff_raw_id=raw_id,
                **data
            )
            self.session.add(norm)
            self.session.commit()
            return norm
        except IntegrityError:
            self.session.rollback()
            logger.warning("Skipping duplicate normalized record for raw_id=%s", raw_id)
            return None

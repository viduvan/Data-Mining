"""
run_report.py — Generate run summary.
"""

from typing import Dict, Any
import logging

from admission_crawler.storage.repositories import CrawlRepository
from admission_crawler.storage.models import CrawlRun

logger = logging.getLogger(__name__)


def generate_run_summary(repo: CrawlRepository, run_id: str) -> Dict[str, Any]:
    run = repo.session.get(CrawlRun, run_id)
    if not run:
        return {}

    duration = (
        (run.finished_at - run.started_at).total_seconds()
        if run.finished_at and run.started_at
        else None
    )
    summary = {
        "run_id": run.crawl_run_id,
        "status": run.status,
        "start_time": run.started_at.isoformat() if run.started_at else None,
        "end_time": run.finished_at.isoformat() if run.finished_at else None,
        "duration_seconds": duration,
        "errors_count": run.total_failed or 0,
    }
    logger.info(
        "Crawl run %s completed: %s, duration=%ss, errors=%s",
        run_id,
        run.status,
        duration,
        run.total_failed or 0,
    )
    return summary

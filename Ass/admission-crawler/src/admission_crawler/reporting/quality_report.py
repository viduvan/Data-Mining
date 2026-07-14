"""
quality_report.py — Data quality metrics.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from admission_crawler.storage.models import CutoffNormalized


def check_quality(db_session: Session):
    """Basic completeness checks on normalized data."""
    total = db_session.query(func.count(CutoffNormalized.cutoff_id)).scalar()
    missing_scores = db_session.query(func.count(CutoffNormalized.cutoff_id)).filter(
        CutoffNormalized.cutoff_score.is_(None)
    ).scalar()
    percentage = missing_scores / total * 100 if total else 0
    print(f"Tổng số bản ghi chuẩn hóa: {total}")
    print(f"Số bản ghi thiếu điểm: {missing_scores} ({percentage:.1f}%)")

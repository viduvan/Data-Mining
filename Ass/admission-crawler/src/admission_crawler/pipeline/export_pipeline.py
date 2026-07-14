"""
export_pipeline.py — Export normalized data to CSV/JSON.
"""

import csv
import json
import logging
from sqlalchemy.orm import Session
from pathlib import Path
from admission_crawler.storage.models import CutoffNormalized
from admission_crawler.config import settings

logger = logging.getLogger(__name__)

def export_data(db_session: Session, format_type: str = "csv", output_dir: str = None):
    """Export normalized data joining with necessary dimension info."""
    if not output_dir:
        # Use data/export relative to working directory
        output_dir = Path("data") / "export"
        
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Query normalized records directly — all needed fields are already on CutoffNormalized
    records = db_session.query(CutoffNormalized).order_by(
        CutoffNormalized.year.desc(),
        CutoffNormalized.university_code,
        CutoffNormalized.major_name
    ).all()
     
    if not records:
        logger.warning("Không có dữ liệu chuẩn hóa để xuất.")
        return
        
    rows = []
    for norm in records:
        rows.append({
            "year": norm.year,
            "province": norm.province or "Hà Nội",
            "university_code": norm.university_code,
            "university_name": norm.university_name,
            "major_name": norm.major_name,
            "major_name_normalized": norm.major_name_normalized,
            "admission_method": norm.admission_method,
            "subject_combinations": ",".join(norm.subject_combinations) if norm.subject_combinations else "",
            "cutoff_score": norm.cutoff_score,
            "score_scale": norm.score_scale,
            "education_level": norm.education_level,
            "source_url": norm.source_url,
        })
        
    file_path = out_dir / f"vietnamnet_hanoi_cutoffs.{format_type}"
    
    if format_type == "csv":
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
    elif format_type == "json":
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
            
    logger.info(f"Đã xuất {len(rows)} bản ghi ra {file_path}")
    return str(file_path)

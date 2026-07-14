"""
anomaly_detector.py — Detect statistical anomalies in normalized data.
"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def detect_score_anomalies(records: List[Dict[str, Any]]) -> None:
    """
    Log warnings if scores are unusually high or low for their scale.
    """
    for r in records:
        score_val = r.get("score_value")
        scale = r.get("score_scale")
        
        if score_val is not None:
            try:
                val = float(score_val)
                if scale == "30" and val > 29.5:
                    logger.warning(f"Điểm chuẩn rất cao ({val}/30) ở ngành: {r.get('major_code')} - {r.get('university_code')}")
                elif scale == "30" and val < 13.0:
                    logger.warning(f"Điểm chuẩn rất thấp ({val}/30) ở ngành: {r.get('major_code')} - {r.get('university_code')}")
            except ValueError:
                pass

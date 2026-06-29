"""
src/recommendation/__init__.py
Recommendation System — Gợi ý trường/ngành theo điểm thi
"""

from .scorer import SafetyScorer
from .recommender import AdmissionRecommender

__all__ = ["SafetyScorer", "AdmissionRecommender"]

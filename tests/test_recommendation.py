"""
tests/test_recommendation.py
Unit tests cho Recommendation System
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.recommendation.scorer import SafetyScorer, PRIORITY_SCORE
from src.recommendation.recommender import AdmissionRecommender


# ================================================================
# Fixtures
# ================================================================

@pytest.fixture
def scorer():
    return SafetyScorer()


@pytest.fixture
def sample_admission_df():
    """Dữ liệu tuyển sinh mẫu cho Recommender."""
    return pd.DataFrame({
        "school_name": [
            "Đại học Bách khoa Hà Nội",
            "Đại học Kinh tế Quốc dân",
            "Đại học Ngoại thương",
            "Đại học FPT",
            "Đại học Bách khoa Hà Nội",
        ],
        "major_name": [
            "Công nghệ thông tin",
            "Kinh tế",
            "Kinh tế quốc tế",
            "Công nghệ thông tin",
            "Kỹ thuật điện",
        ],
        "major_group": [
            "Kỹ thuật - Công nghệ",
            "Kinh tế - Quản trị",
            "Kinh tế - Quản trị",
            "Kỹ thuật - Công nghệ",
            "Kỹ thuật - Công nghệ",
        ],
        "subject_group": ["A00", "A01", "D01", "A00", "A00"],
        "admission_score": [27.04, 26.5, 25.5, 22.0, 24.5],
        "quota": [200, 300, 150, 400, 180],
        "competition_level": ["Rất cao", "Rất cao", "Rất cao", "Trung bình", "Cao"],
        "score_trend": ["Tăng", "Ổn định", "Giảm", "Tăng", "Ổn định"],
        "delta_score": [0.3, 0.0, -0.5, 0.8, 0.1],
        "year": [2024, 2024, 2024, 2024, 2024],
        "region": ["Bắc", "Bắc", "Bắc", "Bắc", "Bắc"],
        "school_type": ["Công lập", "Công lập", "Công lập", "Tư thục", "Công lập"],
    })


@pytest.fixture
def recommender(sample_admission_df):
    return AdmissionRecommender(sample_admission_df)


# ================================================================
# Test SafetyScorer
# ================================================================

class TestSafetyScorer:

    def test_compute_total_score_kv3(self, scorer):
        """KV3 không được cộng điểm."""
        total = scorer.compute_total_score([8.0, 9.0, 8.5], priority_region="KV3")
        assert total == 25.5

    def test_compute_total_score_kv1(self, scorer):
        """KV1 được cộng 0.75 điểm."""
        total = scorer.compute_total_score([8.0, 9.0, 8.5], priority_region="KV1")
        assert total == 25.5 + 0.75

    def test_compute_total_score_kv2nt(self, scorer):
        """KV2-NT được cộng 0.5 điểm."""
        total = scorer.compute_total_score([8.0, 9.0, 8.5], priority_region="KV2-NT")
        assert total == 25.5 + 0.5

    def test_safety_score_above(self, scorer):
        """Điểm thí sinh cao hơn điểm chuẩn → safety > 0."""
        score = scorer.compute_safety_score(27.0, 25.0)
        assert score > 0

    def test_safety_score_below(self, scorer):
        """Điểm thí sinh thấp hơn điểm chuẩn → safety < 0."""
        score = scorer.compute_safety_score(24.0, 25.0)
        assert score < 0

    def test_safety_score_equal(self, scorer):
        """Điểm bằng điểm chuẩn → safety = 0."""
        score = scorer.compute_safety_score(25.0, 25.0)
        assert score == 0.0

    def test_classify_safety_an_toan(self, scorer):
        """Safety ≥ 10% → An toàn."""
        label = scorer.classify_safety(15.0)
        assert "An toàn" in label

    def test_classify_safety_tuong_doi(self, scorer):
        """0 ≤ Safety < 10% → Tương đối."""
        label = scorer.classify_safety(5.0)
        assert "Tương đối" in label

    def test_classify_safety_rui_ro(self, scorer):
        """Safety < 0 → Rủi ro hoặc Không khuyến nghị."""
        label = scorer.classify_safety(-5.0)
        assert "Rủi ro" in label or "Không khuyến nghị" in label

    def test_classify_safety_khong_khuyen_nghi(self, scorer):
        """Safety < -10% → Không khuyến nghị."""
        label = scorer.classify_safety(-15.0)
        assert "Không khuyến nghị" in label

    def test_score_recommendations_returns_df(self, scorer, sample_admission_df):
        result = scorer.score_recommendations(sample_admission_df, student_total_score=25.0)
        assert isinstance(result, pd.DataFrame)
        assert "safety_score" in result.columns
        assert "safety_label" in result.columns

    def test_score_recommendations_sorted(self, scorer, sample_admission_df):
        """Kết quả phải được sort: an toàn nhất trên cùng."""
        result = scorer.score_recommendations(sample_admission_df, student_total_score=28.0)
        if len(result) > 1:
            # Không có row "Không khuyến nghị" trước "An toàn"
            labels = result["safety_label"].tolist()
            safe_idx = [i for i, l in enumerate(labels) if "An toàn" in l]
            risky_idx = [i for i, l in enumerate(labels) if "Không khuyến nghị" in l]
            if safe_idx and risky_idx:
                assert min(safe_idx) < max(risky_idx)


# ================================================================
# Test AdmissionRecommender
# ================================================================

class TestAdmissionRecommender:

    def test_recommend_returns_df(self, recommender):
        result = recommender.recommend(
            scores=[9.0, 9.0, 9.0],
            subject_group="A00",
        )
        assert isinstance(result, pd.DataFrame)

    def test_recommend_filters_by_subject_group(self, recommender):
        result = recommender.recommend(
            scores=[9.0, 9.0, 9.0],
            subject_group="A00",
        )
        if not result.empty and "subject_group" in result.columns:
            assert all(result["subject_group"] == "A00")

    def test_recommend_high_score_gets_results(self, recommender):
        """Điểm cao → có nhiều kết quả."""
        result = recommender.recommend(
            scores=[9.5, 9.5, 9.5],  # Tổng = 28.5 → đủ điều kiện hầu hết
            subject_group="A00",
        )
        assert len(result) > 0

    def test_recommend_very_low_score_no_results(self, recommender):
        """Điểm rất thấp → ít hoặc không có kết quả an toàn."""
        result = recommender.recommend(
            scores=[4.0, 4.0, 4.0],  # Tổng = 12.0 → rất thấp
            subject_group="A00",
            include_risky=False,  # Không bao gồm rủi ro
        )
        # Với điểm thấp như vậy, không có an toàn
        if not result.empty:
            assert all("An toàn" not in row for row in result.get("safety_label", []))

    def test_recommend_top_n_respected(self, recommender):
        result = recommender.recommend(
            scores=[9.0, 9.0, 9.0],
            subject_group="A00",
            top_n=2,
        )
        assert len(result) <= 2

    def test_from_csv_with_nonexistent_file(self):
        """from_csv với file không tồn tại → trả về empty data."""
        rec = AdmissionRecommender.from_csv(data_path="/nonexistent/path.csv")
        assert rec.data.empty

    def test_recommend_with_empty_data(self):
        rec = AdmissionRecommender(pd.DataFrame())
        result = rec.recommend(scores=[9.0, 9.0, 9.0], subject_group="A00")
        assert result.empty

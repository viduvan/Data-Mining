"""
tests/test_preprocessing.py
Unit tests cho preprocessing module
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.preprocessing.data_cleaner import DataCleaner
from src.preprocessing.feature_engineering import FeatureEngineer
from src.preprocessing.validators import DataValidator


# ================================================================
# Fixtures — Dữ liệu mẫu
# ================================================================

@pytest.fixture
def sample_df():
    """DataFrame mẫu cho testing."""
    return pd.DataFrame({
        "school_code": ["BKH", "NEU", "BKH", "NEU", "FTU"],
        "school_name": [
            "Đại học Bách khoa Hà Nội",
            "Đại học Kinh tế Quốc dân",
            "Đại học Bách khoa Hà Nội",
            "Đại học Kinh tế Quốc dân",
            "Đại học Ngoại thương",
        ],
        "major_code": ["7480201", "7340101", "7480201", "7340101", "7340120"],
        "major_name": [
            "Công nghệ thông tin",
            "Kinh tế",
            "Công nghệ thông tin",
            "Kinh tế",
            "Kinh tế quốc tế",
        ],
        "subject_group": ["A00", "A01", "A00", "A01", "D01"],
        "admission_score": [27.04, 26.5, 26.8, 26.0, 25.5],
        "quota": [200, 300, 210, 310, 150],
        "admission_method": ["THPT"] * 5,
        "year": [2023, 2023, 2024, 2024, 2024],
        "source_url": ["http://example.com"] * 5,
        "crawled_at": ["2024-01-01"] * 5,
    })


@pytest.fixture
def dirty_df():
    """DataFrame với dữ liệu bẩn để test cleaning."""
    return pd.DataFrame({
        "school_name": ["  ĐH Bách khoa HN  ", None, "Đại học Kinh tế QD"],
        "major_name": ["7480201 - Công nghệ thông tin", "Kinh tế", ""],
        "subject_group": ["a 00", "A01", "D01"],
        "admission_score": [27.0, 35.0, None],  # 35 là không hợp lệ
        "quota": [200, None, 150],
        "year": [2023, 2023, 2023],
        "admission_method": [None, "THPT", "THPT"],
        "school_code": ["BKH", "NEU", "FTU"],
        "major_code": ["7480201", "7340101", "7340120"],
        "source_url": [""] * 3,
        "crawled_at": ["2024-01-01"] * 3,
    })


# ================================================================
# Test DataCleaner
# ================================================================

class TestDataCleaner:

    def test_clean_removes_invalid_score(self, dirty_df):
        cleaner = DataCleaner()
        cleaned = cleaner.clean_admission_data(dirty_df)
        # Điểm 35 không hợp lệ phải bị loại
        assert cleaned["admission_score"].max() <= 30.0

    def test_clean_removes_null_school(self, dirty_df):
        cleaner = DataCleaner()
        cleaned = cleaner.clean_admission_data(dirty_df)
        # Không có school_name null
        assert cleaned["school_name"].isna().sum() == 0

    def test_clean_removes_null_score(self, dirty_df):
        cleaner = DataCleaner()
        cleaned = cleaner.clean_admission_data(dirty_df)
        assert cleaned["admission_score"].isna().sum() == 0

    def test_normalize_subject_group(self, dirty_df):
        cleaner = DataCleaner()
        cleaned = cleaner.clean_admission_data(dirty_df)
        # "a 00" phải được chuẩn hóa thành "A00"
        valid_records = cleaned[cleaned["school_name"].str.contains("Bách khoa", na=False)]
        if not valid_records.empty:
            assert valid_records["subject_group"].iloc[0] == "A00"

    def test_clean_returns_dataframe(self, sample_df):
        cleaner = DataCleaner()
        result = cleaner.clean_admission_data(sample_df)
        assert isinstance(result, pd.DataFrame)

    def test_clean_valid_data_retains_records(self, sample_df):
        cleaner = DataCleaner()
        result = cleaner.clean_admission_data(sample_df)
        assert len(result) > 0

    def test_fill_missing_admission_method(self, dirty_df):
        cleaner = DataCleaner()
        cleaned = cleaner.clean_admission_data(dirty_df)
        if "admission_method" in cleaned.columns:
            assert cleaned["admission_method"].isna().sum() == 0


# ================================================================
# Test FeatureEngineer
# ================================================================

class TestFeatureEngineer:

    def test_adds_major_group(self, sample_df):
        engineer = FeatureEngineer()
        result = engineer.engineer_features(sample_df)
        assert "major_group" in result.columns

    def test_adds_competition_level(self, sample_df):
        engineer = FeatureEngineer()
        result = engineer.engineer_features(sample_df)
        assert "competition_level" in result.columns

    def test_competition_level_values(self, sample_df):
        engineer = FeatureEngineer()
        result = engineer.engineer_features(sample_df)
        valid_levels = {"Rất cao", "Cao", "Trung bình", "Thấp", None, float("nan")}
        unique_levels = set(result["competition_level"].dropna().unique())
        assert unique_levels.issubset(valid_levels)

    def test_adds_delta_score(self, sample_df):
        engineer = FeatureEngineer()
        result = engineer.engineer_features(sample_df)
        assert "delta_score" in result.columns

    def test_adds_score_trend(self, sample_df):
        engineer = FeatureEngineer()
        result = engineer.engineer_features(sample_df)
        assert "score_trend" in result.columns

    def test_cntt_classified_correctly(self, sample_df):
        engineer = FeatureEngineer()
        result = engineer.engineer_features(sample_df)
        cntt_rows = result[result["major_name"] == "Công nghệ thông tin"]
        if not cntt_rows.empty:
            assert cntt_rows["major_group"].iloc[0] == "Kỹ thuật - Công nghệ"

    def test_high_score_very_competitive(self, sample_df):
        engineer = FeatureEngineer()
        result = engineer.engineer_features(sample_df)
        high_rows = result[result["admission_score"] >= 25.0]
        assert (high_rows["competition_level"] == "Rất cao").all()


# ================================================================
# Test DataValidator
# ================================================================

class TestDataValidator:

    def test_valid_data_passes(self, sample_df):
        validator = DataValidator()
        result = validator.validate_admission_data(sample_df)
        assert result.is_valid is True

    def test_empty_df_fails(self):
        validator = DataValidator()
        result = validator.validate_admission_data(pd.DataFrame())
        assert result.is_valid is False

    def test_missing_required_column_fails(self):
        validator = DataValidator()
        df = pd.DataFrame({"school_name": ["Test"], "year": [2023]})
        # Thiếu admission_score
        result = validator.validate_admission_data(df)
        assert result.is_valid is False

    def test_stats_computed(self, sample_df):
        validator = DataValidator()
        result = validator.validate_admission_data(sample_df)
        assert "total_records" in result.stats
        assert result.stats["total_records"] == len(sample_df)

    def test_out_of_range_score_fails(self):
        validator = DataValidator()
        df = pd.DataFrame({
            "school_name": ["Test School"],
            "admission_score": [35.0],  # Vượt range
            "year": [2023],
        })
        result = validator.validate_admission_data(df)
        assert result.is_valid is False
        assert len(result.errors) > 0

"""
src/preprocessing/feature_engineering.py
Tạo các features mới từ dữ liệu đã clean:
- delta_score: Chênh lệch điểm chuẩn so với năm trước
- competition_level: Mức độ cạnh tranh
- major_group: Nhóm ngành
- score_trend: Xu hướng tăng/giảm/ổn định
"""

import pandas as pd
import numpy as np
from loguru import logger

from .data_cleaner import MAJOR_GROUP_MAPPING


class FeatureEngineer:
    """
    Tạo features mới cho dữ liệu tuyển sinh.

    Features được tạo:
    - delta_score      : Thay đổi điểm chuẩn so với năm trước (YoY)
    - delta_score_pct  : Thay đổi % so với năm trước
    - competition_level: Rất cao / Cao / Trung bình / Thấp
    - major_group      : Nhóm ngành học
    - score_trend      : Tăng / Giảm / Ổn định (dựa trên 2 năm gần nhất)
    - avg_score_school : Điểm trung bình của trường (across ngành, năm đó)
    - rank_in_year     : Thứ hạng điểm chuẩn trong cùng năm
    """

    # Ngưỡng phân loại mức cạnh tranh
    COMPETITION_THRESHOLDS = {
        "Rất cao": 25.0,
        "Cao": 22.0,
        "Trung bình": 18.0,
        # < 18: Thấp
    }

    # Ngưỡng delta để xác định trend
    TREND_THRESHOLD = 0.5  # Thay đổi ≥ 0.5 điểm = Tăng/Giảm

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Áp dụng tất cả feature engineering.

        Args:
            df: DataFrame đã clean

        Returns:
            DataFrame với các cột features mới
        """
        logger.info("Bắt đầu Feature Engineering...")
        df = df.copy()
        df = df.sort_values(["school_name", "major_name", "subject_group", "year"])

        df = self._add_major_group(df)
        df = self._add_competition_level(df)
        df = self._add_delta_score(df)
        df = self._add_score_trend(df)
        df = self._add_school_avg_score(df)
        df = self._add_year_rank(df)

        logger.success(f"Feature Engineering hoàn tất. Shape: {df.shape}")
        return df

    def _add_major_group(self, df: pd.DataFrame) -> pd.DataFrame:
        """Phân nhóm ngành học dựa trên tên ngành."""
        def classify_major(major_name: str) -> str:
            if pd.isna(major_name) or not major_name:
                return "Khác"
            major_lower = str(major_name).lower()
            for keyword, group in MAJOR_GROUP_MAPPING.items():
                if keyword in major_lower:
                    return group
            return "Khác"

        df["major_group"] = df["major_name"].apply(classify_major)
        distribution = df["major_group"].value_counts()
        logger.info(f"Phân nhóm ngành:\n{distribution.to_string()}")
        return df

    def _add_competition_level(self, df: pd.DataFrame) -> pd.DataFrame:
        """Phân loại mức độ cạnh tranh dựa trên điểm chuẩn."""
        def classify_competition(score: float) -> str:
            if pd.isna(score):
                return None
            if score >= self.COMPETITION_THRESHOLDS["Rất cao"]:
                return "Rất cao"
            elif score >= self.COMPETITION_THRESHOLDS["Cao"]:
                return "Cao"
            elif score >= self.COMPETITION_THRESHOLDS["Trung bình"]:
                return "Trung bình"
            else:
                return "Thấp"

        df["competition_level"] = df["admission_score"].apply(classify_competition)
        return df

    def _add_delta_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tính chênh lệch điểm chuẩn so với năm trước (Year-over-Year).
        Group by: school_name + major_name + subject_group
        """
        group_key = ["school_name", "major_name", "subject_group"]

        # Shift trong group theo năm
        df["delta_score"] = df.groupby(group_key)["admission_score"].diff()
        df["delta_score_pct"] = (
            df["delta_score"] / df.groupby(group_key)["admission_score"].shift(1) * 100
        ).round(2)

        logger.info(
            f"delta_score: mean={df['delta_score'].mean():.2f}, "
            f"std={df['delta_score'].std():.2f}"
        )
        return df

    def _add_score_trend(self, df: pd.DataFrame) -> pd.DataFrame:
        """Xác định xu hướng điểm chuẩn dựa trên delta_score."""
        def classify_trend(delta: float) -> str:
            if pd.isna(delta):
                return "Không xác định"
            if delta >= self.TREND_THRESHOLD:
                return "Tăng"
            elif delta <= -self.TREND_THRESHOLD:
                return "Giảm"
            else:
                return "Ổn định"

        df["score_trend"] = df["delta_score"].apply(classify_trend)
        return df

    def _add_school_avg_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Tính điểm trung bình của trường trong từng năm."""
        school_avg = (
            df.groupby(["school_name", "year"])["admission_score"]
            .mean()
            .round(2)
            .rename("avg_score_school")
            .reset_index()
        )
        df = df.merge(school_avg, on=["school_name", "year"], how="left")
        return df

    def _add_year_rank(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tính thứ hạng điểm chuẩn trong từng năm.
        Rank 1 = điểm cao nhất trong năm đó.
        """
        df["rank_in_year"] = (
            df.groupby("year")["admission_score"]
            .rank(method="min", ascending=False)
            .astype("Int64")
        )
        return df

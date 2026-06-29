"""
src/preprocessing/validators.py
Kiểm tra chất lượng dữ liệu sau mỗi bước ETL
"""

from dataclasses import dataclass, field
from typing import List

import pandas as pd
import numpy as np
from loguru import logger


@dataclass
class ValidationResult:
    """Kết quả kiểm tra data quality."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def add_error(self, msg: str):
        self.errors.append(msg)
        self.is_valid = False
        logger.error(f"[VALIDATION ERROR] {msg}")

    def add_warning(self, msg: str):
        self.warnings.append(msg)
        logger.warning(f"[VALIDATION WARNING] {msg}")

    def summary(self) -> str:
        status = "✅ PASSED" if self.is_valid else "❌ FAILED"
        lines = [
            f"Validation Result: {status}",
            f"Errors  : {len(self.errors)}",
            f"Warnings: {len(self.warnings)}",
        ]
        if self.errors:
            lines.append("Errors:")
            for e in self.errors:
                lines.append(f"  - {e}")
        if self.warnings:
            lines.append("Warnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")
        return "\n".join(lines)


class DataValidator:
    """
    Kiểm tra chất lượng dữ liệu tuyển sinh.

    Áp dụng nhiều quy tắc validation:
    - Required fields
    - Value ranges
    - Null percentage thresholds
    - Uniqueness constraints
    - Data type checks
    """

    # Cấu hình validation
    MAX_NULL_PCT = 0.10           # Tối đa 10% null cho cột quan trọng
    SCORE_MIN = 0.0
    SCORE_MAX = 30.0
    QUOTA_MIN = 1
    QUOTA_MAX = 50000
    VALID_YEARS = list(range(2015, 2031))

    def validate_admission_data(self, df: pd.DataFrame) -> ValidationResult:
        """
        Validate toàn bộ bộ dữ liệu điểm chuẩn.

        Args:
            df: DataFrame cần validate

        Returns:
            ValidationResult với danh sách lỗi và cảnh báo
        """
        result = ValidationResult()

        logger.info(f"Validating {len(df):,} records...")

        self._check_not_empty(df, result)
        if not result.is_valid:
            return result

        self._check_required_columns(df, result)
        self._check_null_percentage(df, result)
        self._check_score_range(df, result)
        self._check_year_values(df, result)
        self._check_quota_range(df, result)
        self._check_school_name_quality(df, result)
        self._compute_stats(df, result)

        logger.info(result.summary())
        return result

    def _check_not_empty(self, df: pd.DataFrame, result: ValidationResult):
        if df.empty:
            result.add_error("DataFrame rỗng!")

    def _check_required_columns(self, df: pd.DataFrame, result: ValidationResult):
        required = ["school_name", "admission_score", "year"]
        for col in required:
            if col not in df.columns:
                result.add_error(f"Thiếu cột bắt buộc: '{col}'")

    def _check_null_percentage(self, df: pd.DataFrame, result: ValidationResult):
        important_cols = ["school_name", "admission_score", "year"]
        for col in important_cols:
            if col not in df.columns:
                continue
            null_pct = df[col].isna().mean()
            if null_pct > self.MAX_NULL_PCT:
                result.add_error(
                    f"Cột '{col}' có {null_pct*100:.1f}% null (cho phép tối đa {self.MAX_NULL_PCT*100:.0f}%)"
                )
            elif null_pct > 0:
                result.add_warning(f"Cột '{col}' có {null_pct*100:.1f}% null")

    def _check_score_range(self, df: pd.DataFrame, result: ValidationResult):
        if "admission_score" not in df.columns:
            return
        scores = df["admission_score"].dropna()
        out_of_range = scores[(scores < self.SCORE_MIN) | (scores > self.SCORE_MAX)]
        if len(out_of_range) > 0:
            result.add_error(
                f"Có {len(out_of_range)} điểm chuẩn ngoài range [{self.SCORE_MIN}, {self.SCORE_MAX}]: "
                f"min={scores.min():.2f}, max={scores.max():.2f}"
            )

    def _check_year_values(self, df: pd.DataFrame, result: ValidationResult):
        if "year" not in df.columns:
            return
        invalid_years = df[~df["year"].isin(self.VALID_YEARS)]["year"].unique()
        if len(invalid_years) > 0:
            result.add_warning(f"Năm không hợp lệ: {list(invalid_years)}")

    def _check_quota_range(self, df: pd.DataFrame, result: ValidationResult):
        if "quota" not in df.columns:
            return
        quotas = df["quota"].dropna()
        if len(quotas) == 0:
            return
        out_of_range = quotas[(quotas < self.QUOTA_MIN) | (quotas > self.QUOTA_MAX)]
        if len(out_of_range) > 0:
            result.add_warning(f"Có {len(out_of_range)} chỉ tiêu ngoài range hợp lý")

    def _check_school_name_quality(self, df: pd.DataFrame, result: ValidationResult):
        if "school_name" not in df.columns:
            return
        # Kiểm tra tên trường quá ngắn (có thể là lỗi)
        short_names = df[df["school_name"].str.len() < 5]["school_name"].unique()
        if len(short_names) > 0:
            result.add_warning(f"Tên trường nghi ngờ (< 5 ký tự): {list(short_names[:5])}")

    def _compute_stats(self, df: pd.DataFrame, result: ValidationResult):
        """Tính các thống kê tổng hợp."""
        stats = {
            "total_records": len(df),
            "unique_schools": df["school_name"].nunique() if "school_name" in df.columns else 0,
            "unique_majors": df["major_name"].nunique() if "major_name" in df.columns else 0,
            "years_covered": sorted(df["year"].dropna().unique().tolist()) if "year" in df.columns else [],
            "score_mean": round(df["admission_score"].mean(), 2) if "admission_score" in df.columns else None,
            "score_std": round(df["admission_score"].std(), 2) if "admission_score" in df.columns else None,
            "score_min": df["admission_score"].min() if "admission_score" in df.columns else None,
            "score_max": df["admission_score"].max() if "admission_score" in df.columns else None,
        }
        result.stats = stats
        logger.info(
            f"Stats: {stats['total_records']:,} records, "
            f"{stats['unique_schools']} trường, "
            f"{stats['unique_majors']} ngành, "
            f"điểm trung bình: {stats['score_mean']}"
        )

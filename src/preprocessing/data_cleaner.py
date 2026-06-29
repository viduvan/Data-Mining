"""
src/preprocessing/data_cleaner.py
Làm sạch dữ liệu tuyển sinh raw:
- Chuẩn hóa tên trường, tên ngành
- Loại bỏ duplicates
- Xử lý missing values
- Validate kiểu dữ liệu
"""

import re
import unicodedata
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np
from loguru import logger


# ================================================================
# Mapping chuẩn hóa tên trường
# Các tên viết khác nhau → tên chuẩn
# ================================================================
SCHOOL_NAME_MAPPING = {
    # Đại học Quốc gia
    "đhqghn": "Đại học Quốc gia Hà Nội",
    "đại học quốc gia hà nội": "Đại học Quốc gia Hà Nội",
    "vnu hanoi": "Đại học Quốc gia Hà Nội",
    "đhqg tp.hcm": "Đại học Quốc gia TP.HCM",
    "đại học quốc gia tp hồ chí minh": "Đại học Quốc gia TP.HCM",
    "vnu hcmc": "Đại học Quốc gia TP.HCM",
    # Bách khoa
    "đh bách khoa hà nội": "Đại học Bách khoa Hà Nội",
    "đại học bách khoa hn": "Đại học Bách khoa Hà Nội",
    "hust": "Đại học Bách khoa Hà Nội",
    "đh bách khoa tp.hcm": "Đại học Bách khoa TP.HCM",
    "đại học bách khoa hcm": "Đại học Bách khoa TP.HCM",
    "hcmut": "Đại học Bách khoa TP.HCM",
    # Kinh tế
    "neu": "Đại học Kinh tế Quốc dân",
    "đhktqd": "Đại học Kinh tế Quốc dân",
    "ueh": "Đại học Kinh tế TP.HCM",
    # Ngoại thương
    "ftu": "Đại học Ngoại thương",
    "đh ngoại thương hà nội": "Đại học Ngoại thương",
}

# ================================================================
# Mapping chuẩn hóa nhóm ngành
# ================================================================
MAJOR_GROUP_MAPPING = {
    # Kỹ thuật - Công nghệ
    "công nghệ thông tin": "Kỹ thuật - Công nghệ",
    "kỹ thuật": "Kỹ thuật - Công nghệ",
    "công nghệ": "Kỹ thuật - Công nghệ",
    "điện": "Kỹ thuật - Công nghệ",
    "điện tử": "Kỹ thuật - Công nghệ",
    "cơ khí": "Kỹ thuật - Công nghệ",
    "xây dựng": "Kỹ thuật - Công nghệ",
    "kiến trúc": "Kỹ thuật - Công nghệ",
    "hóa học": "Kỹ thuật - Công nghệ",
    "vật lý": "Kỹ thuật - Công nghệ",
    # Kinh tế - Quản trị
    "kinh tế": "Kinh tế - Quản trị",
    "quản trị": "Kinh tế - Quản trị",
    "tài chính": "Kinh tế - Quản trị",
    "kế toán": "Kinh tế - Quản trị",
    "ngân hàng": "Kinh tế - Quản trị",
    "thương mại": "Kinh tế - Quản trị",
    "marketing": "Kinh tế - Quản trị",
    # Y - Dược
    "y khoa": "Y - Dược",
    "y học": "Y - Dược",
    "dược": "Y - Dược",
    "điều dưỡng": "Y - Dược",
    "y tế": "Y - Dược",
    # Sư phạm - Giáo dục
    "sư phạm": "Sư phạm - Giáo dục",
    "giáo dục": "Sư phạm - Giáo dục",
    # Luật - Xã hội
    "luật": "Luật - Xã hội",
    "xã hội": "Luật - Xã hội",
    "chính trị": "Luật - Xã hội",
    "quan hệ quốc tế": "Luật - Xã hội",
    # Nghệ thuật - Nhân văn
    "nghệ thuật": "Nghệ thuật - Nhân văn",
    "ngôn ngữ": "Nghệ thuật - Nhân văn",
    "văn học": "Nghệ thuật - Nhân văn",
    "lịch sử": "Nghệ thuật - Nhân văn",
    "triết học": "Nghệ thuật - Nhân văn",
    # Nông - Lâm - Ngư
    "nông nghiệp": "Nông - Lâm - Ngư",
    "lâm nghiệp": "Nông - Lâm - Ngư",
    "thủy sản": "Nông - Lâm - Ngư",
    "thú y": "Nông - Lâm - Ngư",
}


class DataCleaner:
    """
    Làm sạch và chuẩn hóa dữ liệu tuyển sinh raw.

    Quy trình:
    1. Load raw CSV files
    2. Chuẩn hóa encoding
    3. Chuẩn hóa tên trường, tên ngành
    4. Loại bỏ duplicates
    5. Xử lý missing values
    6. Validate kiểu dữ liệu
    7. Export clean data
    """

    def __init__(self):
        self.stats = {
            "total_raw": 0,
            "duplicates_removed": 0,
            "invalid_score": 0,
            "missing_school": 0,
            "total_clean": 0,
        }

    def clean_admission_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline làm sạch chính cho dữ liệu điểm chuẩn.

        Args:
            df: DataFrame raw từ CSV

        Returns:
            DataFrame đã làm sạch
        """
        self.stats["total_raw"] = len(df)
        logger.info(f"Bắt đầu làm sạch {len(df):,} records...")

        df = df.copy()

        # Bước 1: Chuẩn hóa cột string
        df = self._normalize_string_columns(df)

        # Bước 2: Chuẩn hóa tên trường
        df = self._normalize_school_names(df)

        # Bước 3: Chuẩn hóa tên ngành
        df = self._normalize_major_names(df)

        # Bước 4: Chuẩn hóa tổ hợp xét tuyển
        df = self._normalize_subject_groups(df)

        # Bước 5: Xử lý kiểu dữ liệu số
        df = self._fix_numeric_columns(df)

        # Bước 6: Xử lý missing values
        df = self._handle_missing_values(df)

        # Bước 7: Loại bỏ duplicates
        df = self._remove_duplicates(df)

        # Bước 8: Filter dữ liệu không hợp lệ
        df = self._filter_invalid_records(df)

        # Bước 9: Reset index
        df = df.reset_index(drop=True)

        self.stats["total_clean"] = len(df)
        self._log_stats()

        return df

    def clean_school_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """Làm sạch dữ liệu thông tin trường."""
        df = df.copy()
        string_cols = ["school_name", "school_type", "region", "province", "website"]
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace("nan", None)

        # Loại bỏ duplicates theo school_name
        df = df.drop_duplicates(subset=["school_name"], keep="first")
        df = df.reset_index(drop=True)
        logger.info(f"School info sau cleaning: {len(df)} trường")
        return df

    # ================================================================
    # Normalization methods
    # ================================================================

    def _normalize_string_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Strip whitespace và chuẩn hóa unicode cho các cột string."""
        str_cols = ["school_code", "school_name", "major_code", "major_name",
                    "subject_group", "admission_method"]
        for col in str_cols:
            if col in df.columns:
                def _norm(x):
                    if x is None:
                        return None
                    s = str(x)
                    if s in ("nan", "None", ""):
                        return None
                    try:
                        return unicodedata.normalize("NFC", s.strip()) or None
                    except Exception:
                        return None
                df[col] = df[col].apply(_norm)
        return df

    def _normalize_school_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Chuẩn hóa tên trường: mapping + format."""
        if "school_name" not in df.columns:
            return df

        def normalize(name):
            if pd.isna(name) or not name:
                return name
            name = str(name).strip()
            # Thử lookup mapping
            name_lower = name.lower()
            if name_lower in SCHOOL_NAME_MAPPING:
                return SCHOOL_NAME_MAPPING[name_lower]
            # Chuẩn hóa viết tắt
            name = re.sub(r"\bĐH\b", "Đại học", name)
            name = re.sub(r"\bHV\b", "Học viện", name)
            name = re.sub(r"\bTP HCM\b", "TP.HCM", name)
            name = re.sub(r"\bTP Hồ Chí Minh\b", "TP.HCM", name)
            # Collapse multiple spaces
            name = re.sub(r"\s+", " ", name).strip()
            return name

        df["school_name"] = df["school_name"].apply(normalize)
        return df

    def _normalize_major_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Chuẩn hóa tên ngành: loại bỏ mã ngành ở đầu."""
        if "major_name" not in df.columns:
            return df

        def normalize(name):
            if pd.isna(name) or not name:
                return name
            name = str(name).strip()
            # Loại bỏ mã ngành 7 số ở đầu (VD: "7480201 - Công nghệ thông tin")
            name = re.sub(r"^\d{7}\s*[-–]\s*", "", name)
            name = re.sub(r"\s+", " ", name).strip()
            return name

        df["major_name"] = df["major_name"].apply(normalize)
        return df

    def _normalize_subject_groups(self, df: pd.DataFrame) -> pd.DataFrame:
        """Chuẩn hóa tổ hợp xét tuyển (A00, D01, C00...)."""
        if "subject_group" not in df.columns:
            return df

        def normalize(group):
            if pd.isna(group) or not group:
                return group
            group = str(group).strip().upper()
            group = re.sub(r"\s+", "", group)
            # Match pattern: chữ + 2 số
            match = re.match(r"([A-Z])(\d{2})", group)
            if match:
                return f"{match.group(1)}{match.group(2)}"
            return group

        df["subject_group"] = df["subject_group"].apply(normalize)
        return df

    def _fix_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Chuẩn hóa kiểu dữ liệu số."""
        # Điểm chuẩn
        if "admission_score" in df.columns:
            df["admission_score"] = pd.to_numeric(
                df["admission_score"].astype(str).str.replace(",", "."),
                errors="coerce"
            )

        # Chỉ tiêu
        if "quota" in df.columns:
            df["quota"] = pd.to_numeric(
                df["quota"].astype(str).str.replace(".", "").str.replace(",", ""),
                errors="coerce"
            ).astype("Int64")  # Nullable integer

        # Năm
        if "year" in df.columns:
            df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Xử lý missing values."""
        # school_name: bắt buộc, không thể điền
        missing_school = df["school_name"].isna().sum()
        if missing_school > 0:
            logger.warning(f"Loại {missing_school} records thiếu tên trường")
            self.stats["missing_school"] = missing_school
            df = df.dropna(subset=["school_name"])

        # admission_score: bắt buộc
        df = df.dropna(subset=["admission_score"])

        # year: bắt buộc
        df = df.dropna(subset=["year"])

        # subject_group: điền mặc định nếu thiếu
        if "subject_group" in df.columns:
            df["subject_group"] = df["subject_group"].fillna("Không xác định")

        # admission_method: điền mặc định
        if "admission_method" in df.columns:
            df["admission_method"] = df["admission_method"].fillna("Xét điểm thi THPT")

        return df

    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Loại bỏ duplicates."""
        key_cols = ["school_name", "major_name", "subject_group", "year"]
        available_keys = [c for c in key_cols if c in df.columns]

        before = len(df)
        df = df.drop_duplicates(subset=available_keys, keep="first")
        removed = before - len(df)

        if removed > 0:
            logger.info(f"Loại bỏ {removed:,} records trùng lặp")
            self.stats["duplicates_removed"] = removed

        return df

    def _filter_invalid_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """Lọc bỏ records không hợp lệ."""
        before = len(df)

        # Điểm chuẩn phải trong range 0-30
        if "admission_score" in df.columns:
            invalid_score = ~df["admission_score"].between(0, 30)
            count = invalid_score.sum()
            if count > 0:
                logger.warning(f"Loại {count} records có điểm chuẩn ngoài range [0, 30]")
                self.stats["invalid_score"] = count
                df = df[~invalid_score]

        # Năm phải trong range hợp lý
        if "year" in df.columns:
            df = df[df["year"].between(2000, 2030)]

        after = len(df)
        logger.info(f"Filter invalid: {before - after} records bị loại")
        return df

    def _log_stats(self) -> None:
        """In thống kê cleaning."""
        logger.info("=" * 50)
        logger.info("THỐNG KÊ DATA CLEANING")
        logger.info(f"  Raw records      : {self.stats['total_raw']:,}")
        logger.info(f"  Duplicates xóa   : {self.stats['duplicates_removed']:,}")
        logger.info(f"  Invalid score    : {self.stats['invalid_score']:,}")
        logger.info(f"  Missing school   : {self.stats['missing_school']:,}")
        logger.info(f"  Clean records    : {self.stats['total_clean']:,}")
        retention = self.stats['total_clean'] / max(self.stats['total_raw'], 1) * 100
        logger.info(f"  Retention rate   : {retention:.1f}%")
        logger.info("=" * 50)

    def load_raw_files(self, raw_dir: Path, years: list = None) -> pd.DataFrame:
        """Load và merge tất cả file raw CSV."""
        dfs = []
        pattern = "admission_*.csv"
        files = sorted(raw_dir.glob(pattern))

        if not files:
            logger.error(f"Không tìm thấy file nào trong {raw_dir}")
            return pd.DataFrame()

        for file in files:
            try:
                # Lấy năm từ tên file
                year_match = re.search(r"admission_(\d{4})\.csv", file.name)
                if year_match:
                    year = int(year_match.group(1))
                    if years and year not in years:
                        continue

                df = pd.read_csv(file, encoding="utf-8-sig")
                dfs.append(df)
                logger.info(f"  Loaded {file.name}: {len(df):,} records")
            except Exception as e:
                logger.error(f"Lỗi đọc {file}: {e}")

        if not dfs:
            return pd.DataFrame()

        combined = pd.concat(dfs, ignore_index=True)
        logger.info(f"Tổng: {len(combined):,} records từ {len(dfs)} files")
        return combined

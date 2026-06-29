"""
src/preprocessing/db_loader.py
Load dữ liệu clean vào PostgreSQL Data Warehouse
Sử dụng SQLAlchemy + psycopg2
"""

import os
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


def get_db_url() -> str:
    """Tạo PostgreSQL connection URL từ biến môi trường."""
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "vietnam_admission_dw")
    user = os.getenv("DB_USER", "admission_user")
    password = os.getenv("DB_PASSWORD", "")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"


class DBLoader:
    """
    Load dữ liệu vào PostgreSQL Data Warehouse.

    Hỗ trợ:
    - Load Dimension tables trước (lookup data)
    - Load Fact table sau (với FK references)
    - Upsert logic (tránh duplicate khi chạy lại)
    - Batch insert để tối ưu performance
    """

    BATCH_SIZE = 1000  # Số records mỗi batch insert

    def __init__(self, db_url: str = None):
        self.db_url = db_url or get_db_url()
        self.engine = self._create_engine()

    def _create_engine(self) -> Engine:
        """Tạo SQLAlchemy engine."""
        try:
            engine = create_engine(
                self.db_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,  # Kiểm tra connection trước khi dùng
                echo=False,
            )
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.success(f"Kết nối PostgreSQL thành công!")
            return engine
        except Exception as e:
            logger.error(f"Không thể kết nối PostgreSQL: {e}")
            raise

    def load_all(
        self,
        admission_df: pd.DataFrame,
        school_df: pd.DataFrame = None,
    ) -> dict:
        """
        Load toàn bộ dữ liệu vào Data Warehouse.
        Thứ tự: Dimensions trước → Fact sau.

        Args:
            admission_df: DataFrame điểm chuẩn đã clean + feature engineering
            school_df: DataFrame thông tin trường (optional)

        Returns:
            Dict thống kê số records đã load
        """
        summary = {}
        logger.info("Bắt đầu load dữ liệu vào PostgreSQL Data Warehouse...")

        # 1. Load Dimension Tables
        summary["dim_year"] = self._load_dim_year(admission_df)
        summary["dim_region"] = self._load_dim_region(admission_df, school_df)
        summary["dim_school"] = self._load_dim_school(admission_df, school_df)
        summary["dim_major"] = self._load_dim_major(admission_df)
        summary["dim_subject_group"] = self._load_dim_subject_group(admission_df)

        # 2. Load Fact Table
        summary["fact_admission"] = self._load_fact_admission(admission_df)

        # Log tổng kết
        logger.info("=" * 50)
        logger.info("KẾT QUẢ LOAD DỮ LIỆU VÀO POSTGRESQL")
        for table, count in summary.items():
            logger.info(f"  {table}: {count:,} records")
        logger.info("=" * 50)

        return summary

    # ================================================================
    # Load Dimension Tables
    # ================================================================

    def _load_dim_year(self, df: pd.DataFrame) -> int:
        """Load dim_year từ các năm có trong dữ liệu."""
        years = df["year"].dropna().unique()
        records = []
        for year in sorted(years):
            year = int(year)
            if year <= 2022:
                period = "Giai đoạn COVID (2020-2022)"
            else:
                period = "Giai đoạn Hậu COVID (2023-2025)"
            records.append({"year": year, "period_label": period})

        dim_df = pd.DataFrame(records)
        return self._upsert_table(dim_df, "dim_year", conflict_cols=["year"])

    def _load_dim_region(
        self, admission_df: pd.DataFrame, school_df: pd.DataFrame = None
    ) -> int:
        """Load dim_region."""
        regions = [
            {"region_code": "B", "region_name": "Miền Bắc", "area": "Bắc"},
            {"region_code": "T", "region_name": "Miền Trung", "area": "Trung"},
            {"region_code": "N", "region_name": "Miền Nam", "area": "Nam"},
            {"region_code": "UK", "region_name": "Không xác định", "area": "Không xác định"},
        ]
        dim_df = pd.DataFrame(regions)
        return self._upsert_table(dim_df, "dim_region", conflict_cols=["region_code"])

    def _load_dim_school(
        self, admission_df: pd.DataFrame, school_df: pd.DataFrame = None
    ) -> int:
        """Load dim_school."""
        # Lấy danh sách trường từ dữ liệu điểm chuẩn
        schools = (
            admission_df[["school_code", "school_name"]]
            .drop_duplicates()
            .reset_index(drop=True)
        )

        # Merge với school info nếu có
        if school_df is not None and not school_df.empty:
            schools = schools.merge(
                school_df[["school_code", "school_name", "school_type", "province"]],
                on=["school_name"],
                how="left",
                suffixes=("", "_info"),
            )
            if "school_code_info" in schools.columns:
                schools["school_code"] = schools["school_code"].fillna(
                    schools["school_code_info"]
                )
                schools = schools.drop(columns=["school_code_info"])

        # Fill defaults
        if "school_type" not in schools.columns:
            schools["school_type"] = "Công lập"
        if "province" not in schools.columns:
            schools["province"] = None

        schools["school_type"] = schools["school_type"].fillna("Công lập")

        return self._upsert_table(schools, "dim_school", conflict_cols=["school_name"])

    def _load_dim_major(self, df: pd.DataFrame) -> int:
        """Load dim_major."""
        majors = (
            df[["major_code", "major_name", "major_group"]]
            .drop_duplicates(subset=["major_name"])
            .reset_index(drop=True)
        )
        majors["major_code"] = majors["major_code"].fillna("")
        majors["major_group"] = majors["major_group"].fillna("Khác")

        return self._upsert_table(majors, "dim_major", conflict_cols=["major_name"])

    def _load_dim_subject_group(self, df: pd.DataFrame) -> int:
        """Load dim_subject_group."""
        # Map tổ hợp → môn học
        subject_map = {
            "A00": ("Toán", "Vật lý", "Hóa học"),
            "A01": ("Toán", "Vật lý", "Tiếng Anh"),
            "B00": ("Toán", "Hóa học", "Sinh học"),
            "C00": ("Ngữ văn", "Lịch sử", "Địa lý"),
            "D01": ("Toán", "Ngữ văn", "Tiếng Anh"),
            "D07": ("Toán", "Hóa học", "Tiếng Anh"),
            "D08": ("Toán", "Sinh học", "Tiếng Anh"),
        }

        groups = df["subject_group"].dropna().unique()
        records = []
        for group in groups:
            subjects = subject_map.get(group, ("", "", ""))
            records.append({
                "group_code": group,
                "group_name": group,
                "subject_1": subjects[0] if len(subjects) > 0 else "",
                "subject_2": subjects[1] if len(subjects) > 1 else "",
                "subject_3": subjects[2] if len(subjects) > 2 else "",
            })

        dim_df = pd.DataFrame(records)
        return self._upsert_table(dim_df, "dim_subject_group", conflict_cols=["group_code"])

    # ================================================================
    # Load Fact Table
    # ================================================================

    def _load_fact_admission(self, df: pd.DataFrame) -> int:
        """
        Load fact_admission với FK lookup.
        Join với dimension tables để lấy surrogate keys.
        """
        logger.info("Loading fact_admission...")

        # Lấy surrogate keys từ dim tables
        with self.engine.connect() as conn:
            schools = pd.read_sql("SELECT school_key, school_name FROM dim_school", conn)
            majors = pd.read_sql("SELECT major_key, major_name FROM dim_major", conn)
            years = pd.read_sql("SELECT year_key, year FROM dim_year", conn)
            subject_groups = pd.read_sql(
                "SELECT subject_group_key, group_code FROM dim_subject_group", conn
            )

        # Merge để lấy FKs
        fact = df.merge(schools, on="school_name", how="left")
        fact = fact.merge(majors, on="major_name", how="left")
        fact = fact.merge(years, on="year", how="left")
        fact = fact.merge(
            subject_groups, left_on="subject_group", right_on="group_code", how="left"
        )

        # Chọn cột cho fact table
        fact_cols = {
            "school_key": "school_key",
            "major_key": "major_key",
            "year_key": "year_key",
            "subject_group_key": "subject_group_key",
            "admission_score": "admission_score",
            "quota": "quota",
            "admission_method": "admission_method",
            "delta_score": "delta_score",
            "competition_level": "competition_level",
        }

        fact_df = pd.DataFrame()
        for src_col, dest_col in fact_cols.items():
            if src_col in fact.columns:
                fact_df[dest_col] = fact[src_col]
            else:
                fact_df[dest_col] = None

        # Chỉ giữ records có đủ FK quan trọng
        fact_df = fact_df.dropna(subset=["school_key", "year_key"])

        count = self._insert_table(fact_df, "fact_admission")
        return count

    # ================================================================
    # Helpers
    # ================================================================

    def _upsert_table(
        self,
        df: pd.DataFrame,
        table_name: str,
        conflict_cols: list,
    ) -> int:
        """
        Insert hoặc update records (upsert).
        Sử dụng ON CONFLICT DO NOTHING để tránh duplicate.
        """
        if df.empty:
            logger.warning(f"{table_name}: không có dữ liệu")
            return 0

        try:
            df.to_sql(
                table_name,
                self.engine,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=self.BATCH_SIZE,
            )
            count = len(df)
            logger.info(f"  {table_name}: {count:,} records loaded")
            return count
        except Exception as e:
            # Nếu lỗi duplicate, thử insert từng batch
            logger.warning(f"  {table_name}: lỗi bulk insert ({e}), thử skip duplicates...")
            try:
                with self.engine.connect() as conn:
                    # Lấy records hiện có
                    existing = pd.read_sql(f"SELECT {', '.join(conflict_cols)} FROM {table_name}", conn)
                merged = df.merge(existing, on=conflict_cols, how="left", indicator=True)
                new_records = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])
                if not new_records.empty:
                    new_records.to_sql(table_name, self.engine, if_exists="append", index=False, chunksize=self.BATCH_SIZE)
                logger.info(f"  {table_name}: {len(new_records):,} new records inserted")
                return len(new_records)
            except Exception as e2:
                logger.error(f"  {table_name}: thất bại hoàn toàn: {e2}")
                return 0

    def _insert_table(self, df: pd.DataFrame, table_name: str) -> int:
        """Insert records vào table (append)."""
        if df.empty:
            return 0
        try:
            df.to_sql(
                table_name,
                self.engine,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=self.BATCH_SIZE,
            )
            logger.info(f"  {table_name}: {len(df):,} records inserted")
            return len(df)
        except Exception as e:
            logger.error(f"  {table_name}: lỗi insert: {e}")
            return 0

    def test_connection(self) -> bool:
        """Kiểm tra kết nối PostgreSQL."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"PostgreSQL version: {version}")
                return True
        except Exception as e:
            logger.error(f"Test connection thất bại: {e}")
            return False

    def close(self):
        """Đóng connection pool."""
        self.engine.dispose()
        logger.info("DB connection pool đóng.")

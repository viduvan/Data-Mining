"""
src/preprocessing/etl_pipeline.py
Pipeline ETL tích hợp end-to-end:
Raw CSV → Clean → Feature Engineering → Validate → PostgreSQL

Cách dùng:
    python -m src.preprocessing.etl_pipeline
    python -m src.preprocessing.etl_pipeline --skip-db
    python -m src.preprocessing.etl_pipeline --year 2023 2024
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
from loguru import logger

from .data_cleaner import DataCleaner
from .feature_engineering import FeatureEngineer
from .validators import DataValidator
from .db_loader import DBLoader


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

for d in [DATA_CLEANED_DIR, DATA_PROCESSED_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class ETLPipeline:
    """
    Pipeline ETL hoàn chỉnh:

    1. Load raw CSV
    2. DataCleaner → cleaned data
    3. FeatureEngineer → processed data (features thêm)
    4. DataValidator → kiểm tra chất lượng
    5. Export to CSV (cleaned/, processed/)
    6. DBLoader → load vào PostgreSQL (optional)

    Checkpoint: Lưu intermediate results để resume nếu lỗi
    """

    def __init__(
        self,
        raw_dir: Path = None,
        cleaned_dir: Path = None,
        processed_dir: Path = None,
        skip_db: bool = False,
    ):
        self.raw_dir = raw_dir or DATA_RAW_DIR
        self.cleaned_dir = cleaned_dir or DATA_CLEANED_DIR
        self.processed_dir = processed_dir or DATA_PROCESSED_DIR
        self.skip_db = skip_db

        self.cleaner = DataCleaner()
        self.engineer = FeatureEngineer()
        self.validator = DataValidator()

    def run(self, years: list = None) -> dict:
        """
        Chạy toàn bộ pipeline ETL.

        Args:
            years: Danh sách năm cần xử lý (None = tất cả)

        Returns:
            Dict thống kê kết quả
        """
        logger.info("=" * 60)
        logger.info("BẮT ĐẦU ETL PIPELINE")
        logger.info("=" * 60)

        result = {}

        # ─── Bước 1: Load raw data ────────────────────────────────
        logger.info("Bước 1: Load raw data...")
        raw_admission = self.cleaner.load_raw_files(self.raw_dir, years)
        raw_schools = self._load_school_info()

        if raw_admission.empty:
            logger.error("Không có dữ liệu raw. Dừng pipeline.")
            return {"error": "No raw data found"}

        result["raw_records"] = len(raw_admission)
        logger.success(f"  Loaded {len(raw_admission):,} records raw")

        # ─── Bước 2: Data Cleaning ────────────────────────────────
        logger.info("Bước 2: Data Cleaning...")
        cleaned = self.cleaner.clean_admission_data(raw_admission)
        cleaned_schools = self.cleaner.clean_school_info(raw_schools) if not raw_schools.empty else pd.DataFrame()

        result["cleaned_records"] = len(cleaned)

        # Export cleaned data
        cleaned_path = self.cleaned_dir / "admission_cleaned.csv"
        cleaned.to_csv(cleaned_path, index=False, encoding="utf-8-sig")
        logger.success(f"  Cleaned data → {cleaned_path}")

        # ─── Bước 3: Feature Engineering ─────────────────────────
        logger.info("Bước 3: Feature Engineering...")
        processed = self.engineer.engineer_features(cleaned)

        result["processed_records"] = len(processed)

        # Export processed data
        processed_path = self.processed_dir / "admission_processed.csv"
        processed.to_csv(processed_path, index=False, encoding="utf-8-sig")
        logger.success(f"  Processed data → {processed_path}")

        # ─── Bước 4: Validation ───────────────────────────────────
        logger.info("Bước 4: Data Validation...")
        validation = self.validator.validate_admission_data(processed)
        result["validation_passed"] = validation.is_valid
        result["validation_errors"] = len(validation.errors)
        result["validation_warnings"] = len(validation.warnings)

        if not validation.is_valid:
            logger.error("Validation FAILED! Kiểm tra lại dữ liệu trước khi load DB.")
            if not self.skip_db:
                logger.error("Dừng pipeline do validation thất bại.")
                return result

        # ─── Bước 5: Load vào PostgreSQL ─────────────────────────
        if not self.skip_db:
            logger.info("Bước 5: Load vào PostgreSQL...")
            try:
                loader = DBLoader()
                db_summary = loader.load_all(processed, cleaned_schools)
                result["db_load"] = db_summary
                loader.close()
                logger.success("  Load PostgreSQL thành công!")
            except Exception as e:
                logger.error(f"  Lỗi load PostgreSQL: {e}")
                result["db_error"] = str(e)
        else:
            logger.info("Bước 5: Bỏ qua load DB (--skip-db)")

        # ─── Tổng kết ─────────────────────────────────────────────
        logger.info("=" * 60)
        logger.info("KẾT QUẢ ETL PIPELINE")
        logger.info(f"  Raw records       : {result.get('raw_records', 0):,}")
        logger.info(f"  Cleaned records   : {result.get('cleaned_records', 0):,}")
        logger.info(f"  Processed records : {result.get('processed_records', 0):,}")
        logger.info(f"  Validation        : {'✅ PASS' if result.get('validation_passed') else '❌ FAIL'}")
        if "db_load" in result:
            logger.info(f"  PostgreSQL load   : ✅")
        logger.info("=" * 60)

        return result

    def _load_school_info(self) -> pd.DataFrame:
        """Load thông tin trường từ CSV."""
        school_file = self.raw_dir / "schools_info.csv"
        if school_file.exists():
            df = pd.read_csv(school_file, encoding="utf-8-sig")
            logger.info(f"  School info: {len(df)} trường")
            return df
        logger.warning("Không tìm thấy schools_info.csv")
        return pd.DataFrame()


def main():
    parser = argparse.ArgumentParser(description="ETL Pipeline — Vietnam Admission Data")
    parser.add_argument("--year", nargs="+", type=int, help="Năm cần xử lý")
    parser.add_argument("--skip-db", action="store_true", help="Bỏ qua bước load PostgreSQL")
    parser.add_argument("--raw-dir", type=str, help="Thư mục raw data")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir) if args.raw_dir else DATA_RAW_DIR

    pipeline = ETLPipeline(raw_dir=raw_dir, skip_db=args.skip_db)
    result = pipeline.run(years=args.year)

    if result.get("validation_passed") is False:
        sys.exit(1)


if __name__ == "__main__":
    main()

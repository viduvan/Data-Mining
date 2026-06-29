"""
src/crawler/admission_crawler.py
Crawler chính thu thập dữ liệu điểm chuẩn tuyển sinh 2020-2025

Các nguồn:
- thituyensinh.vn
- tuyensinh247.com
- Fallback: scrape từ bảng HTML tổng hợp

Output: data/raw/admission_YYYY.csv
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger
from tqdm import tqdm

from .base_crawler import BaseCrawler
from .config import (
    ADMISSION_SOURCES,
    TARGET_YEARS,
    DATA_RAW_DIR,
    ADMISSION_COLUMNS,
    OUTPUT_ENCODING,
    CHECKPOINT_ENABLED,
    CHECKPOINT_FILE,
)
from .utils import (
    normalize_school_name,
    normalize_major_name,
    normalize_subject_group,
    parse_admission_score,
    parse_quota,
    normalize_text,
    save_checkpoint,
    load_checkpoint,
    get_timestamp,
)


class AdmissionCrawler(BaseCrawler):
    """
    Crawler thu thập điểm chuẩn tuyển sinh đại học Việt Nam.

    Hỗ trợ nhiều nguồn với fallback tự động:
    1. Thử nguồn chính (thituyensinh.vn)
    2. Nếu thất bại → thử nguồn backup
    3. Lưu checkpoint để resume

    Ví dụ sử dụng:
        crawler = AdmissionCrawler()
        crawler.crawl_all_years()
        crawler.close()

    Hoặc dùng context manager:
        with AdmissionCrawler() as crawler:
            crawler.crawl_all_years()
    """

    def __init__(self, output_dir: Path = None, years: list = None):
        super().__init__(output_dir or DATA_RAW_DIR)
        self.years = years or TARGET_YEARS
        self.checkpoint = load_checkpoint(CHECKPOINT_FILE) if CHECKPOINT_ENABLED else {}

    # ================================================================
    # Phương thức chính
    # ================================================================

    def crawl(self, year: int) -> list:
        """
        Crawl điểm chuẩn cho một năm cụ thể.

        Args:
            year: Năm tuyển sinh (VD: 2023)

        Returns:
            List of dict records theo ADMISSION_COLUMNS schema
        """
        logger.info(f"Bắt đầu crawl năm {year}...")
        records = []

        # Thử từng nguồn theo thứ tự
        for source_name, source_config in ADMISSION_SOURCES.items():
            if not source_config.get("enabled", True):
                continue

            logger.info(f"  Thử nguồn: {source_name}")
            try:
                source_records = self._crawl_from_source(year, source_name, source_config)
                if source_records:
                    records.extend(source_records)
                    logger.success(
                        f"  ✓ {source_name}: {len(source_records)} records cho năm {year}"
                    )
                    break  # Dừng nếu nguồn đầu tiên thành công
            except Exception as e:
                logger.warning(f"  ✗ {source_name} thất bại: {e}. Thử nguồn tiếp theo...")

        if not records:
            logger.error(f"Không crawl được dữ liệu cho năm {year} từ tất cả nguồn.")

        return records

    def crawl_all_years(self) -> dict:
        """
        Crawl điểm chuẩn cho tất cả năm trong TARGET_YEARS.

        Returns:
            Dict {year: number_of_records}
        """
        summary = {}

        for year in tqdm(self.years, desc="Crawling years"):
            # Bỏ qua nếu đã có checkpoint
            checkpoint_key = f"admission_{year}"
            if self.checkpoint.get(checkpoint_key, {}).get("completed"):
                logger.info(f"Bỏ qua năm {year} (đã có checkpoint)")
                summary[year] = self.checkpoint[checkpoint_key]["count"]
                continue

            records = self.crawl(year)

            if records:
                output_file = self.save(records, f"admission_{year}.csv")
                summary[year] = len(records)
                logger.success(f"Năm {year}: Đã lưu {len(records)} records → {output_file}")

                # Lưu checkpoint
                if CHECKPOINT_ENABLED:
                    self.checkpoint[checkpoint_key] = {
                        "completed": True,
                        "count": len(records),
                        "file": str(output_file),
                        "timestamp": get_timestamp(),
                    }
                    save_checkpoint(CHECKPOINT_FILE, self.checkpoint)
            else:
                summary[year] = 0
                logger.warning(f"Năm {year}: Không có dữ liệu")

        self._print_summary(summary)
        return summary

    # ================================================================
    # Các nguồn crawl cụ thể
    # ================================================================

    def _crawl_from_source(
        self, year: int, source_name: str, source_config: dict
    ) -> list:
        """Dispatcher: điều hướng đến method crawl phù hợp với từng nguồn."""
        method_name = f"_crawl_{source_name}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(year, source_config)
        else:
            logger.debug(f"Không có method {method_name}, dùng generic crawler")
            return self._crawl_generic_table(year, source_config)

    def _crawl_thituyensinh(self, year: int, config: dict) -> list:
        """
        Crawl từ thituyensinh.vn
        URL pattern: https://thituyensinh.vn/diem-chuan-{year}
        """
        url = f"{config['base_url']}/diem-chuan-{year}"
        html = self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_html(html)
        if not soup:
            return []

        return self._parse_admission_table(soup, year, url)

    def _crawl_tuyensinh247(self, year: int, config: dict) -> list:
        """
        Crawl từ tuyensinh247.com
        URL pattern: https://tuyensinh247.com/diem-chuan-{year}.html
        """
        url = f"{config['base_url']}/diem-chuan-{year}.html"
        html = self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_html(html)
        if not soup:
            return []

        return self._parse_admission_table(soup, year, url)

    def _crawl_generic_table(self, year: int, config: dict) -> list:
        """Generic crawler: tìm bảng HTML điểm chuẩn trên trang."""
        url = config.get("admission_url", config.get("base_url"))
        html = self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_html(html)
        if not soup:
            return []

        return self._parse_admission_table(soup, year, url)

    # ================================================================
    # HTML Parsing
    # ================================================================

    def _parse_admission_table(
        self, soup, year: int, source_url: str
    ) -> list:
        """
        Parse bảng điểm chuẩn từ HTML.
        Thử nhiều cấu trúc bảng phổ biến.

        Returns:
            List of dict records
        """
        records = []

        # Tìm tất cả bảng có thể chứa điểm chuẩn
        tables = soup.find_all("table")
        if not tables:
            # Thử tìm div/section chứa dữ liệu dạng list
            records = self._parse_list_format(soup, year, source_url)
        else:
            for table in tables:
                table_records = self._parse_html_table(table, year, source_url)
                records.extend(table_records)

        return records

    def _parse_html_table(self, table, year: int, source_url: str) -> list:
        """Parse một bảng HTML thành danh sách records."""
        records = []
        rows = table.find_all("tr")

        if len(rows) < 2:
            return []

        # Xác định header row
        header_row = rows[0]
        headers = [th.get_text(strip=True).lower() for th in header_row.find_all(["th", "td"])]

        # Mapping cột linh hoạt
        col_map = self._detect_column_mapping(headers)
        if not col_map:
            return []

        # Parse data rows
        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            if not cells:
                continue

            try:
                record = self._extract_row_data(cells, col_map, year, source_url)
                if record and record.get("admission_score") is not None:
                    records.append(record)
            except Exception as e:
                logger.debug(f"Bỏ qua row lỗi: {e}")

        return records

    def _parse_list_format(self, soup, year: int, source_url: str) -> list:
        """Parse dữ liệu dạng list/card thay vì table."""
        records = []
        # Tìm pattern phổ biến: div.school-item, article.admission-entry...
        selectors = [
            ".school-item", ".admission-item", ".diem-chuan-item",
            "article.entry", ".result-row",
        ]
        for selector in selectors:
            items = soup.select(selector)
            if items:
                logger.debug(f"Tìm thấy {len(items)} items với selector '{selector}'")
                # Parse từng item (cần customize theo cấu trúc thực tế)
                break

        return records

    def _detect_column_mapping(self, headers: list) -> dict:
        """
        Tự động nhận diện mapping cột từ header names.

        Returns:
            Dict {field_name: column_index} hoặc {} nếu không nhận diện được
        """
        col_map = {}

        patterns = {
            "school_code": ["mã trường", "ma truong", "code"],
            "school_name": ["tên trường", "ten truong", "trường", "truong", "school"],
            "major_code": ["mã ngành", "ma nganh"],
            "major_name": ["tên ngành", "ten nganh", "ngành", "nganh", "major"],
            "subject_group": ["tổ hợp", "to hop", "khối", "khoi", "group"],
            "admission_score": ["điểm chuẩn", "diem chuan", "điểm", "diem", "score"],
            "quota": ["chỉ tiêu", "chi tieu", "quota"],
            "admission_method": ["phương thức", "phuong thuc", "method"],
        }

        for i, header in enumerate(headers):
            header_lower = header.lower().strip()
            for field, keywords in patterns.items():
                if field not in col_map:
                    if any(kw in header_lower for kw in keywords):
                        col_map[field] = i
                        break

        # Cần ít nhất trường tên trường và điểm chuẩn
        if "school_name" not in col_map or "admission_score" not in col_map:
            return {}

        return col_map

    def _extract_row_data(
        self, cells: list, col_map: dict, year: int, source_url: str
    ) -> Optional[dict]:
        """Extract dữ liệu từ một row HTML."""

        def get_cell_text(col_name: str) -> str:
            idx = col_map.get(col_name)
            if idx is not None and idx < len(cells):
                return cells[idx].get_text(strip=True)
            return ""

        school_name = normalize_school_name(get_cell_text("school_name"))
        if not school_name:
            return None

        record = {
            "school_code": normalize_text(get_cell_text("school_code")),
            "school_name": school_name,
            "major_code": normalize_text(get_cell_text("major_code")),
            "major_name": normalize_major_name(get_cell_text("major_name")),
            "subject_group": normalize_subject_group(get_cell_text("subject_group")),
            "admission_score": parse_admission_score(get_cell_text("admission_score")),
            "quota": parse_quota(get_cell_text("quota")),
            "admission_method": normalize_text(get_cell_text("admission_method")) or "Xét điểm thi THPT",
            "year": year,
            "source_url": source_url,
            "crawled_at": get_timestamp(),
        }
        return record

    # ================================================================
    # Lưu dữ liệu
    # ================================================================

    def save(self, data: list, filename: str) -> Path:
        """
        Lưu dữ liệu vào CSV.

        Args:
            data: List of dict records
            filename: Tên file output (VD: admission_2023.csv)

        Returns:
            Path của file đã lưu
        """
        if not data:
            logger.warning(f"Không có dữ liệu để lưu vào {filename}")
            return None

        output_path = self.output_dir / filename
        df = pd.DataFrame(data, columns=ADMISSION_COLUMNS)

        # Đảm bảo đủ cột
        for col in ADMISSION_COLUMNS:
            if col not in df.columns:
                df[col] = None

        df = df[ADMISSION_COLUMNS]
        df.to_csv(output_path, index=False, encoding=OUTPUT_ENCODING)
        logger.info(f"Đã lưu {len(df)} records → {output_path}")
        return output_path

    # ================================================================
    # Reporting
    # ================================================================

    def _print_summary(self, summary: dict) -> None:
        """In tóm tắt kết quả crawl."""
        total = sum(summary.values())
        logger.info("=" * 50)
        logger.info("KẾT QUẢ CRAWL ĐIỂM CHUẨN")
        logger.info("=" * 50)
        for year, count in sorted(summary.items()):
            status = "✓" if count > 0 else "✗"
            logger.info(f"  {status} Năm {year}: {count:,} records")
        logger.info(f"  TỔNG: {total:,} records")
        logger.info("=" * 50)

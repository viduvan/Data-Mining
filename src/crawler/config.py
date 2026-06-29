"""
src/crawler/config.py
Cấu hình cho toàn bộ crawler — URLs, headers, rate limiting, paths
"""

import os
from pathlib import Path

# ================================================================
# Đường dẫn thư mục
# ================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

# ================================================================
# Nguồn dữ liệu tuyển sinh
# Mỗi entry là: (tên nguồn, URL mẫu, ghi chú)
# ================================================================
ADMISSION_SOURCES = {
    # Điểm chuẩn tổng hợp từ các trang tuyển sinh lớn
    "thituyensinh": {
        "base_url": "https://thituyensinh.vn",
        "admission_url": "https://thituyensinh.vn/diem-chuan",
        "description": "Tổng hợp điểm chuẩn nhiều trường",
        "enabled": True,
    },
    "tuyensinh247": {
        "base_url": "https://tuyensinh247.com",
        "admission_url": "https://tuyensinh247.com/diem-chuan.html",
        "description": "Điểm chuẩn các trường đại học",
        "enabled": True,
    },
    "diemthi_edu": {
        "base_url": "https://diemthi.hcm.edu.vn",
        "admission_url": "https://diemthi.hcm.edu.vn/diem-chuan",
        "description": "Điểm thi, điểm chuẩn TP.HCM",
        "enabled": True,
    },
    # Nguồn dữ liệu mở / backup
    "vnexpress": {
        "base_url": "https://vnexpress.net",
        "admission_url": "https://vnexpress.net/giao-duc/tuyen-sinh",
        "description": "Tổng hợp điểm chuẩn trên báo VNExpress",
        "enabled": False,  # Dùng khi nguồn chính không khả dụng
    },
}

# ================================================================
# Danh sách năm cần crawl
# ================================================================
TARGET_YEARS = list(range(2020, 2026))  # 2020, 2021, 2022, 2023, 2024, 2025

# ================================================================
# HTTP Headers — giả lập trình duyệt thật
# ================================================================
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Danh sách User-Agent để rotation
USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
]

# ================================================================
# Rate Limiting & Retry
# ================================================================
CRAWL_DELAY_SECONDS = float(os.getenv("CRAWL_DELAY", "1.5"))      # Delay giữa mỗi request
CRAWL_MAX_RETRIES = int(os.getenv("CRAWL_MAX_RETRIES", "3"))       # Số lần retry tối đa
CRAWL_TIMEOUT_SECONDS = int(os.getenv("CRAWL_TIMEOUT", "30"))      # Timeout mỗi request
CRAWL_BACKOFF_FACTOR = 2.0                                          # Exponential backoff factor

# ================================================================
# Selenium Settings (cho trang JavaScript-rendered)
# ================================================================
SELENIUM_HEADLESS = True        # Chạy Chrome không hiện giao diện
SELENIUM_PAGE_LOAD_TIMEOUT = 30
SELENIUM_IMPLICIT_WAIT = 10

# ================================================================
# Output Settings
# ================================================================
OUTPUT_ENCODING = "utf-8-sig"       # UTF-8 with BOM (cho Excel đọc đúng tiếng Việt)
CHECKPOINT_ENABLED = True           # Lưu checkpoint để resume nếu bị ngắt
CHECKPOINT_FILE = DATA_RAW_DIR / ".crawl_checkpoint.json"

# ================================================================
# Column schema cho output CSV
# ================================================================
ADMISSION_COLUMNS = [
    "school_code",
    "school_name",
    "major_code",
    "major_name",
    "subject_group",
    "admission_score",
    "quota",
    "admission_method",
    "year",
    "source_url",
    "crawled_at",
]

SCHOOL_INFO_COLUMNS = [
    "school_code",
    "school_name",
    "school_type",       # Công lập / Tư thục / Nước ngoài
    "region",            # Bắc / Trung / Nam
    "province",          # Tỉnh/thành phố
    "website",
    "phone",
    "email",
    "established_year",
]

# ================================================================
# Logging
# ================================================================
LOG_LEVEL = "INFO"
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)
LOG_FILE = PROJECT_ROOT / "logs" / "crawler.log"

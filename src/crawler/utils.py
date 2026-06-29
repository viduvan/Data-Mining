"""
src/crawler/utils.py
Hàm tiện ích cho crawler — text normalization, number parsing, file I/O
"""

import re
import json
import time
import random
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import requests
from loguru import logger

from .config import USER_AGENTS, CRAWL_DELAY_SECONDS


# ================================================================
# Text Normalization
# ================================================================

def normalize_text(text: str) -> str:
    """Chuẩn hóa chuỗi: strip, collapse spaces, unicode NFC."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", str(text))
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_school_name(name: str) -> str:
    """
    Chuẩn hóa tên trường đại học:
    - Viết hoa chữ đầu mỗi từ quan trọng
    - Chuẩn hóa viết tắt phổ biến
    """
    if not name:
        return ""

    name = normalize_text(name)

    # Chuẩn hóa các viết tắt phổ biến
    abbreviation_map = {
        r"\bĐH\b": "Đại học",
        r"\bTrường ĐH\b": "Trường Đại học",
        r"\bHV\b": "Học viện",
        r"\bCĐ\b": "Cao đẳng",
        r"\bTP\.?HCM\b": "TP.HCM",
        r"\bTP Hồ Chí Minh\b": "TP.HCM",
        r"\bHà Nội\b": "Hà Nội",
    }

    for pattern, replacement in abbreviation_map.items():
        name = re.sub(pattern, replacement, name, flags=re.IGNORECASE)

    return name.strip()


def normalize_major_name(name: str) -> str:
    """Chuẩn hóa tên ngành học."""
    if not name:
        return ""
    name = normalize_text(name)
    # Loại bỏ mã ngành ở đầu nếu có (VD: "7480201 - Công nghệ thông tin")
    name = re.sub(r"^\d{7}\s*[-–]\s*", "", name)
    return name.strip()


def normalize_subject_group(group: str) -> str:
    """Chuẩn hóa tổ hợp xét tuyển (VD: a00, A 00 → A00)."""
    if not group:
        return ""
    group = normalize_text(group)
    # Loại bỏ khoảng trắng, viết hoa
    group = re.sub(r"\s+", "", group).upper()
    # Chuẩn hóa format: chữ + 2 số (A00, D01, C00...)
    match = re.match(r"([A-Z])(\d{2})", group)
    if match:
        return f"{match.group(1)}{match.group(2)}"
    return group


# ================================================================
# Number Parsing
# ================================================================

def parse_admission_score(score_str: str) -> Optional[float]:
    """
    Parse điểm chuẩn từ chuỗi.
    Xử lý các format: "25.0", "25,0", "25", "25.00", "N/A", ""
    """
    if not score_str or str(score_str).strip().upper() in ("N/A", "KHÔNG XÉT", "-", ""):
        return None

    score_str = str(score_str).strip()
    # Kiểm tra số âm ngay từ đầu
    if score_str.startswith("-"):
        return None
    # Thay dấu phẩy → dấu chấm
    score_str = score_str.replace(",", ".")
    # Lấy số đầu tiên tìm thấy
    match = re.search(r"\d+\.?\d*", score_str)
    if match:
        value = float(match.group())
        # Validate: điểm chuẩn hợp lệ 0–30
        if 0 <= value <= 30:
            return value
    return None


def parse_quota(quota_str: str) -> Optional[int]:
    """Parse chỉ tiêu tuyển sinh từ chuỗi."""
    if not quota_str or str(quota_str).strip() in ("N/A", "-", ""):
        return None

    quota_str = str(quota_str).strip()
    # Loại bỏ dấu chấm ngăn cách hàng nghìn (VD: "1.200" → "1200")
    quota_str = quota_str.replace(".", "")
    match = re.search(r"\d+", quota_str)
    if match:
        value = int(match.group())
        if 0 < value < 100000:  # Validate: chỉ tiêu hợp lý
            return value
    return None


# ================================================================
# HTTP Utilities
# ================================================================

def get_random_user_agent() -> str:
    """Trả về User-Agent ngẫu nhiên từ danh sách."""
    return random.choice(USER_AGENTS)


def make_session() -> requests.Session:
    """Tạo requests.Session với headers mặc định."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
        "Connection": "keep-alive",
    })
    return session


def random_delay(base: float = None) -> None:
    """Thêm delay ngẫu nhiên (base ± 30%) giữa các request."""
    if base is None:
        base = CRAWL_DELAY_SECONDS
    delay = base * (0.7 + random.random() * 0.6)
    time.sleep(delay)


# ================================================================
# Checkpoint (Resume khi bị ngắt)
# ================================================================

def save_checkpoint(checkpoint_file: Path, data: dict) -> None:
    """Lưu trạng thái crawl vào file JSON."""
    checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
    with open(checkpoint_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    logger.debug(f"Checkpoint saved: {checkpoint_file}")


def load_checkpoint(checkpoint_file: Path) -> dict:
    """Load trạng thái crawl từ file JSON."""
    if not checkpoint_file.exists():
        return {}
    try:
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Checkpoint loaded: {checkpoint_file}")
        return data
    except Exception as e:
        logger.warning(f"Không thể load checkpoint: {e}")
        return {}


# ================================================================
# File I/O
# ================================================================

def get_timestamp() -> str:
    """Trả về timestamp hiện tại dạng string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_dir(path: Union[str, Path]) -> Path:
    """Tạo thư mục nếu chưa tồn tại."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def clean_filename(name: str) -> str:
    """Làm sạch tên file: loại bỏ ký tự đặc biệt."""
    name = unicodedata.normalize("NFC", name)
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    return name.strip()

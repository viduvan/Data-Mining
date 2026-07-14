"""
constants.py — Hằng số toàn cục cho admission-crawler.
"""

from __future__ import annotations

# ── Versioning ────────────────────────────────────────────────────────────────
PARSER_VERSION = "v0.1.0"
APP_VERSION = "0.1.0"

# ── Target domain ─────────────────────────────────────────────────────────────
BASE_URL = "https://vietnamnet.vn"
ALLOWED_DOMAIN = "vietnamnet.vn"
ROBOTS_URL = "https://vietnamnet.vn/robots.txt"
INDEX_PATH_TEMPLATE = "/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-{year}"

# ── Scope ─────────────────────────────────────────────────────────────────────
PROVINCE_FILTER = "Hà Nội"
YEARS = list(range(2016, 2026))  # 2016 → 2025 inclusive

# ── Page sizes (observed) ─────────────────────────────────────────────────────
INDEX_PAGE_SIZE = 20       # trường mỗi trang index
MAJOR_PAGE_SIZE = 20       # ngành mỗi trang detail

# ── URL Page statuses ─────────────────────────────────────────────────────────
class PageStatus:
    DISCOVERED = "DISCOVERED"
    QUEUED = "QUEUED"
    FETCHING = "FETCHING"
    FETCHED = "FETCHED"
    PARSED = "PARSED"
    VALIDATED = "VALIDATED"
    COMPLETED = "COMPLETED"
    RETRY_PENDING = "RETRY_PENDING"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"

# ── Page types ────────────────────────────────────────────────────────────────
class PageType:
    ROBOTS = "ROBOTS"
    YEAR_INDEX = "YEAR_INDEX"
    UNIVERSITY_DETAIL = "UNIVERSITY_DETAIL"
    MAJOR_DETAIL = "MAJOR_DETAIL"

# ── Crawl run statuses ────────────────────────────────────────────────────────
class RunStatus:
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    STOPPED = "STOPPED"
    PAUSED = "PAUSED"

# ── HTTP headers ──────────────────────────────────────────────────────────────
DEFAULT_HEADERS = {
    "User-Agent": (
        "UniversityCutoffResearchBot/1.0 "
        "(+contact: research@example.com; educational research)"
    ),
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Cache-Control": "no-cache",
}

# ── Retry statuses ────────────────────────────────────────────────────────────
RETRY_STATUSES = {408, 425, 500, 502, 503, 504}
STOP_ON_STATUS = {403}
SKIP_ON_STATUS = {404, 410}

# ── Score ─────────────────────────────────────────────────────────────────────
SCORE_MIN = 0
SCORE_MAX = 2000   # không giới hạn ở 30 — có thể là thang 1500
VALID_SCORE_SCALES = {"30", "40", "100", "150", "1200", "1500", "unknown"}

# ── Table header aliases ──────────────────────────────────────────────────────
# Dùng để nhận diện bảng theo header, không theo CSS class
INDEX_TABLE_HEADERS = {
    "stt": {"stt", "số thứ tự", "no"},
    "university": {"trường", "tên trường", "trường/cơ sở đào tạo"},
    "university_code": {"mã trường", "mã"},
    "province": {"tỉnh thành", "tỉnh/thành", "tỉnh thành phố"},
}

DETAIL_TABLE_HEADERS = {
    "stt": {"stt", "số thứ tự"},
    "major": {"ngành", "tên ngành", "ngành/chương trình"},
    "score": {"điểm chuẩn", "điểm", "điểm trúng tuyển"},
    "level": {"hệ", "loại hình", "hệ đào tạo"},
    "subject_group": {"khối thi", "tổ hợp", "khối", "tổ hợp xét tuyển"},
    "note": {"ghi chú", "chú thích"},
}

# ── Admission method keywords ─────────────────────────────────────────────────
METHOD_KEYWORDS = {
    "thpt_exam": [
        "điểm thi thpt",
        "thi tốt nghiệp thpt",
        "kết quả thi thpt",
        "xét duyệt điểm thi thpt",
        "xét kết quả thi thpt",
        "điểm tốt nghiệp",
    ],
    "transcript": [
        "học bạ",
        "kết quả học tập",
        "xét học bạ",
    ],
    "competency_test": [
        "đánh giá năng lực",
        "đgnl",
        "hsa",
        "năng lực",
    ],
    "thinking_assessment": [
        "đánh giá tư duy",
        "đgtd",
        "tsa",
        "tư duy",
    ],
    "direct_admission": [
        "tuyển thẳng",
        "xét tuyển thẳng",
        "thẳng",
    ],
    "combined": [
        "kết hợp",
        "nhiều phương thức",
    ],
}

# ── Subject combination regex ─────────────────────────────────────────────────
SUBJECT_COMBO_PATTERN = r"\b[A-Z]\d{2}\b"  # A00, D01, C00, v.v.

# ── Program type keywords ──────────────────────────────────────────────────────
PROGRAM_TYPE_KEYWORDS = {
    "international_cooperation": [
        "việt - nhật",
        "việt nhật",
        "việt - pháp",
        "việt pháp",
        "việt - anh",
        "việt anh",
        "liên kết quốc tế",
    ],
    "advanced": [
        "tiên tiến",
        "ct tiên tiến",
        "chương trình tiên tiến",
    ],
    "high_quality": [
        "chất lượng cao",
        "clc",
    ],
    "english_taught": [
        "dạy bằng tiếng anh",
        "giảng dạy bằng tiếng anh",
        "tiếng anh",
    ],
    "talent": [
        "tài năng",
        "cử nhân tài năng",
    ],
}

# ── Cache TTL (ngày) ──────────────────────────────────────────────────────────
CACHE_TTL_DAYS = {
    "2016-2023": 365,
    "2024": 180,
    "2025": 30,
}

def get_cache_ttl_days(year: int) -> int:
    if year <= 2023:
        return 365
    elif year == 2024:
        return 180
    else:
        return 30

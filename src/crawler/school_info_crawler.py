"""
src/crawler/school_info_crawler.py
Crawler thu thập thông tin trường đại học Việt Nam

Output: data/raw/schools_info.csv
"""

from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger
from tqdm import tqdm

from .base_crawler import BaseCrawler
from .config import DATA_RAW_DIR, SCHOOL_INFO_COLUMNS, OUTPUT_ENCODING
from .utils import normalize_text, normalize_school_name, get_timestamp


# Danh sách khu vực/tỉnh thành của Việt Nam
REGION_MAPPING = {
    # Miền Bắc
    "Hà Nội": "Bắc",
    "Hải Phòng": "Bắc",
    "Hải Dương": "Bắc",
    "Quảng Ninh": "Bắc",
    "Thái Nguyên": "Bắc",
    "Nam Định": "Bắc",
    "Bắc Giang": "Bắc",
    "Vĩnh Phúc": "Bắc",
    "Hưng Yên": "Bắc",
    "Bắc Ninh": "Bắc",
    # Miền Trung
    "Đà Nẵng": "Trung",
    "Huế": "Trung",
    "Thừa Thiên Huế": "Trung",
    "Quảng Nam": "Trung",
    "Quảng Ngãi": "Trung",
    "Bình Định": "Trung",
    "Khánh Hòa": "Trung",
    "Nghệ An": "Trung",
    "Thanh Hóa": "Trung",
    # Miền Nam
    "TP.HCM": "Nam",
    "Hồ Chí Minh": "Nam",
    "Cần Thơ": "Nam",
    "Đồng Nai": "Nam",
    "Bình Dương": "Nam",
    "Long An": "Nam",
    "An Giang": "Nam",
    "Đà Lạt": "Nam",
    "Lâm Đồng": "Nam",
    "Tiền Giang": "Nam",
}


# Danh sách mẫu trường đại học (dùng khi không crawl được)
# Đây là dữ liệu seed cơ bản để hệ thống hoạt động
SEED_SCHOOLS = [
    # Miền Bắc
    {"school_code": "QSX", "school_name": "Đại học Quốc gia Hà Nội", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "BKH", "school_name": "Đại học Bách khoa Hà Nội", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "NEU", "school_name": "Đại học Kinh tế Quốc dân", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "FTU", "school_name": "Đại học Ngoại thương", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "HMU", "school_name": "Đại học Y Hà Nội", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "HAN", "school_name": "Học viện Ngoại giao", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "AOF", "school_name": "Học viện Tài chính", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "BAH", "school_name": "Học viện Ngân hàng", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "TMU", "school_name": "Đại học Thương mại", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "HLU", "school_name": "Đại học Luật Hà Nội", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "UET", "school_name": "Trường Đại học Công nghệ - ĐHQGHN", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "ULIS", "school_name": "Trường Đại học Ngoại ngữ - ĐHQGHN", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "UEL_HN", "school_name": "Trường Đại học Kinh tế - ĐHQGHN", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "UTC", "school_name": "Đại học Giao thông Vận tải", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "NUCE", "school_name": "Đại học Xây dựng Hà Nội", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "HAU", "school_name": "Đại học Kiến trúc Hà Nội", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "HUP", "school_name": "Đại học Dược Hà Nội", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "AJC", "school_name": "Học viện Báo chí và Tuyên truyền", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "VNUA", "school_name": "Học viện Nông nghiệp Việt Nam", "school_type": "Công lập", "province": "Hà Nội"},
    {"school_code": "TNU", "school_name": "Đại học Thái Nguyên", "school_type": "Công lập", "province": "Thái Nguyên"},
    {"school_code": "HHU", "school_name": "Đại học Hàng hải Việt Nam", "school_type": "Công lập", "province": "Hải Phòng"},
    
    # Miền Trung
    {"school_code": "DUT", "school_name": "Trường Đại học Bách khoa - ĐH Đà Nẵng", "school_type": "Công lập", "province": "Đà Nẵng"},
    {"school_code": "DUE", "school_name": "Trường Đại học Kinh tế - ĐH Đà Nẵng", "school_type": "Công lập", "province": "Đà Nẵng"},
    {"school_code": "UED", "school_name": "Trường Đại học Sư phạm - ĐH Đà Nẵng", "school_type": "Công lập", "province": "Đà Nẵng"},
    {"school_code": "UFL", "school_name": "Trường Đại học Ngoại ngữ - ĐH Đà Nẵng", "school_type": "Công lập", "province": "Đà Nẵng"},
    {"school_code": "HCE", "school_name": "Trường Đại học Kinh tế - Đại học Huế", "school_type": "Công lập", "province": "Thừa Thiên Huế"},
    {"school_code": "HUP_H", "school_name": "Trường Đại học Y Dược - Đại học Huế", "school_type": "Công lập", "province": "Thừa Thiên Huế"},
    {"school_code": "VNU", "school_name": "Đại học Vinh", "school_type": "Công lập", "province": "Nghệ An"},
    {"school_code": "QNU", "school_name": "Đại học Quy Nhơn", "school_type": "Công lập", "province": "Bình Định"},
    {"school_code": "NTU", "school_name": "Đại học Nha Trang", "school_type": "Công lập", "province": "Khánh Hòa"},
    {"school_code": "DLU", "school_name": "Đại học Đà Lạt", "school_type": "Công lập", "province": "Lâm Đồng"},
    {"school_code": "FLA", "school_name": "Phân hiệu ĐHQG-HCM tại Quảng Ngãi", "school_type": "Công lập", "province": "Quảng Ngãi"},
    
    # Miền Nam
    {"school_code": "QSB", "school_name": "Đại học Quốc gia TP.HCM", "school_type": "Công lập", "province": "TP.HCM"},
    {"school_code": "BKS", "school_name": "Trường Đại học Bách khoa - ĐHQG-HCM", "school_type": "Công lập", "province": "TP.HCM"},
    {"school_code": "USSH", "school_name": "Trường Đại học KHXH&NV - ĐHQG-HCM", "school_type": "Công lập", "province": "TP.HCM"},
    {"school_code": "HCMUS", "school_name": "Trường Đại học Khoa học Tự nhiên - ĐHQG-HCM", "school_type": "Công lập", "province": "TP.HCM"},
    {"school_code": "UEL", "school_name": "Trường Đại học Kinh tế - Luật - ĐHQG-HCM", "school_type": "Công lập", "province": "TP.HCM"},
    {"school_code": "UIT", "school_name": "Trường Đại học Công nghệ Thông tin - ĐHQG-HCM", "school_type": "Công lập", "province": "TP.HCM"},
    {"school_code": "UEH", "school_name": "Đại học Kinh tế TP.HCM", "school_type": "Công lập", "province": "TP.HCM"},
    {"school_code": "UMP", "school_name": "Đại học Y Dược TP.HCM", "school_type": "Công lập", "province": "TP.HCM"},
    {"school_code": "UTE", "school_name": "Đại học Sư phạm Kỹ thuật TP.HCM", "school_type": "Công lập", "province": "TP.HCM"},
    {"school_code": "SGU", "school_name": "Đại học Sài Gòn", "school_type": "Công lập", "province": "TP.HCM"},
    {"school_code": "OU", "school_name": "Đại học Mở TP.HCM", "school_type": "Công lập", "province": "TP.HCM"},
    {"school_code": "NLU", "school_name": "Đại học Nông Lâm TP.HCM", "school_type": "Công lập", "province": "TP.HCM"},
    {"school_code": "TDTU", "school_name": "Đại học Tôn Đức Thắng", "school_type": "Công lập", "province": "TP.HCM"},
    {"school_code": "CTU", "school_name": "Đại học Cần Thơ", "school_type": "Công lập", "province": "Cần Thơ"},
    {"school_code": "TGU", "school_name": "Đại học Tiền Giang", "school_type": "Công lập", "province": "Tiền Giang"},
    {"school_code": "AGU", "school_name": "Đại học An Giang", "school_type": "Công lập", "province": "An Giang"},
    {"school_code": "BDU", "school_name": "Đại học Bình Dương", "school_type": "Tư thục", "province": "Bình Dương"},
    {"school_code": "DNU", "school_name": "Đại học Đồng Nai", "school_type": "Công lập", "province": "Đồng Nai"},
    
    # Tư thục & Nước ngoài nổi tiếng
    {"school_code": "RMIT", "school_name": "Đại học RMIT Việt Nam", "school_type": "Nước ngoài", "province": "TP.HCM"},
    {"school_code": "FPT", "school_name": "Đại học FPT", "school_type": "Tư thục", "province": "Hà Nội"},
    {"school_code": "FUV", "school_name": "Đại học Fulbright Việt Nam", "school_type": "Nước ngoài", "province": "TP.HCM"},
    {"school_code": "BUV", "school_name": "Đại học Anh quốc Việt Nam", "school_type": "Nước ngoài", "province": "Hưng Yên"},
    {"school_code": "VGU", "school_name": "Đại học Việt Đức", "school_type": "Công lập", "province": "Bình Dương"},
    {"school_code": "HUT", "school_name": "Đại học Công nghệ TP.HCM (HUTECH)", "school_type": "Tư thục", "province": "TP.HCM"},
    {"school_code": "UEF", "school_name": "Đại học Kinh tế - Tài chính TP.HCM", "school_type": "Tư thục", "province": "TP.HCM"},
    {"school_code": "VLU", "school_name": "Đại học Văn Lang", "school_type": "Tư thục", "province": "TP.HCM"},
    {"school_code": "LAC", "school_name": "Đại học Lạc Hồng", "school_type": "Tư thục", "province": "Đồng Nai"},
    {"school_code": "HIU", "school_name": "Đại học Quốc tế Hồng Bàng", "school_type": "Tư thục", "province": "TP.HCM"},
    {"school_code": "NTT", "school_name": "Đại học Nguyễn Tất Thành", "school_type": "Tư thục", "province": "TP.HCM"},
    {"school_code": "HUP_T", "school_name": "Đại học Phan Châu Trinh", "school_type": "Tư thục", "province": "Quảng Nam"},
]


class SchoolInfoCrawler(BaseCrawler):
    """
    Crawler thu thập thông tin trường đại học:
    - Tên trường, mã trường
    - Loại hình (công lập / tư thục / nước ngoài)
    - Khu vực (Bắc / Trung / Nam), tỉnh/thành
    - Website, liên hệ

    Fallback: Dùng seed data nếu không crawl được
    """

    def __init__(self, output_dir: Path = None):
        super().__init__(output_dir or DATA_RAW_DIR)

    def crawl(self, use_seed: bool = False) -> list:
        """
        Crawl thông tin trường đại học.

        Args:
            use_seed: True = dùng seed data (không crawl web)

        Returns:
            List of dict records
        """
        if use_seed:
            logger.info("Sử dụng seed data cho thông tin trường...")
            return self._get_seed_data()

        logger.info("Bắt đầu crawl thông tin trường...")
        records = []

        # Thử crawl từ web
        try:
            records = self._crawl_school_list()
        except Exception as e:
            logger.warning(f"Crawl web thất bại: {e}. Dùng seed data...")
            records = self._get_seed_data()

        if not records:
            logger.info("Không crawl được, dùng seed data...")
            records = self._get_seed_data()

        logger.success(f"Đã thu thập thông tin {len(records)} trường")
        return records

    def _crawl_school_list(self) -> list:
        """Crawl danh sách trường từ web."""
        records = []

        # URL tham khảo: danh sách trường theo Bộ GD&ĐT
        url = "https://thituyensinh.vn/truong-dai-hoc"
        html = self.fetch_page(url)
        if not html:
            return []

        soup = self.parse_html(html)
        if not soup:
            return []

        # Parse danh sách trường (cần điều chỉnh selector theo cấu trúc thực tế)
        school_items = soup.select(".school-item, .truong-item, article.school")
        for item in tqdm(school_items, desc="Parsing schools"):
            try:
                record = self._parse_school_item(item)
                if record:
                    records.append(record)
            except Exception as e:
                logger.debug(f"Bỏ qua trường lỗi: {e}")

        return records

    def _parse_school_item(self, item) -> Optional[dict]:
        """Parse thông tin một trường từ HTML element."""
        # Generic parser - cần customize theo cấu trúc thực tế
        name_el = item.select_one(".school-name, h2, h3, .name")
        if not name_el:
            return None

        name = normalize_school_name(name_el.get_text(strip=True))
        if not name:
            return None

        code_el = item.select_one(".school-code, .ma-truong")
        province_el = item.select_one(".province, .tinh-thanh, .dia-chi")

        province = normalize_text(province_el.get_text(strip=True)) if province_el else ""
        region = self._get_region(province)

        return {
            "school_code": normalize_text(code_el.get_text(strip=True)) if code_el else "",
            "school_name": name,
            "school_type": self._detect_school_type(name),
            "region": region,
            "province": province,
            "website": "",
            "phone": "",
            "email": "",
            "established_year": None,
        }

    def _get_seed_data(self) -> list:
        """Trả về dữ liệu seed với thông tin mẫu."""
        records = []
        for school in SEED_SCHOOLS:
            province = school.get("province", "")
            region = self._get_region(province)
            record = {
                "school_code": school.get("school_code", ""),
                "school_name": school.get("school_name", ""),
                "school_type": school.get("school_type", "Công lập"),
                "region": region,
                "province": province,
                "website": "",
                "phone": "",
                "email": "",
                "established_year": None,
            }
            records.append(record)
        return records

    def _get_region(self, province: str) -> str:
        """Xác định khu vực (Bắc/Trung/Nam) từ tỉnh/thành."""
        if not province:
            return ""
        for key, region in REGION_MAPPING.items():
            if key.lower() in province.lower() or province.lower() in key.lower():
                return region
        return ""

    def _detect_school_type(self, name: str) -> str:
        """Đoán loại hình trường từ tên."""
        name_lower = name.lower()
        if any(kw in name_lower for kw in ["tư thục", "dân lập", "quốc tế"]):
            return "Tư thục"
        elif any(kw in name_lower for kw in ["rmit", "bia", "biu", "troy"]):
            return "Nước ngoài"
        return "Công lập"

    def save(self, data: list, filename: str = "schools_info.csv") -> Path:
        """Lưu thông tin trường vào CSV."""
        if not data:
            return None

        output_path = self.output_dir / filename
        df = pd.DataFrame(data)

        for col in SCHOOL_INFO_COLUMNS:
            if col not in df.columns:
                df[col] = None

        df = df[SCHOOL_INFO_COLUMNS]
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logger.info(f"Đã lưu {len(df)} trường → {output_path}")
        return output_path

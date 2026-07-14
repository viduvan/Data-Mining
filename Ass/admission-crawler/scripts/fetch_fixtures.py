#!/usr/bin/env python3
"""
fetch_fixtures.py — Lấy HTML thật từ VietNamNet làm fixture cho unit test.
Chạy thủ công MỘT LẦN duy nhất, không dùng automation phức tạp, không phải là crawler run.
"""

import os
import sys
from pathlib import Path
import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}

FIXTURES = [
    {
        "url": "https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2025",
        "filename": "index_2025_page0.html"
    },
    {
        "url": "https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2025-page1",
        "filename": "index_2025_page1.html"
    },
    {
        "url": "https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2025/truong/dai-hoc-bach-khoa-ha-noi?keyword=BKA",
        "filename": "university_bka_2025_page0.html"
    },
    {
        "url": "https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-2024/truong/dai-hoc-bach-khoa-ha-noi?keyword=BKA",
        "filename": "university_bka_2024_page0.html"
    }
]

def main():
    base_dir = Path(__file__).resolve().parent.parent
    fixtures_dir = base_dir / "tests" / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    
    with httpx.Client(headers=HEADERS, timeout=30.0) as client:
        for item in FIXTURES:
            url = item["url"]
            filepath = fixtures_dir / item["filename"]
            
            if filepath.exists():
                print(f"Bỏ qua: {filepath.name} đã tồn tại.")
                continue
                
            print(f"Đang tải: {url}")
            try:
                response = client.get(url)
                response.raise_for_status()
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"Đã lưu: {filepath.name} ({len(response.text)} bytes)")
            except Exception as e:
                print(f"Lỗi khi tải {url}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

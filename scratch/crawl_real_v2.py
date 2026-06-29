"""
Crawler v2: Cào dữ liệu điểm chuẩn THẬT từ tuyensinh247.com
Trang này dùng Next.js SSR — bảng điểm chuẩn năm mới nhất (2025) có sẵn trong HTML tĩnh.
Bảng 1 (table đầu tiên) = Điểm chuẩn theo phương thức Điểm thi THPT.
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from pathlib import Path
from loguru import logger
from datetime import datetime

DATA_RAW_DIR = Path("/home/vietpv/Desktop/Data-Mining/data/raw")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_all_school_links():
    """Lấy danh sách link tất cả các trường từ trang chủ."""
    url = "https://diemthi.tuyensinh247.com/diem-chuan.html"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    
    schools = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/diem-chuan/") and href.endswith(".html"):
            match = re.search(r'-([A-Z0-9]+)\.html$', href)
            if match:
                code = match.group(1)
                name = a.get_text(strip=True)
                if code not in seen and name:
                    seen.add(code)
                    schools.append({
                        "code": code,
                        "name": name,
                        "url": f"https://diemthi.tuyensinh247.com{href}"
                    })
    logger.info(f"Tìm thấy {len(schools)} trường trên trang chủ.")
    return schools


def parse_thpt_table(school, soup, year):
    """Parse bảng điểm chuẩn THPT (bảng đầu tiên trên trang)."""
    tables = soup.find_all("table")
    if not tables:
        return []

    # Bảng 1 = Điểm chuẩn theo phương thức Điểm thi THPT
    table = tables[0]
    rows = table.find_all("tr")
    if len(rows) < 2:
        return []

    records = []
    for tr in rows[1:]:
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cells) < 3:
            continue

        major_name = cells[0]
        raw_groups = cells[1] if len(cells) > 1 else ""
        raw_score  = cells[2] if len(cells) > 2 else ""

        # Bỏ dòng quảng cáo
        if not major_name or "tra cứu" in major_name.lower() or "tuyensinh247" in major_name.lower():
            continue

        # Parse điểm
        score_match = re.search(r'(\d+[\.,]?\d*)', raw_score)
        if not score_match:
            continue
        score = float(score_match.group(1).replace(",", "."))
        if score < 10 or score > 30:
            continue

        # Parse tổ hợp (có thể nhiều tổ hợp cách nhau bởi ; )
        groups = re.findall(r'[A-D]\d{2}', raw_groups)
        if not groups:
            groups = ["A00"]

        for grp in groups:
            records.append({
                "school_code": school["code"],
                "school_name": school["name"],
                "major_code": "",
                "major_name": major_name,
                "subject_group": grp,
                "admission_score": score,
                "quota": 100,
                "admission_method": "Xét điểm thi THPT",
                "year": year,
                "source_url": school["url"],
                "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    return records


def crawl_school(school):
    """Crawl 1 trường, trả về danh sách records."""
    try:
        resp = requests.get(school["url"], headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Xác định năm hiện tại được hiển thị trên trang
        year = 2025  # mặc định
        for h3 in soup.find_all("h3"):
            txt = h3.get_text(strip=True)
            m = re.search(r'Điểm chuẩn.*Điểm thi THPT.*năm\s*(\d{4})', txt)
            if m:
                year = int(m.group(1))
                break

        records = parse_thpt_table(school, soup, year)
        return records
    except Exception as e:
        logger.error(f"Lỗi crawl {school['name']}: {e}")
        return []


def main():
    schools = get_all_school_links()
    if not schools:
        logger.error("Không lấy được danh sách trường!")
        return

    # Crawl TẤT CẢ các trường (không giới hạn)
    all_records = []
    for i, school in enumerate(schools):
        logger.info(f"[{i+1}/{len(schools)}] Crawl: {school['name']} ({school['code']})")
        records = crawl_school(school)
        if records:
            logger.success(f"  -> {len(records)} records")
            all_records.extend(records)
        else:
            logger.warning(f"  -> 0 records")
        time.sleep(0.3)

    if not all_records:
        logger.error("Không thu thập được dữ liệu nào!")
        return

    df = pd.DataFrame(all_records)
    logger.info(f"\nTỔNG CỘNG: {len(df)} records từ {df['school_code'].nunique()} trường")
    logger.info(f"Phân bố theo năm: {df['year'].value_counts().to_dict()}")

    # Lưu theo năm
    for year, df_y in df.groupby("year"):
        path = DATA_RAW_DIR / f"admission_{year}.csv"
        df_y.to_csv(path, index=False, encoding="utf-8-sig")
        logger.success(f"Lưu {len(df_y)} records → {path}")

    # Thống kê
    logger.info(f"\nThống kê chi tiết:")
    logger.info(f"  Số trường: {df['school_code'].nunique()}")
    logger.info(f"  Số ngành: {df['major_name'].nunique()}")
    logger.info(f"  Điểm TB: {df['admission_score'].mean():.2f}")
    logger.info(f"  Điểm Min: {df['admission_score'].min()}")
    logger.info(f"  Điểm Max: {df['admission_score'].max()}")


if __name__ == "__main__":
    main()

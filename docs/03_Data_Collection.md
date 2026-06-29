# 03_Data_Collection.md

# Thu thập Dữ liệu — Data Collection

---

## 1. Tổng quan

Giai đoạn này thu thập dữ liệu điểm chuẩn tuyển sinh đại học Việt Nam từ năm 2020 đến 2025 từ các nguồn web công khai.

**Kết quả đầu ra:** Các file CSV trong thư mục `data/raw/`

---

## 2. Nguồn Dữ liệu

### 2.1 Nguồn chính

| Nguồn | URL | Loại dữ liệu | Trạng thái |
|-------|-----|-------------|-----------|
| thituyensinh.vn | https://thituyensinh.vn/diem-chuan | Điểm chuẩn các trường | 🟢 Ưu tiên 1 |
| tuyensinh247.com | https://tuyensinh247.com/diem-chuan.html | Điểm chuẩn tổng hợp | 🟡 Fallback 1 |
| diemthi.hcm.edu.vn | https://diemthi.hcm.edu.vn/diem-chuan | Điểm chuẩn khu vực HCM | 🟡 Fallback 2 |

### 2.2 Nguồn bổ sung / Backup

| Nguồn | Ghi chú |
|-------|--------|
| VNExpress Giáo dục | Bảng tổng hợp điểm chuẩn hàng năm (dạng báo) |
| Tuổi Trẻ Online | Tổng hợp điểm chuẩn |
| web.archive.org | Backup cho dữ liệu năm 2020-2021 nếu trang gốc đã thay đổi |

### 2.3 Chiến lược Fallback

```
Thử nguồn 1 (thituyensinh.vn)
    │ Thất bại?
    ▼ Có
Thử nguồn 2 (tuyensinh247.com)
    │ Thất bại?
    ▼ Có
Thử nguồn 3 (diemthi.hcm.edu.vn)
    │ Thất bại?
    ▼ Có
Ghi log lỗi → tiếp tục năm khác
```

---

## 3. Thiết kế Crawler

### 3.1 Kiến trúc Class

```
BaseCrawler (Abstract)
├── fetch_page()          → Tải HTML (retry + rate limiting)
├── parse_html()          → BeautifulSoup parsing
├── close()               → Đóng session
├── crawl() [abstract]    → Subclass implement
└── save() [abstract]     → Subclass implement

AdmissionCrawler (kế thừa BaseCrawler)
├── crawl(year)           → Crawl điểm chuẩn 1 năm
├── crawl_all_years()     → Crawl 2020-2025
├── _crawl_thituyensinh() → Parser nguồn 1
├── _crawl_tuyensinh247() → Parser nguồn 2
├── _parse_html_table()   → Parse bảng HTML
└── save()                → Lưu CSV

SchoolInfoCrawler (kế thừa BaseCrawler)
├── crawl(use_seed)       → Crawl / dùng seed data
├── _get_seed_data()      → Dữ liệu mẫu (18+ trường)
└── save()                → Lưu CSV
```

### 3.2 Tính năng kỹ thuật

| Tính năng | Mô tả |
|-----------|-------|
| **Rate Limiting** | Delay 1.5 giây giữa mỗi request (± 30% ngẫu nhiên) |
| **Retry Logic** | Tối đa 3 lần, exponential backoff (2s → 4s → 8s) |
| **User-Agent Rotation** | Thay đổi mỗi 10 requests từ pool 5 User-Agents |
| **Session Management** | Dùng `requests.Session` để tái sử dụng TCP connection |
| **Checkpoint/Resume** | Lưu trạng thái vào `.crawl_checkpoint.json`, resume nếu bị ngắt |
| **Auto Column Detection** | Tự động nhận diện cột từ header bảng HTML |
| **Encoding** | UTF-8-sig (BOM) để Excel đọc đúng tiếng Việt |

---

## 4. Schema Dữ liệu Raw

### 4.1 admission_YYYY.csv

| Cột | Kiểu | Bắt buộc | Mô tả |
|-----|------|---------|-------|
| `school_code` | string | Không | Mã trường (do Bộ GD&ĐT cấp) |
| `school_name` | string | **Có** | Tên trường đầy đủ |
| `major_code` | string | Không | Mã ngành |
| `major_name` | string | Không | Tên ngành |
| `subject_group` | string | Không | Tổ hợp xét tuyển (A00, D01...) |
| `admission_score` | float | **Có** | Điểm chuẩn (0–30) |
| `quota` | int | Không | Chỉ tiêu tuyển sinh |
| `admission_method` | string | Không | Phương thức xét tuyển |
| `year` | int | **Có** | Năm tuyển sinh |
| `source_url` | string | Không | URL nguồn dữ liệu |
| `crawled_at` | string | Tự động | Thời gian crawl |

**Ví dụ dữ liệu raw:**

```csv
school_code,school_name,major_code,major_name,subject_group,admission_score,quota,admission_method,year,source_url,crawled_at
BKH,Đại học Bách khoa Hà Nội,7480201,Công nghệ thông tin,A00,27.04,200,Xét điểm thi THPT,2023,https://thituyensinh.vn/...,2024-01-01 10:00:00
```

### 4.2 schools_info.csv

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `school_code` | string | Mã trường |
| `school_name` | string | Tên trường đầy đủ |
| `school_type` | string | Công lập / Tư thục / Nước ngoài |
| `region` | string | Bắc / Trung / Nam |
| `province` | string | Tỉnh/thành phố |
| `website` | string | Website chính thức |
| `phone` | string | Số điện thoại |
| `email` | string | Email liên hệ |
| `established_year` | int | Năm thành lập |

---

## 5. Hướng dẫn Chạy Crawler

### 5.1 Cài đặt

```bash
# Kích hoạt môi trường ảo
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 5.2 Chạy crawler

```bash
# Crawl tất cả (thông tin trường + điểm chuẩn 2020-2025)
python -m src.crawler.run_crawler

# Crawl năm cụ thể
python -m src.crawler.run_crawler --year 2023

# Crawl nhiều năm
python -m src.crawler.run_crawler --year 2022 2023 2024

# Crawl với thông tin trường từ seed data (nhanh hơn, không cần web)
python -m src.crawler.run_crawler --use-seed-schools

# Chỉ crawl điểm chuẩn
python -m src.crawler.run_crawler --admission-only

# Verbose mode (xem chi tiết)
python -m src.crawler.run_crawler -v
```

### 5.3 Kiểm tra kết quả

```bash
# Xem danh sách files raw
ls -la data/raw/

# Kiểm tra số dòng
wc -l data/raw/admission_*.csv

# Xem mẫu dữ liệu
head -5 data/raw/admission_2023.csv
```

---

## 6. Cấu trúc Output Dự kiến

```
data/raw/
├── admission_2020.csv      # Điểm chuẩn năm 2020
├── admission_2021.csv      # Điểm chuẩn năm 2021
├── admission_2022.csv      # Điểm chuẩn năm 2022
├── admission_2023.csv      # Điểm chuẩn năm 2023
├── admission_2024.csv      # Điểm chuẩn năm 2024
├── admission_2025.csv      # Điểm chuẩn năm 2025
└── schools_info.csv        # Thông tin trường
```

**Ước tính quy mô:**

| Năm | Số trường dự kiến | Số ngành TB | Records ước tính |
|-----|-----------------|------------|-----------------|
| 2020 | ~200 | ~50 | ~10,000 |
| 2021 | ~220 | ~52 | ~11,440 |
| 2022 | ~240 | ~55 | ~13,200 |
| 2023 | ~260 | ~58 | ~15,080 |
| 2024 | ~280 | ~60 | ~16,800 |
| 2025 | ~300 | ~62 | ~18,600 |
| **Tổng** | | | **~85,000+ records** |

---

## 7. Xử lý Lỗi & Edge Cases

| Tình huống | Xử lý |
|-----------|-------|
| Trang web không phản hồi | Retry 3 lần với backoff, ghi log lỗi |
| Cấu trúc HTML thay đổi | Thử fallback parser, ghi cảnh báo |
| Điểm chuẩn = "Chưa có" | Gán NULL, đánh dấu trong log |
| Tên trường viết tắt lạ | Normalize function + manual mapping |
| Encoding sai | Force UTF-8 decode với `apparent_encoding` |
| Dữ liệu trùng lặp | Dedup ở bước Preprocessing |
| IP bị block | User-Agent rotation + delay ngẫu nhiên |

---

## 8. Lưu ý Pháp lý

- Dữ liệu điểm chuẩn được Bộ GD&ĐT và các trường **công bố công khai**
- Crawler tuân thủ `robots.txt` và rate limiting lịch sự
- Dữ liệu chỉ được sử dụng cho mục đích **nghiên cứu học thuật**
- Không crawl dữ liệu cá nhân thí sinh

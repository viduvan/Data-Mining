# 04_Data_Preprocessing.md

# Tiền xử lý Dữ liệu — Data Preprocessing & ETL

---

## 1. Tổng quan Pipeline ETL

Pipeline ETL (Extract – Transform – Load) chuyển đổi dữ liệu thô từ crawler thành dữ liệu sạch, sẵn sàng cho phân tích và khai phá.

```
data/raw/*.csv
     │
     ▼
┌─────────────────┐
│  1. LOAD RAW    │  Đọc tất cả admission_YYYY.csv + schools_info.csv
└────────┬────────┘
         ▼
┌─────────────────┐
│  2. CLEANING    │  Chuẩn hóa, loại bỏ duplicates, xử lý missing
└────────┬────────┘
         ▼
┌─────────────────┐
│  3. FEATURE     │  Tạo delta_score, competition_level, major_group...
│   ENGINEERING   │
└────────┬────────┘
         ▼
┌─────────────────┐
│  4. VALIDATION  │  Kiểm tra data quality
└────────┬────────┘
         ▼
┌─────────────────┐
│  5. EXPORT      │  → CSV (cleaned/, processed/) + PostgreSQL
└─────────────────┘
```

**Module chính:** `src/preprocessing/etl_pipeline.py`

**Cách chạy:**
```bash
# Chạy ETL không load DB (test)
python -m src.preprocessing.etl_pipeline --skip-db

# Chạy ETL đầy đủ
python -m src.preprocessing.etl_pipeline
```

---

## 2. Bước 1: Load Raw Data

**File:** `src/preprocessing/data_cleaner.py` → `load_raw_files()`

| Hạng mục | Chi tiết |
|----------|---------|
| Input | `data/raw/admission_*.csv` |
| Encoding | UTF-8-sig (BOM) |
| Merge | Nối tất cả các năm thành 1 DataFrame |
| Lọc năm | Hỗ trợ `--year 2023 2024` để chỉ load năm cụ thể |

---

## 3. Bước 2: Data Cleaning

### 3.1 Chuẩn hóa chuỗi (String Normalization)

| Xử lý | Ví dụ | Kết quả |
|--------|-------|---------|
| Unicode NFC | Tổ hợp diacritics | Chuẩn hóa Unicode |
| Strip whitespace | `"  Đại học  "` | `"Đại học"` |
| Collapse spaces | `"Đại  học   FPT"` | `"Đại học FPT"` |
| NULL detection | `"nan"`, `"None"`, `""` | → `None` |

### 3.2 Chuẩn hóa tên trường

Sử dụng **mapping dictionary** để đồng nhất tên:

| Tên gốc | Chuẩn hóa thành |
|---------|----------------|
| `"ĐH Bách khoa HN"` | `"Đại học Bách khoa Hà Nội"` |
| `"HUST"` | `"Đại học Bách khoa Hà Nội"` |
| `"đhqghn"` | `"Đại học Quốc gia Hà Nội"` |
| `"TP HCM"` | `"TP.HCM"` |

**Quy tắc:**
- `ĐH` → `Đại học`
- `HV` → `Học viện`
- `TP Hồ Chí Minh` → `TP.HCM`

### 3.3 Chuẩn hóa tên ngành

- Loại bỏ mã ngành 7 số ở đầu: `"7480201 - Công nghệ thông tin"` → `"Công nghệ thông tin"`
- Collapse whitespace

### 3.4 Chuẩn hóa tổ hợp xét tuyển

- Viết hoa + loại khoảng trắng: `"a 00"` → `"A00"`
- Validate format: chữ + 2 số (A00, D01, C00...)

### 3.5 Chuẩn hóa kiểu dữ liệu số

| Cột | Xử lý | Kiểu |
|-----|-------|------|
| `admission_score` | Thay `,` → `.`, ép float | `float64` |
| `quota` | Loại dấu ngăn hàng nghìn, ép int | `Int64` (nullable) |
| `year` | Ép int | `Int64` |

### 3.6 Xử lý Missing Values

| Cột | Chiến lược | Ghi chú |
|-----|-----------|--------|
| `school_name` | **DROP** nếu null | Bắt buộc |
| `admission_score` | **DROP** nếu null | Bắt buộc |
| `year` | **DROP** nếu null | Bắt buộc |
| `subject_group` | Fill `"Không xác định"` | Optional |
| `admission_method` | Fill `"Xét điểm thi THPT"` | Optional |
| `quota` | Giữ NULL | Optional |

### 3.7 Loại bỏ Duplicates

Xác định duplicate bởi tổ hợp: `(school_name, major_name, subject_group, year)`

Giữ lại record đầu tiên (`keep="first"`).

### 3.8 Filter dữ liệu không hợp lệ

| Quy tắc | Loại bỏ nếu |
|---------|------------|
| Điểm chuẩn | Ngoài range `[0, 30]` |
| Năm | Ngoài range `[2000, 2030]` |

---

## 4. Bước 3: Feature Engineering

**File:** `src/preprocessing/feature_engineering.py`

### 4.1 Danh sách Features mới

| Feature | Kiểu | Công thức / Logic |
|---------|------|-------------------|
| `major_group` | string | Phân nhóm ngành theo từ khóa tên ngành |
| `competition_level` | string | Phân loại theo ngưỡng điểm (≥25: Rất cao, ≥22: Cao, ≥18: TB, <18: Thấp) |
| `delta_score` | float | `admission_score[t] - admission_score[t-1]` (YoY change) |
| `delta_score_pct` | float | `delta_score / admission_score[t-1] × 100` |
| `score_trend` | string | Tăng (Δ ≥ 0.5) / Giảm (Δ ≤ -0.5) / Ổn định |
| `avg_score_school` | float | Điểm TB của trường trong năm đó |
| `rank_in_year` | int | Thứ hạng điểm chuẩn trong năm (1 = cao nhất) |

### 4.2 Phân nhóm ngành (`major_group`)

| Nhóm | Từ khóa nhận diện |
|------|------------------|
| Kỹ thuật - Công nghệ | công nghệ, kỹ thuật, điện, cơ khí, xây dựng |
| Kinh tế - Quản trị | kinh tế, quản trị, tài chính, kế toán, marketing |
| Y - Dược | y khoa, dược, điều dưỡng, y tế |
| Sư phạm - Giáo dục | sư phạm, giáo dục |
| Luật - Xã hội | luật, xã hội, chính trị |
| Nghệ thuật - Nhân văn | nghệ thuật, ngôn ngữ, văn học, lịch sử |
| Nông - Lâm - Ngư | nông nghiệp, lâm nghiệp, thủy sản |
| Khác | Không match keyword nào |

---

## 5. Bước 4: Data Validation

**File:** `src/preprocessing/validators.py`

| Quy tắc | Mức độ | Ngưỡng |
|---------|--------|--------|
| Cột bắt buộc phải tồn tại | ERROR | school_name, admission_score, year |
| Null ≤ 10% cho cột quan trọng | ERROR | school_name, admission_score, year |
| Điểm chuẩn trong [0, 30] | ERROR | Toàn bộ |
| Năm hợp lệ (2015–2030) | WARNING | Toàn bộ |
| Tên trường ≥ 5 ký tự | WARNING | Nghi ngờ dữ liệu lỗi |
| Chỉ tiêu trong [1, 50000] | WARNING | Hợp lý |

**Output:** `ValidationResult` object chứa `errors`, `warnings`, `stats`.

---

## 6. Bước 5: Export

### 6.1 CSV Output

| Thư mục | File | Mô tả |
|---------|------|-------|
| `data/cleaned/` | `admission_cleaned.csv` | Dữ liệu đã cleaning |
| `data/processed/` | `admission_processed.csv` | Dữ liệu + features mới |

### 6.2 PostgreSQL Output

Load vào Star Schema (xem `docs/05_Data_Warehouse.md`):
1. Dimension tables trước (dim_region, dim_year, dim_school, dim_major, dim_subject_group)
2. Fact table sau (fact_admission)

---

## 7. Thống kê Cleaning

Sau mỗi lần chạy, pipeline in ra thống kê:

```
══════════════════════════════════════════════
THỐNG KÊ DATA CLEANING
  Raw records      : 85,120
  Duplicates xóa   : 1,340
  Invalid score    : 23
  Missing school   : 5
  Clean records    : 83,752
  Retention rate   : 98.4%
══════════════════════════════════════════════
```

---

## 8. Xử lý Lỗi & Edge Cases

| Tình huống | Xử lý |
|-----------|-------|
| File CSV encoding sai | Auto-detect với `utf-8-sig`, fallback `latin-1` |
| Tên trường viết nhiều kiểu | Mapping dictionary + regex normalize |
| Điểm chuẩn có chữ (VD: "Chưa có") | Ép số → NaN → DROP |
| Year thiếu trong filename | Parse từ nội dung file hoặc bỏ qua |
| Cột không có trong file raw | Tạo cột với giá trị NULL |

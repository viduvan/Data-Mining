# 05_Data_Warehouse.md

# Kho Dữ liệu — PostgreSQL Data Warehouse

---

## 1. Tổng quan

Data Warehouse sử dụng **PostgreSQL** với thiết kế **Star Schema** để lưu trữ dữ liệu tuyển sinh đã xử lý. Mô hình này tối ưu cho:

- Truy vấn phân tích (OLAP) nhanh
- Kết nối trực tiếp Power BI qua PostgreSQL connector
- Aggregate theo nhiều chiều (trường, ngành, năm, khu vực, tổ hợp)

---

## 2. Star Schema — Sơ đồ Quan hệ

```
                      ┌──────────────┐
                      │   dim_year   │
                      │──────────────│
                      │ year_key PK  │
                      │ year         │
                      │ period_label │
                      └──────┬───────┘
                             │
  ┌──────────────┐    ┌──────┴───────────┐    ┌────────────────┐
  │  dim_school  │    │  fact_admission  │    │   dim_major    │
  │──────────────│    │──────────────────│    │────────────────│
  │ school_key PK├───►│ admission_key PK │◄───┤ major_key PK   │
  │ school_code  │    │ school_key FK    │    │ major_code     │
  │ school_name  │    │ major_key FK     │    │ major_name     │
  │ school_type  │    │ year_key FK      │    │ major_group    │
  │ province     │    │ subject_group_key│    │ field_of_study │
  │ region_code  │    │ admission_score  │    └────────────────┘
  │ website      │    │ quota            │
  └──────┬───────┘    │ admission_method │
         │            │ delta_score      │
         │            │ competition_level│
  ┌──────┴───────┐    │ score_trend      │    ┌──────────────────┐
  │  dim_region  │    │ created_at       │    │dim_subject_group │
  │──────────────│    └──────┬───────────┘    │──────────────────│
  │ region_key PK│           │                │ subject_group_key│
  │ region_code  │           └───────────────►│ group_code       │
  │ region_name  │                            │ group_name       │
  │ area         │                            │ subject_1/2/3    │
  └──────────────┘                            └──────────────────┘
```

---

## 3. Chi tiết Dimension Tables

### 3.1 dim_region — Chiều khu vực

| Cột | Kiểu | Constraint | Mô tả |
|-----|------|-----------|-------|
| `region_key` | SERIAL | PK | Khóa tự tăng |
| `region_code` | VARCHAR(10) | UNIQUE NOT NULL | B, T, N, UK |
| `region_name` | VARCHAR(100) | NOT NULL | Miền Bắc / Miền Trung / Miền Nam |
| `area` | VARCHAR(50) | | Bắc / Trung / Nam |

**Seed data:** 4 records (Bắc, Trung, Nam, Không xác định)

### 3.2 dim_year — Chiều năm

| Cột | Kiểu | Constraint | Mô tả |
|-----|------|-----------|-------|
| `year_key` | SERIAL | PK | Khóa tự tăng |
| `year` | INT | UNIQUE NOT NULL | 2020, 2021, ..., 2025 |
| `period_label` | VARCHAR(100) | | Giai đoạn COVID / Hậu COVID |

**Phân kỳ:**
- 2020–2022: "Giai đoạn COVID (2020-2022)"
- 2023–2025: "Giai đoạn Hậu COVID (2023-2025)"

### 3.3 dim_school — Chiều trường

| Cột | Kiểu | Constraint | Mô tả |
|-----|------|-----------|-------|
| `school_key` | SERIAL | PK | Khóa tự tăng |
| `school_code` | VARCHAR(20) | | Mã trường (Bộ GD&ĐT) |
| `school_name` | VARCHAR(300) | UNIQUE NOT NULL | Tên trường đầy đủ |
| `school_type` | VARCHAR(50) | CHECK IN(...) | Công lập / Tư thục / Nước ngoài |
| `province` | VARCHAR(100) | | Tỉnh/thành phố |
| `region_code` | VARCHAR(10) | FK → dim_region | Khu vực |
| `website` | VARCHAR(255) | | Website chính thức |
| `established_year` | INT | | Năm thành lập |

**Indexes:** school_name, school_type, region_code

### 3.4 dim_major — Chiều ngành

| Cột | Kiểu | Constraint | Mô tả |
|-----|------|-----------|-------|
| `major_key` | SERIAL | PK | Khóa tự tăng |
| `major_code` | VARCHAR(20) | | Mã ngành (7 số) |
| `major_name` | VARCHAR(300) | UNIQUE NOT NULL | Tên ngành |
| `major_group` | VARCHAR(100) | | Nhóm ngành |
| `field_of_study` | VARCHAR(200) | | Lĩnh vực chi tiết |

### 3.5 dim_subject_group — Chiều tổ hợp

| Cột | Kiểu | Constraint | Mô tả |
|-----|------|-----------|-------|
| `subject_group_key` | SERIAL | PK | Khóa tự tăng |
| `group_code` | VARCHAR(10) | UNIQUE NOT NULL | A00, D01, C00... |
| `group_name` | VARCHAR(100) | NOT NULL | Tên đầy đủ |
| `subject_1` | VARCHAR(100) | | Môn 1 |
| `subject_2` | VARCHAR(100) | | Môn 2 |
| `subject_3` | VARCHAR(100) | | Môn 3 |

**Seed data:** 12 tổ hợp phổ biến (A00, A01, B00, C00, D01...)

---

## 4. Chi tiết Fact Table

### fact_admission — Bảng sự kiện điểm chuẩn

| Cột | Kiểu | Constraint | Mô tả |
|-----|------|-----------|-------|
| `admission_key` | SERIAL | PK | Khóa tự tăng |
| `school_key` | INT | FK NOT NULL | → dim_school |
| `major_key` | INT | FK | → dim_major |
| `year_key` | INT | FK NOT NULL | → dim_year |
| `subject_group_key` | INT | FK | → dim_subject_group |
| `admission_score` | NUMERIC(5,2) | | Điểm chuẩn (0.00–30.00) |
| `quota` | INT | | Chỉ tiêu tuyển sinh |
| `admission_method` | VARCHAR(200) | | Phương thức xét tuyển |
| `delta_score` | NUMERIC(5,2) | | Chênh lệch YoY |
| `delta_score_pct` | NUMERIC(7,2) | | Chênh lệch % |
| `competition_level` | VARCHAR(20) | CHECK IN(...) | Rất cao / Cao / TB / Thấp |
| `score_trend` | VARCHAR(20) | | Tăng / Giảm / Ổn định |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Thời gian load |

**Unique Constraint:** `(school_key, major_key, subject_group_key, year_key)` — tránh trùng lặp

**Indexes:** school_key, major_key, year_key, admission_score, competition_level, (year_key + admission_score)

---

## 5. Hướng dẫn Setup

### 5.1 Cài đặt PostgreSQL

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Khởi động service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 5.2 Tạo Database

```bash
sudo -u postgres psql -f sql/create_database.sql
```

### 5.3 Tạo Schema

```bash
psql -U admission_user -d vietnam_admission_dw -f sql/create_schema.sql
```

### 5.4 Kiểm tra

```bash
# Liệt kê tables
psql -U admission_user -d vietnam_admission_dw -c "\dt"

# Kiểm tra dim_region
psql -U admission_user -d vietnam_admission_dw -c "SELECT * FROM dim_region;"

# Kiểm tra dim_year
psql -U admission_user -d vietnam_admission_dw -c "SELECT * FROM dim_year;"
```

---

## 6. Load Dữ liệu

### 6.1 Tự động (Python)

```bash
python -m src.preprocessing.etl_pipeline
```

Pipeline tự động:
1. Load dim tables (region → year → school → major → subject_group)
2. Load fact table (fact_admission) với FK lookup
3. Upsert logic (skip duplicates khi chạy lại)

### 6.2 Thủ công (SQL)

```sql
-- Kiểm tra sau khi load
SELECT COUNT(*) AS total_records FROM fact_admission;
SELECT COUNT(*) AS total_schools FROM dim_school;
SELECT COUNT(*) AS total_majors FROM dim_major;
```

---

## 7. Truy vấn Phân tích Mẫu

### 7.1 Điểm trung bình theo năm

```sql
SELECT y.year, ROUND(AVG(f.admission_score), 2) AS avg_score
FROM fact_admission f
JOIN dim_year y ON f.year_key = y.year_key
GROUP BY y.year
ORDER BY y.year;
```

### 7.2 Top 10 trường điểm cao nhất

```sql
SELECT s.school_name, ROUND(AVG(f.admission_score), 2) AS avg_score
FROM fact_admission f
JOIN dim_school s ON f.school_key = s.school_key
GROUP BY s.school_name
ORDER BY avg_score DESC
LIMIT 10;
```

### 7.3 Phân bố mức cạnh tranh

```sql
SELECT f.competition_level, COUNT(*) AS count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM fact_admission f
GROUP BY f.competition_level
ORDER BY count DESC;
```

Xem thêm queries chi tiết tại:
- `sql/queries/trend_analysis.sql`
- `sql/queries/school_analysis.sql`
- `sql/queries/major_analysis.sql`

---

## 8. Kết nối từ Power BI

1. Mở Power BI Desktop → `Get Data` → `PostgreSQL Database`
2. Server: `localhost`
3. Database: `vietnam_admission_dw`
4. Chọn tables: `fact_admission` + tất cả `dim_*`
5. Power BI tự detect relationships qua FK

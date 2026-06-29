# 02_System_Architecture.md

# Kiến trúc Hệ thống — Vietnam University Admission Data Mining

---

## 1. Tổng quan Kiến trúc

Hệ thống được thiết kế theo mô hình **Pipeline Data Analytics** gồm 7 lớp chức năng liên kết tuần tự:

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
│   Website Bộ GD&ĐT │ Website Trường │ Báo chí Giáo dục         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/HTML
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATA COLLECTION LAYER                         │
│        Python Crawler (requests + BeautifulSoup + Selenium)     │
│           → Output: CSV files vào data/raw/                     │
└────────────────────────────┬────────────────────────────────────┘
                             │ Raw CSV
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 DATA CLEANING & ETL LAYER                       │
│    Cleaning │ Normalization │ Feature Engineering │ Validation  │
│        → Output: Clean CSV vào data/cleaned/ & data/processed/  │
└────────────────────────────┬────────────────────────────────────┘
                             │ Clean Data
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATA WAREHOUSE LAYER (PostgreSQL)                  │
│          Star Schema: 1 Fact Table + 5 Dimension Tables         │
│         vietnam_admission_dw database trên PostgreSQL           │
└──────────────────┬─────────────────────┬───────────────────────┘
                   │                     │
                   ▼                     ▼
┌────────────────────────┐   ┌──────────────────────────────────┐
│   EDA LAYER            │   │     DATA MINING LAYER            │
│   Jupyter Notebooks    │   │  Clustering │ Assoc. Rules       │
│   Matplotlib/Seaborn   │   │  Forecasting (ARIMA/LinReg)      │
│   Plotly               │   │  scikit-learn, mlxtend, stats    │
└────────────┬───────────┘   └──────────────┬───────────────────┘
             │                              │
             └──────────────┬───────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│           BUSINESS INTELLIGENCE LAYER (Power BI)               │
│    Executive │ School │ Major │ Forecast Dashboards             │
│         Interactive Reports, KPIs, DAX Measures                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              DECISION SUPPORT LAYER                             │
│           Recommendation System (Python CLI/Notebook)           │
│      Input: Điểm thi + Tổ hợp + Khu vực                        │
│      Output: Danh sách Trường/Ngành + Safety Score             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Kiến trúc Chức năng

```
                        Người dùng
                             │
              ┌──────────────┼──────────────────┐
              │              │                  │
              ▼              ▼                  ▼
       Dashboard         Phân tích EDA     Gợi ý Trường/Ngành
       Power BI           Notebooks        Recommendation System
              │              │                  │
              └──────────────┼──────────────────┘
                             ▼
                   Data Warehouse (PostgreSQL)
                   vietnam_admission_dw
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
              ETL Pipeline       Data Mining
              (Preprocessing)    (Mining Layer)
                    │
               Raw Dataset
               (data/raw/)
                    │
              Web Crawler
              (src/crawler/)
                    │
             Data Sources (Web)
```

---

## 3. Thiết kế từng Layer

### 3.1 Data Collection Layer

**Công nghệ:** `requests`, `BeautifulSoup4`, `lxml`, `Selenium`, `tqdm`

**Mô hình:**
```
BaseCrawler (Abstract)
    ├── AdmissionCrawler      → Crawl điểm chuẩn theo năm
    └── SchoolInfoCrawler     → Crawl thông tin trường
```

**Chiến lược crawl:**
- Rate limiting: 1.5 giây giữa mỗi request
- Retry logic: Tối đa 3 lần với exponential backoff
- User-Agent rotation để tránh bị chặn
- Lưu checkpoint để resume nếu bị ngắt

**Output schema dữ liệu raw:**

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| school_code | string | Mã trường (do Bộ GD&ĐT cấp) |
| school_name | string | Tên trường đầy đủ |
| major_code | string | Mã ngành |
| major_name | string | Tên ngành |
| subject_group | string | Tổ hợp xét tuyển (VD: A00, D01) |
| admission_score | float | Điểm chuẩn |
| quota | int | Chỉ tiêu tuyển sinh |
| admission_method | string | Phương thức xét tuyển |
| year | int | Năm tuyển sinh |
| source_url | string | URL nguồn dữ liệu |

---

### 3.2 Data Cleaning & ETL Layer

**Công nghệ:** `pandas`, `numpy`, `SQLAlchemy`, `loguru`

**Các bước xử lý:**

```
Raw Data (CSV)
     │
     ▼ data_cleaner.py
[1] Chuẩn hóa encoding (UTF-8)
[2] Chuẩn hóa tên trường (lowercase, bỏ dấu, mapping)
[3] Chuẩn hóa tên ngành
[4] Loại bỏ duplicates
[5] Xử lý missing values
[6] Validate kiểu dữ liệu (điểm 0-30, chỉ tiêu > 0)
     │
     ▼ feature_engineering.py
[7] Tính delta_score (YoY change)
[8] Tính competition_level
[9] Phân nhóm ngành (major_group)
[10] Phân khu vực (region)
     │
     ▼ validators.py
[11] Data quality report
[12] Log vi phạm
     │
     ▼ Clean Dataset (data/cleaned/ + data/processed/)
     │
     ▼ db_loader.py
[13] Load vào PostgreSQL (Upsert)
```

---

### 3.3 Data Warehouse Layer (PostgreSQL)

**Database:** `vietnam_admission_dw` trên PostgreSQL 15+

**Mô hình:** Star Schema

```
                    ┌─────────────┐
                    │  dim_year   │
                    │─────────────│
                    │ year_key PK │
                    │ year        │
                    │ period_label│
                    └──────┬──────┘
                           │ FK
         ┌─────────────────┼─────────────────┐
         │                 │                 │
┌────────┴──────┐  ┌───────┴────────┐  ┌────┴────────────┐
│  dim_school   │  │  fact_         │  │   dim_major     │
│───────────────│  │  admission     │  │─────────────────│
│ school_key PK │◄─┤────────────────├─►│ major_key PK    │
│ school_code   │  │ admission_key  │  │ major_code      │
│ school_name   │  │ school_key FK  │  │ major_name      │
│ school_type   │  │ major_key FK   │  │ major_group     │
│ region_key FK │  │ year_key FK    │  │ field_of_study  │
│ website       │  │ subj_grp_key FK│  └─────────────────┘
└───────────────┘  │ region_key FK  │
                   │ admission_score│
┌───────────────┐  │ quota          │  ┌─────────────────┐
│dim_subject_grp│  │ admission_meth │  │   dim_region    │
│───────────────│◄─┤ delta_score    ├─►│─────────────────│
│ subj_grp_key  │  │ competition_lvl│  │ region_key PK   │
│ group_code    │  └────────────────┘  │ region_code     │
│ group_name    │                      │ region_name     │
│ subject_1     │                      │ area            │
│ subject_2     │                      └─────────────────┘
│ subject_3     │
└───────────────┘
```

**Kết nối Power BI:** PostgreSQL Connector (có sẵn trong Power BI Desktop)

---

### 3.4 EDA Layer

**Công nghệ:** `Jupyter Notebook`, `matplotlib`, `seaborn`, `plotly`

**Kết nối:** SQLAlchemy → PostgreSQL → pandas DataFrame

**Notebooks:**

| Notebook | Mục tiêu |
|---------|---------|
| 01_data_overview | Tổng quan, thống kê mô tả |
| 02_trend_analysis | Xu hướng điểm chuẩn theo năm |
| 03_school_analysis | Phân tích theo trường |
| 04_major_analysis | Phân tích theo ngành |
| 05_subject_group_analysis | Phân tích theo tổ hợp |

---

### 3.5 Data Mining Layer

**Công nghệ:** `scikit-learn`, `mlxtend`, `statsmodels`

| Module | Thuật toán | Input | Output |
|--------|-----------|-------|--------|
| clustering.py | K-Means | Vector features trường/ngành | Cluster labels |
| association_rules.py | Apriori | Transaction matrix | Tập luật (support, confidence, lift) |
| forecasting.py | Linear Reg. + ARIMA | Time series điểm chuẩn | Dự báo năm tới + confidence interval |

---

### 3.6 Business Intelligence Layer (Power BI)

**Kết nối:** Power BI Desktop → PostgreSQL (hoặc CSV export từ `data/warehouse/`)

**Dashboards:**

| Dashboard | Mô tả |
|-----------|-------|
| Executive Dashboard | KPIs tổng quát, trends tổng thể |
| School Dashboard | Drill-down theo trường |
| Major Dashboard | Drill-down theo ngành/nhóm ngành |
| Forecast Dashboard | Dự báo điểm chuẩn tương lai |

---

### 3.7 Decision Support Layer

**Công nghệ:** Python (CLI + Jupyter Notebook demo)

**Luồng xử lý Recommendation:**

```
Input: (score, subject_group, region)
         │
         ▼
[1] Tính tổng điểm + điểm ưu tiên khu vực
         │
         ▼
[2] Query PostgreSQL: tìm ngành/trường có điểm chuẩn ≤ tổng điểm thí sinh
         │
         ▼
[3] Tính safety_score = (score - admission_score) / admission_score × 100%
         │
         ▼
[4] Phân loại: 🟢 An toàn | 🟡 Tương đối | 🔴 Rủi ro
         │
         ▼
[5] Enrich với cluster info và dự báo điểm xu hướng
         │
         ▼
Output: Ranked list (trường, ngành, điểm chuẩn, safety_score, cluster)
```

---

## 4. Luồng dữ liệu End-to-End

```
[Web Sources]
     │ HTTP crawl
     ▼
[data/raw/*.csv]          ← Admision data 2020-2025 raw
     │ ETL pipeline
     ▼
[data/cleaned/*.csv]      ← Cleaned & validated data
     │ Feature engineering
     ▼
[data/processed/*.csv]    ← Features added (delta, level, group...)
     │ db_loader.py
     ▼
[PostgreSQL DW]           ← Star Schema (fact + 5 dim tables)
     │                         │
     │ SQLAlchemy              │ Power BI Connector
     ▼                         ▼
[Notebooks/Mining]        [Power BI Dashboard]
     │
     ▼
[Recommendation CLI]
```

---

## 5. Công nghệ Stack Tổng hợp

| Layer | Công nghệ | Phiên bản |
|-------|-----------|---------|
| Data Collection | Python, requests, BeautifulSoup4, Selenium | Python 3.10+ |
| ETL & Preprocessing | pandas, numpy, SQLAlchemy | pandas 2.0+ |
| Data Warehouse | PostgreSQL | 15+ |
| EDA & Visualization | Jupyter, matplotlib, seaborn, plotly | Latest |
| Data Mining | scikit-learn, mlxtend, statsmodels | Latest |
| BI Dashboard | Microsoft Power BI Desktop | Latest |
| Version Control | Git | 2.x |

---

## 6. Yêu cầu Hệ thống

| Thành phần | Yêu cầu tối thiểu |
|-----------|-----------------|
| OS | Linux / macOS / Windows 10+ |
| Python | 3.10+ |
| RAM | 8 GB (khuyến nghị 16 GB) |
| Disk | 5 GB trống |
| PostgreSQL | 15+ |
| Power BI | Desktop version (Windows) |
| Chrome | Latest (cho Selenium) |

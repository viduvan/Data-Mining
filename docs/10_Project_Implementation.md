# 10_Project_Implementation.md

# Hướng dẫn Triển khai — Project Implementation Guide

---

## 1. Yêu cầu Hệ thống

### 1.1 Phần mềm

| Phần mềm | Phiên bản | Bắt buộc? |
|----------|----------|----------|
| Python | ≥ 3.10 | ✅ Bắt buộc |
| Conda (Miniconda / Anaconda) | Mới nhất | ✅ Bắt buộc |
| PostgreSQL | ≥ 15 | ✅ Bắt buộc |
| Power BI Desktop | Mới nhất | Khuyến nghị |
| Git | ≥ 2.30 | Khuyến nghị |

### 1.2 Phần cứng (Khuyến nghị)

| Thông số | Tối thiểu | Khuyến nghị |
|---------|----------|------------|
| RAM | 4 GB | 8 GB |
| CPU | 2 cores | 4 cores |
| Disk | 5 GB trống | 10 GB trống |
| Internet | Cần (cho crawling) | Ổn định |

---

## 2. Cài đặt Từng bước

### Bước 1: Clone Project

```bash
git clone https://github.com/your-username/Data-Mining.git
cd Data-Mining
```

### Bước 2: Tạo Conda Environment

```bash
# Tạo env mới
conda create -n testing python=3.11 -y

# Kích hoạt env
conda activate testing
```

### Bước 3: Cài đặt Dependencies

```bash
# Cài tất cả packages
pip install -r requirements.txt

# Hoặc cài từng nhóm:
pip install pandas numpy                                    # Core
pip install requests beautifulsoup4 tqdm                     # Crawling
pip install sqlalchemy psycopg2-binary python-dotenv loguru  # Database
pip install scikit-learn mlxtend statsmodels                  # Mining
pip install matplotlib seaborn plotly openpyxl                # Visualization
pip install pytest                                           # Testing
pip install jupyter                                          # Notebooks
```

### Bước 4: Cài đặt PostgreSQL

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Khởi động
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Kiểm tra
psql --version
```

### Bước 5: Tạo Database

```bash
# Tạo database + user
sudo -u postgres psql -f sql/create_database.sql

# Tạo schema (Star Schema)
psql -U admission_user -d vietnam_admission_dw -f sql/create_schema.sql
```

### Bước 6: Cấu hình .env

```bash
cp .env.example .env
```

Sửa file `.env`:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vietnam_admission_dw
DB_USER=admission_user
DB_PASSWORD=admission_pass_2024
```

---

## 3. Chạy Từng Module

### 3.1 Thu thập dữ liệu (Crawling)

```bash
# Chạy crawler (dùng seed data, không cần internet)
python -m src.crawler.run_crawler --use-seed-schools

# Chạy crawler thực tế (cần internet)
python -m src.crawler.run_crawler

# Kết quả: data/raw/admission_*.csv + schools_info.csv
```

### 3.2 Xử lý dữ liệu (ETL)

```bash
# ETL + load vào PostgreSQL
python -m src.preprocessing.etl_pipeline

# ETL chỉ tạo CSV (không cần DB)
python -m src.preprocessing.etl_pipeline --skip-db

# Kết quả: data/cleaned/ + data/processed/
```

### 3.3 Export cho Power BI

```bash
python -m src.preprocessing.export_powerbi

# Kết quả: data/warehouse/*.csv
```

### 3.4 Data Mining

```python
# Trong Python / Jupyter Notebook

# Clustering
from src.mining.clustering import ClusteringAnalyzer
import pandas as pd
df = pd.read_csv("data/processed/admission_processed.csv", encoding="utf-8-sig")
analyzer = ClusteringAnalyzer(df)
schools = analyzer.cluster_schools(k=4)

# Association Rules
from src.mining.association_rules import AssociationRuleMiner
miner = AssociationRuleMiner(df)
rules = miner.mine_rules()

# Forecasting
from src.mining.forecasting import ScoreForecaster
forecaster = ScoreForecaster(df)
result = forecaster.forecast_school_major("Đại học Bách khoa Hà Nội", "Công nghệ thông tin")
```

### 3.5 Recommendation System

```bash
# CLI
python -m src.recommendation.recommender \
  --scores 8.5 9.0 8.0 \
  --group A00 \
  --region KV2 \
  --top 15
```

### 3.6 Jupyter Notebooks

```bash
jupyter notebook notebooks/ --no-browser --port=8888
# Mở: http://localhost:8888
```

---

## 4. Chạy Tests

```bash
# Tất cả tests
python -m pytest tests/ -v

# Test cụ thể
python -m pytest tests/test_crawler.py -v
python -m pytest tests/test_preprocessing.py -v
python -m pytest tests/test_recommendation.py -v
```

---

## 5. Cấu trúc Mã nguồn

```
Data-Mining/
├── src/
│   ├── __init__.py
│   ├── crawler/                    # Phase 2: Thu thập dữ liệu
│   │   ├── __init__.py
│   │   ├── config.py               # Cấu hình URLs, headers, delays
│   │   ├── base_crawler.py          # Abstract base class
│   │   ├── admission_crawler.py     # Crawl điểm chuẩn 2020-2025
│   │   ├── school_info_crawler.py   # Crawl thông tin trường
│   │   ├── utils.py                 # Normalize, parse, checkpoint
│   │   └── run_crawler.py           # CLI entry point
│   │
│   ├── preprocessing/              # Phase 3: ETL & DW
│   │   ├── __init__.py
│   │   ├── data_cleaner.py          # Làm sạch dữ liệu
│   │   ├── feature_engineering.py   # Tạo features mới
│   │   ├── validators.py            # Kiểm tra data quality
│   │   ├── etl_pipeline.py          # Orchestrate pipeline
│   │   ├── db_loader.py             # Load vào PostgreSQL
│   │   └── export_powerbi.py        # Export CSV cho Power BI
│   │
│   ├── mining/                     # Phase 5: Data Mining
│   │   ├── __init__.py
│   │   ├── clustering.py            # K-Means clustering
│   │   ├── association_rules.py     # Apriori association rules
│   │   └── forecasting.py           # Linear Regression + ARIMA
│   │
│   └── recommendation/            # Phase 5: Recommendation
│       ├── __init__.py
│       ├── scorer.py                # Safety score calculation
│       └── recommender.py           # Admission recommender engine
│
├── sql/
│   ├── create_database.sql          # Tạo DB + user
│   ├── create_schema.sql            # Star Schema DDL
│   └── queries/
│       ├── trend_analysis.sql       # Queries xu hướng
│       ├── school_analysis.sql      # Queries phân tích trường
│       └── major_analysis.sql       # Queries phân tích ngành
│
├── tests/
│   ├── test_crawler.py              # 29 test cases
│   ├── test_preprocessing.py        # 20 test cases
│   └── test_recommendation.py       # 18 test cases
│
├── data/                           # Dữ liệu (gitignored)
│   ├── raw/                         # Dữ liệu thô
│   ├── cleaned/                     # Dữ liệu đã cleaning
│   ├── processed/                   # Dữ liệu + features
│   └── warehouse/                   # Export cho Power BI
│
├── docs/                           # 12 tài liệu
├── powerbi/                        # Wireframe + DAX measures
├── notebooks/                      # Jupyter notebooks
├── images/                         # Charts, plots
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

---

## 6. Troubleshooting

### 6.1 Lỗi thường gặp

| Lỗi | Nguyên nhân | Giải pháp |
|-----|-----------|----------|
| `ModuleNotFoundError: No module named 'src'` | Chạy từ sai thư mục | `cd Data-Mining/` rồi chạy lại |
| `psycopg2 OperationalError: connection refused` | PostgreSQL chưa chạy | `sudo systemctl start postgresql` |
| `UnicodeDecodeError` | Encoding sai | Dùng `encoding="utf-8-sig"` |
| `Empty DataFrame after cleaning` | Dữ liệu raw thiếu | Kiểm tra `data/raw/` có file không |
| `ARIMA cannot fit` | Dữ liệu quá ít | Cần ≥3 data points, nên ≥5 |

### 6.2 Reset Database

```bash
# Xóa tất cả dữ liệu, giữ schema
psql -U admission_user -d vietnam_admission_dw -c "TRUNCATE fact_admission CASCADE;"

# Xóa toàn bộ và tạo lại
sudo -u postgres psql -c "DROP DATABASE vietnam_admission_dw;"
sudo -u postgres psql -f sql/create_database.sql
psql -U admission_user -d vietnam_admission_dw -f sql/create_schema.sql
```

### 6.3 Reset Data

```bash
# Xóa tất cả dữ liệu processed
rm -rf data/cleaned/* data/processed/* data/warehouse/*
```

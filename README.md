# Vietnam University Admission Data Mining

> **Phân tích và Khai phá dữ liệu tuyển sinh Đại học Việt Nam giai đoạn 2020–2025 bằng Data Mining và Power BI**

---

## Giới thiệu

Dự án xây dựng hệ thống thu thập, xử lý, phân tích và khai phá dữ liệu tuyển sinh đại học Việt Nam giai đoạn 2020–2025, kết hợp các kỹ thuật Data Mining và trực quan hóa bằng Power BI nhằm hỗ trợ học sinh, giáo viên và nhà quản lý giáo dục trong việc phân tích xu hướng và ra quyết định tuyển sinh.

## Công nghệ sử dụng

| Công nghệ | Mục đích |
|-----------|---------|
| Python | Crawl dữ liệu, ETL, Data Mining |
| PostgreSQL | Data Warehouse (Star Schema) |
| Power BI | Dashboard, KPI, Visualization |
| Jupyter Notebook | EDA, phân tích, trình bày kết quả |
| SQL | Thiết kế & truy vấn Data Warehouse |

## Cấu trúc thư mục

```text
Data-Mining/
├── data/
│   ├── raw/              # Dữ liệu thô crawl về
│   ├── cleaned/          # Dữ liệu đã làm sạch
│   ├── processed/        # Dữ liệu đã xử lý (feature engineering)
│   └── warehouse/        # Export từ PostgreSQL cho Power BI
├── notebooks/            # Jupyter notebooks (EDA & Data Mining)
├── src/
│   ├── crawler/          # Web crawler thu thập dữ liệu
│   ├── preprocessing/    # ETL & Data Cleaning pipeline
│   ├── mining/           # Thuật toán Data Mining
│   └── recommendation/   # Hệ thống gợi ý trường/ngành
├── powerbi/              # Power BI files, wireframes, DAX measures
├── sql/                  # PostgreSQL DDL & analytical queries
│   └── queries/          # Truy vấn phân tích mẫu
├── docs/                 # Tài liệu chi tiết từng module
├── images/               # Hình ảnh, biểu đồ xuất ra
├── tests/                # Unit tests
├── requirements.txt
└── README.md
```

## Hướng dẫn cài đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd Data-Mining
```

### 2. Tạo môi trường ảo Python

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
# hoặc: venv\Scripts\activate   # Windows
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cài đặt PostgreSQL

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# Tạo database
sudo -u postgres psql
CREATE DATABASE vietnam_admission_dw;
CREATE USER admission_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE vietnam_admission_dw TO admission_user;
\q
```

### 5. Cấu hình biến môi trường

```bash
cp .env.example .env
# Chỉnh sửa .env với thông tin PostgreSQL của bạn
```

File `.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vietnam_admission_dw
DB_USER=admission_user
DB_PASSWORD=your_password
```

## Hướng dẫn chạy từng bước

### Bước 1 — Thu thập dữ liệu (Crawl)

```bash
python -m src.crawler.run_crawler --year all --output data/raw/
```

### Bước 2 — Làm sạch & ETL

```bash
python -m src.preprocessing.etl_pipeline --input data/raw/ --output data/cleaned/
```

### Bước 3 — Tạo Data Warehouse PostgreSQL

```bash
psql -U admission_user -d vietnam_admission_dw -f sql/create_schema.sql
python -m src.preprocessing.db_loader --input data/cleaned/
```

### Bước 4 — Chạy EDA (Jupyter Notebook)

```bash
jupyter notebook notebooks/
```

### Bước 5 — Chạy Data Mining

```bash
python -m src.mining.clustering
python -m src.mining.association_rules
python -m src.mining.forecasting
```

### Bước 6 — Export dữ liệu cho Power BI

```bash
python -m src.preprocessing.export_powerbi --output data/warehouse/
```

### Bước 7 — Demo Recommendation System

```bash
python -m src.recommendation.recommender --score 26.5 --group A00 --region HN
```

## Tài liệu dự án

| File | Nội dung |
|------|---------|
| [01_Problem_Statement.md](docs/01_Problem_Statement.md) | Phân tích bài toán nghiệp vụ |
| [02_System_Architecture.md](docs/02_System_Architecture.md) | Kiến trúc hệ thống |
| [03_Data_Collection.md](docs/03_Data_Collection.md) | Thiết kế thu thập dữ liệu |
| [04_Data_Preprocessing.md](docs/04_Data_Preprocessing.md) | ETL & Data Cleaning |
| [05_Data_Warehouse.md](docs/05_Data_Warehouse.md) | Star Schema PostgreSQL |
| [06_Exploratory_Data_Analysis.md](docs/06_Exploratory_Data_Analysis.md) | EDA & KPIs |
| [07_Data_Mining.md](docs/07_Data_Mining.md) | Thuật toán & kết quả Mining |
| [08_PowerBI_Dashboard.md](docs/08_PowerBI_Dashboard.md) | Thiết kế Dashboard |
| [09_Recommendation_System.md](docs/09_Recommendation_System.md) | Hệ thống gợi ý |
| [10_Project_Implementation.md](docs/10_Project_Implementation.md) | Hướng dẫn triển khai |
| [11_Project_Management.md](docs/11_Project_Management.md) | Timeline & quản lý tiến độ |
| [12_Future_Work.md](docs/12_Future_Work.md) | Định hướng mở rộng |

## Chạy Tests

```bash
pytest tests/ -v --cov=src
```


---

*Dự án thuộc môn học Data Mining — Trường Đại học FPT HÀ NỘI*

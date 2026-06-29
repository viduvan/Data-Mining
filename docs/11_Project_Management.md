# 11_Project_Management.md

# Quản lý Dự án — Vietnam University Admission Data Mining

---

## 1. Tổng quan Tiến độ

| Phase | Nội dung | Thời gian | Trạng thái |
|-------|----------|-----------|-----------|
| Phase 1 | Thiết lập dự án & Tài liệu nền tảng | 2–3 ngày | 🔄 Đang thực hiện |
| Phase 2 | Thu thập dữ liệu (Data Collection) | 5–7 ngày | ⏳ Chờ |
| Phase 3 | ETL & Data Warehouse (PostgreSQL) | 5–7 ngày | ⏳ Chờ |
| Phase 4 | Exploratory Data Analysis | 4–5 ngày | ⏳ Chờ |
| Phase 5 | Data Mining & Recommendation | 7–10 ngày | ⏳ Chờ |
| Phase 6 | Power BI Dashboard & Hoàn thiện | 5–7 ngày | ⏳ Chờ |
| **Tổng** | | **~30–40 ngày** | |

---

## 2. Milestones

| Milestone | Deliverable chính | Phase |
|-----------|-----------------|-------|
| M1 — Project Foundation | Cấu trúc thư mục, README, requirements.txt, 3 tài liệu nền | Phase 1 |
| M2 — Raw Data Ready | Crawler hoạt động, dữ liệu raw 2020–2025 trong `data/raw/` | Phase 2 |
| M3 — Data Warehouse Live | PostgreSQL DW với Star Schema, dữ liệu clean đã load | Phase 3 |
| M4 — EDA Complete | 5 notebooks EDA, insights và visualizations | Phase 4 |
| M5 — Models Ready | 3 mô hình Mining + Recommendation System hoạt động | Phase 5 |
| M6 — Project Complete | Power BI Dashboard, tài liệu đầy đủ, unit tests pass | Phase 6 |

---

## 3. Checklist Deliverables

### Phase 1 ✅ / ❌

- [ ] Cấu trúc thư mục đầy đủ
- [ ] `README.md`
- [ ] `requirements.txt`
- [ ] `.env.example`
- [ ] `docs/01_Problem_Statement.md`
- [ ] `docs/02_System_Architecture.md`
- [ ] `docs/11_Project_Management.md`

### Phase 2

- [ ] `src/crawler/config.py`
- [ ] `src/crawler/base_crawler.py`
- [ ] `src/crawler/admission_crawler.py`
- [ ] `src/crawler/school_info_crawler.py`
- [ ] `src/crawler/utils.py`
- [ ] `src/crawler/run_crawler.py`
- [ ] `data/raw/admission_2020.csv` đến `2025.csv`
- [ ] `data/raw/schools_info.csv`
- [ ] `docs/03_Data_Collection.md`

### Phase 3

- [ ] `src/preprocessing/data_cleaner.py`
- [ ] `src/preprocessing/feature_engineering.py`
- [ ] `src/preprocessing/etl_pipeline.py`
- [ ] `src/preprocessing/validators.py`
- [ ] `src/preprocessing/db_loader.py`
- [ ] `src/preprocessing/export_powerbi.py`
- [ ] `sql/create_database.sql`
- [ ] `sql/create_schema.sql`
- [ ] `sql/load_data.sql`
- [ ] `sql/create_indexes.sql`
- [ ] `sql/queries/trend_analysis.sql`
- [ ] `sql/queries/school_analysis.sql`
- [ ] `sql/queries/major_analysis.sql`
- [ ] `data/cleaned/*.csv` — dữ liệu clean
- [ ] `docs/04_Data_Preprocessing.md`
- [ ] `docs/05_Data_Warehouse.md`

### Phase 4

- [ ] `notebooks/01_data_overview.ipynb`
- [ ] `notebooks/02_trend_analysis.ipynb`
- [ ] `notebooks/03_school_analysis.ipynb`
- [ ] `notebooks/04_major_analysis.ipynb`
- [ ] `notebooks/05_subject_group_analysis.ipynb`
- [ ] `docs/06_Exploratory_Data_Analysis.md`

### Phase 5

- [ ] `src/mining/clustering.py`
- [ ] `src/mining/association_rules.py`
- [ ] `src/mining/forecasting.py`
- [ ] `src/recommendation/recommender.py`
- [ ] `src/recommendation/scorer.py`
- [ ] `notebooks/06_clustering.ipynb`
- [ ] `notebooks/07_association_rules.ipynb`
- [ ] `notebooks/08_forecasting.ipynb`
- [ ] `notebooks/09_recommendation_demo.ipynb`
- [ ] `docs/07_Data_Mining.md`
- [ ] `docs/09_Recommendation_System.md`

### Phase 6

- [ ] `powerbi/dashboard_wireframe.md`
- [ ] `powerbi/dax_measures.md`
- [ ] `powerbi/data_model.md`
- [ ] `data/warehouse/*.csv` — export cho Power BI
- [ ] `docs/08_PowerBI_Dashboard.md`
- [ ] `docs/10_Project_Implementation.md`
- [ ] `docs/12_Future_Work.md`
- [ ] `tests/test_crawler.py`
- [ ] `tests/test_preprocessing.py`
- [ ] `tests/test_mining.py`
- [ ] `tests/test_recommendation.py`
- [ ] pytest pass ≥ 70% coverage

---

## 4. Quản lý Rủi ro

| Rủi ro | Xác suất | Mức độ ảnh hưởng | Biện pháp |
|--------|---------|-----------------|---------|
| Website thay đổi cấu trúc HTML | Cao | Cao | Viết crawler linh hoạt, có fallback parser |
| Dữ liệu năm cũ không còn online | Trung bình | Cao | Tìm nguồn backup (Kaggle, archive.org, báo chí) |
| Dữ liệu thiếu nhiều | Trung bình | Trung bình | Chiến lược imputation rõ ràng, đánh dấu NULL |
| Rate limiting / IP bị block | Cao | Trung bình | Thêm delay, user-agent rotation |
| PostgreSQL connection issues | Thấp | Cao | Kiểm tra kỹ config, có fallback sang CSV |
| Model accuracy thấp | Trung bình | Thấp | Thử nhiều thuật toán, feature engineering tốt |

---

## 5. Phụ thuộc giữa các Phase

```
Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5 ──► Phase 6
(Setup)  (Crawl)     (ETL/DW)    (EDA)       (Mining)    (BI/Final)

Phase 3 phụ thuộc Phase 2 (cần raw data)
Phase 4 phụ thuộc Phase 3 (cần DW)
Phase 5 phụ thuộc Phase 3 & 4 (cần DW + EDA insights)
Phase 6 phụ thuộc Phase 3 & 5 (cần DW + Mining results)
```

---

## 6. Cấu trúc Git

### Nhánh (Branches)

| Branch | Mục đích |
|--------|---------|
| `main` | Code stable, đã review |
| `phase-1-setup` | Phase 1 development |
| `phase-2-crawler` | Phase 2 development |
| `phase-3-etl` | Phase 3 development |
| `phase-4-eda` | Phase 4 development |
| `phase-5-mining` | Phase 5 development |
| `phase-6-bi` | Phase 6 development |

### Commit Convention

```
feat: thêm tính năng mới
fix: sửa lỗi
docs: cập nhật tài liệu
refactor: tái cấu trúc code
test: thêm/sửa tests
data: cập nhật dữ liệu
```

---

## 7. Tài nguyên & Liên kết

| Tài nguyên | Ghi chú |
|-----------|--------|
| PostgreSQL 15 Docs | https://www.postgresql.org/docs/15/ |
| Power BI Documentation | https://learn.microsoft.com/power-bi/ |
| scikit-learn User Guide | https://scikit-learn.org/stable/user_guide.html |
| mlxtend Association Rules | http://rasbt.github.io/mlxtend/user_guide/frequent_patterns/ |
| statsmodels ARIMA | https://www.statsmodels.org/stable/tsa.html |

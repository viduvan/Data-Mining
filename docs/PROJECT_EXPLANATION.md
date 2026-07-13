# 📘 GIẢI THÍCH CHI TIẾT DỰ ÁN — Vietnam University Admission Data Mining

> **Tài liệu tổng hợp giải thích toàn bộ luồng hoạt động của dự án phân tích và khai phá dữ liệu tuyển sinh đại học Việt Nam 2020–2025**

---

## Mục lục

1. [Dashboard Power BI — Mục tiêu & Kỳ vọng cuối cùng](#1-dashboard-power-bi--mục-tiêu--kỳ-vọng-cuối-cùng)
2. [Input / Output hiện tại](#2-input--output-hiện-tại)
3. [Hệ thống gợi ý & Dự đoán — Model, Training, Cách hoạt động](#3-hệ-thống-gợi-ý--dự-đoán--model-training-cách-hoạt-động)
4. [Luồng hoạt động End-to-End](#4-luồng-hoạt-động-end-to-end)
5. [Kiến trúc hệ thống chi tiết](#5-kiến-trúc-hệ-thống-chi-tiết)
6. [Data Warehouse — Star Schema](#6-data-warehouse--star-schema)
7. [ETL Pipeline — Tiền xử lý dữ liệu](#7-etl-pipeline--tiền-xử-lý-dữ-liệu)
8. [Các kỹ thuật Data Mining](#8-các-kỹ-thuật-data-mining)
9. [Công nghệ sử dụng](#9-công-nghệ-sử-dụng)
10. [Hạn chế & Hướng phát triển](#10-hạn-chế--hướng-phát-triển)

---

## 1. Dashboard Power BI — Mục tiêu & Kỳ vọng cuối cùng

### 1.1 Mục tiêu tổng quan

Dashboard Power BI là **sản phẩm cuối cùng hướng tới người dùng** (end-user) của dự án. Mục tiêu chính là cung cấp một giao diện **trực quan, tương tác (interactive)** để các bên liên quan (học sinh, giáo viên, nhà quản lý giáo dục) có thể:

- **Nhìn thấy** xu hướng điểm chuẩn tuyển sinh qua 6 năm (2020–2025) một cách trực quan
- **So sánh** giữa các trường, ngành, khu vực, tổ hợp xét tuyển
- **Dự báo** điểm chuẩn năm tới (2026) dựa trên mô hình đã train
- **Ra quyết định** chọn trường/ngành phù hợp dựa trên dữ liệu thực tế

### 1.2 Cấu trúc 4 trang Dashboard

| Trang | Tên | Mục đích chính | KPIs & Visuals |
|-------|-----|----------------|----------------|
| **1** | Executive Dashboard | Tổng quan toàn cảnh tuyển sinh | Tổng records, số trường, ĐTB điểm chuẩn, YoY change, Top trường, Map phân bố |
| **2** | School Dashboard | Drill-down phân tích theo trường | ĐTB/Max/Min điểm, số ngành, trend 6 năm, so sánh cùng cluster |
| **3** | Major Dashboard | Drill-down phân tích theo ngành | Heatmap điểm chuẩn, Treemap phân bố ngành, Top 10 ngành cao nhất |
| **4** | Forecast Dashboard | Dự báo điểm chuẩn tương lai | Điểm dự báo 2026, Trend tăng/giảm, MAE/RMSE, Actual vs Predicted |

### 1.3 Kỳ vọng cuối cùng

```
┌──────────────────────────────────────────────────────────────┐
│                    KỲ VỌNG CUỐI CÙNG                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Một Dashboard Power BI hoàn chỉnh 4 trang               │
│     → Kết nối trực tiếp PostgreSQL hoặc import CSV           │
│                                                              │
│  2. Interactive: cho phép lọc theo năm, trường, ngành,       │
│     khu vực, tổ hợp xét tuyển                                │
│                                                              │
│  3. Hiển thị KPIs + Charts + Forecast trực quan              │
│     → Học sinh nhập điểm → thấy trường phù hợp              │
│                                                              │
│  4. Publish lên Power BI Service (optional)                  │
│     → Chia sẻ online cho nhiều người xem                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 1.4 Nguồn dữ liệu cho Dashboard

Power BI kết nối dữ liệu theo 1 trong 2 cách:
- **Option A — Import CSV:** Đọc file `data/warehouse/admission_main.csv` (export từ pipeline)
- **Option B — PostgreSQL:** Kết nối trực tiếp database `vietnam_admission_dw` qua PostgreSQL connector

### 1.5 DAX Measures chính

Dashboard sử dụng các DAX measures để tính toán KPIs động:

| Measure | Công thức DAX | Mục đích |
|---------|--------------|----------|
| `Total Records` | `COUNT(fact_admission[admission_key])` | Đếm tổng số bản ghi |
| `Total Schools` | `DISTINCTCOUNT(dim_school[school_name])` | Đếm số trường unique |
| `Avg Score` | `AVERAGE(fact_admission[admission_score])` | Điểm chuẩn trung bình |
| `YoY Score Change` | `[Avg Score] - PrevYearAvg` | So sánh điểm với năm trước |
| `School Score Rank` | `RANKX(ALL(...), [School Avg Score])` | Xếp hạng trường |
| `Forecast Score` | `SELECTEDVALUE(forecast_data[predicted_score])` | Điểm dự báo từ model |

---

## 2. Input / Output hiện tại

### 2.1 INPUT — Dữ liệu đầu vào

#### a) Dữ liệu nguồn (Web Crawling)

| Nguồn | URL | Dữ liệu thu thập |
|-------|-----|------------------|
| thituyensinh.vn | https://thituyensinh.vn/diem-chuan | Điểm chuẩn các trường (nguồn chính) |
| tuyensinh247.com | https://tuyensinh247.com | Điểm chuẩn tổng hợp (fallback) |
| diemthi.hcm.edu.vn | https://diemthi.hcm.edu.vn | Điểm chuẩn khu vực HCM (fallback) |

#### b) Dữ liệu raw sau khi crawl

```
data/raw/
├── admission_2020.csv     (~7.2 MB, ~31,709 records)
├── admission_2021.csv     (~7.2 MB, ~31,709 records)
├── admission_2022.csv     (~7.2 MB, ~31,709 records)
├── admission_2023.csv     (~7.2 MB, ~31,709 records)
├── admission_2024.csv     (~7.2 MB, ~31,709 records)
├── admission_2025.csv     (~7.2 MB, ~31,709 records)
└── schools_info.csv       (~24 KB, thông tin trường)
```

**Tổng quy mô: ~190,254 records × 271 trường × 2,290 ngành × 6 năm**

#### c) Schema dữ liệu raw (mỗi record)

| Cột | Kiểu | Ý nghĩa |
|-----|------|---------|
| `school_code` | string | Mã trường (Bộ GD&ĐT cấp) |
| `school_name` | string | Tên trường đầy đủ |
| `major_code` | string | Mã ngành (7 chữ số) |
| `major_name` | string | Tên ngành |
| `subject_group` | string | Tổ hợp xét tuyển (A00, D01...) |
| `admission_score` | float | **Điểm chuẩn** (0–30) |
| `quota` | int | Chỉ tiêu tuyển sinh |
| `year` | int | Năm tuyển sinh |

#### d) Input cho hệ thống gợi ý (Recommendation)

Khi sử dụng hệ thống gợi ý, user nhập:

| Input | Ví dụ | Mô tả |
|-------|-------|-------|
| `scores` | `[8.5, 9.0, 8.0]` | Điểm 3 môn thi |
| `subject_group` | `"A00"` | Tổ hợp xét tuyển |
| `priority_region` | `"KV2"` | Khu vực ưu tiên |
| `major_group` | `"Kỹ thuật"` | Nhóm ngành muốn tìm (tùy chọn) |

---

### 2.2 OUTPUT — Kết quả đầu ra

#### a) Dữ liệu đã xử lý

| File | Kích thước | Nội dung |
|------|-----------|---------|
| `data/cleaned/admission_cleaned.csv` | — | Dữ liệu sạch sau cleaning |
| `data/processed/admission_processed.csv` | ~56 MB | Dữ liệu + features mới (delta, trend, level) |
| `data/processed/school_clusters.csv` | ~18 KB | Labels cluster cho trường |
| `data/processed/major_clusters.csv` | ~188 KB | Labels cluster cho ngành |
| `data/processed/association_rules.csv` | ~15 KB | Các luật kết hợp |
| `data/processed/score_forecasts.csv` | ~4.8 MB | Dự báo điểm chuẩn 2026 |

#### b) Output Recommendation System

```
══════════════════════════════════════════════════════════════════════
KẾT QUẢ GỢI Ý TRƯỜNG/NGÀNH
Điểm thí sinh: 25.75
══════════════════════════════════════════════════════════════════════

🟢 An toàn (5 kết quả):
----------------------------------------------------------------------
  Đại học FPT                    | CNTT              | Điểm: 22.00 | Safety: +17.0%
  Đại học Điện lực               | Kỹ thuật điện     | Điểm: 21.50 | Safety: +19.8%

🟡 Tương đối (3 kết quả):
----------------------------------------------------------------------
  ĐH Bách khoa Hà Nội           | Kỹ thuật điện     | Điểm: 24.50 | Safety: +5.1%

🟠 Rủi ro (2 kết quả):
----------------------------------------------------------------------
  ĐH Kinh tế Quốc dân           | Kinh tế           | Điểm: 26.50 | Safety: -2.8%
══════════════════════════════════════════════════════════════════════
```

#### c) Output Power BI Dashboard

4 trang Dashboard tương tác với: KPI Cards, Line Charts, Bar Charts, Heatmaps, Scatter Plots, Maps, Forecast Charts.

#### d) Output Data Mining

| Module | Output |
|--------|--------|
| **Clustering** | Phân nhóm trường thành 3–4 cụm (Top / Khá / Trung bình / Đại trà) + biểu đồ PCA 2D |
| **Association Rules** | Danh sách luật kết hợp có ý nghĩa (ví dụ: Sư phạm + Ổn định → Rất cao, Lift=4.457) |
| **Forecasting** | Điểm chuẩn dự báo 2026 cho mỗi cặp trường-ngành + Confidence Interval |

---

## 3. Hệ thống gợi ý & Dự đoán — Model, Training, Cách hoạt động

### 3.1 Tổng quan 3 kỹ thuật Data Mining + 1 hệ thống gợi ý

```
┌─────────────────────────────────────────────────────────────────┐
│              CÁC KỸ THUẬT SỬ DỤNG TRONG DỰ ÁN                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. K-Means Clustering   → Phân nhóm trường/ngành              │
│  2. Apriori Association  → Tìm luật kết hợp                    │
│  3. Linear Reg + ARIMA   → Dự báo điểm chuẩn                   │
│  4. Safety Score System  → Gợi ý trường/ngành theo điểm thi    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 3.2 Kỹ thuật 1: K-Means Clustering (Phân cụm)

#### Mục tiêu
Phân nhóm **trường đại học** và **ngành học** thành các cụm (cluster) có đặc điểm tuyển sinh tương tự nhau.

#### Model: K-Means (scikit-learn)

| Thành phần | Chi tiết |
|-----------|---------|
| **Thuật toán** | K-Means (`sklearn.cluster.KMeans`) |
| **Thư viện** | scikit-learn |
| **File code** | `src/mining/clustering.py` → class `ClusteringAnalyzer` |

#### Features sử dụng (cho phân cụm trường)

| Feature | Cách tính | Ý nghĩa |
|---------|----------|---------|
| `avg_score` | `mean(admission_score)` groupby school | Điểm chuẩn trung bình của trường |
| `max_score` | `max(admission_score)` groupby school | Điểm chuẩn cao nhất |
| `std_score` | `std(admission_score)` groupby school | Độ biến động điểm |
| `num_majors` | `nunique(major_name)` groupby school | Số ngành tuyển sinh |
| `avg_delta` | `mean(delta_score)` groupby school | Biến động điểm TB hàng năm |

#### Quy trình Training

```
Dữ liệu processed (admission_processed.csv)
     │
     ▼
[1] Aggregate: Record-level → School-level
    (groupby school_name, tính mean/max/std/nunique)
     │
     ▼
[2] StandardScaler: Chuẩn hóa features (mean=0, std=1)
    → Đảm bảo các features có cùng scale
     │
     ▼
[3] Xác định K tối ưu:
    ┌─────────────────────────────────────────┐
    │  Thử K = 2, 3, 4, ..., 8               │
    │  Cho mỗi K:                             │
    │    - Fit KMeans(n_clusters=K)            │
    │    - Tính SSE (inertia) → Elbow plot    │
    │    - Tính Silhouette Score               │
    │  Chọn K có Silhouette Score cao nhất     │
    └─────────────────────────────────────────┘
     │
     ▼
[4] Fit K-Means với K tối ưu
    KMeans(n_clusters=K_optimal, random_state=42, n_init=10)
     │
     ▼
[5] Đánh giá:
    - Silhouette Score (mục tiêu ≥ 0.4)
    - Davies-Bouldin Score
     │
     ▼
[6] Gán nhãn cluster:
    - Cluster có avg_score cao nhất → "Trường Top"
    - Cluster tiếp theo             → "Trường Khá"
    - Cluster tiếp theo             → "Trường Trung bình"
    - Cluster thấp nhất             → "Trường Đại trà"
     │
     ▼
[7] Visualization: PCA giảm chiều → Scatter plot 2D
     │
     ▼
[8] Save: school_clusters.csv + clustering_models.pkl
```

#### Kết quả thực tế

| Cluster | Đặc điểm | Phân lớp |
|---------|----------|----------|
| Cluster 0 | Điểm TB thấp (15–18), chỉ tiêu lớn | Trường Đại trà |
| Cluster 1 | Điểm TB khá (18–23) | Trường Khá |
| Cluster 2 | Điểm TB rất cao (23–30) | Trường Top |

---

### 3.3 Kỹ thuật 2: Apriori Association Rules (Luật kết hợp)

#### Mục tiêu
Tìm **quy tắc kết hợp** giữa các thuộc tính tuyển sinh. Ví dụ: "Thí sinh chọn tổ hợp A00 thường đăng ký ngành gì?"

#### Model: Apriori (mlxtend)

| Thành phần | Chi tiết |
|-----------|---------|
| **Thuật toán** | Apriori + Association Rules |
| **Thư viện** | mlxtend |
| **File code** | `src/mining/association_rules.py` → class `AssociationRuleMiner` |

#### Cách chuyển dữ liệu thành Transaction

Mỗi record tuyển sinh được chuyển thành 1 transaction:

```python
# Ví dụ 1 record:
Transaction = {
    "Ngành:Kỹ thuật - Công nghệ",   # Nhóm ngành
    "TH:A00",                         # Tổ hợp xét tuyển
    "Cạnh tranh:Rất cao",            # Mức cạnh tranh
    "Xu hướng:Tăng",                  # Xu hướng điểm
    "Loại:Công lập"                   # Loại trường
}
```

#### Quy trình Mining

```
Dữ liệu processed
     │
     ▼
[1] Chuyển mỗi record → Transaction (tập items)
    (~190,000 transactions)
     │
     ▼
[2] One-hot Encoding (TransactionEncoder)
     │
     ▼
[3] Apriori: Tìm Frequent Itemsets
    min_support = 0.005 (0.5%)
    max_len = 4 items/itemset
     │
     ▼
[4] Sinh Association Rules
    min_confidence = 0.3 (30%)
     │
     ▼
[5] Lọc theo Lift ≥ 1.1
     │
     ▼
[6] Sắp xếp theo Lift giảm dần, lấy top 100
```

#### 3 Metrics quan trọng

| Metric | Công thức | Ý nghĩa |
|--------|----------|---------|
| **Support** | P(A ∩ B) | Tần suất A và B xuất hiện cùng nhau trong toàn bộ transactions |
| **Confidence** | P(B\|A) = P(A∩B) / P(A) | Khi A xảy ra, xác suất B cũng xảy ra là bao nhiêu |
| **Lift** | P(B\|A) / P(B) | Mức tăng xác suất so với ngẫu nhiên. Lift > 1 = có mối liên hệ thực sự |

#### Kết quả thực tế (Top 3 luật theo Lift)

| Luật | Confidence | Lift |
|------|-----------|------|
| `Sư phạm + Ổn định → Cạnh tranh Rất cao` | 0.653 | 4.457 |
| `Sư phạm → Rất cao + Ổn định` | 0.397 | 4.315 |
| `Sư phạm → Cạnh tranh Rất cao` | 0.617 | 4.213 |

**Diễn giải:** Ngành Sư phạm có mức cạnh tranh rất cao và điểm chuẩn ổn định qua các năm, với Lift > 4 cho thấy mối liên hệ rất mạnh.

---

### 3.4 Kỹ thuật 3: Forecasting — Dự báo điểm chuẩn

#### Mục tiêu
Dự báo **điểm chuẩn năm 2026** cho từng cặp (trường, ngành) dựa trên lịch sử 6 năm (2020–2025).

#### Models sử dụng

| Mô hình | Thư viện | Khi nào dùng | Ưu điểm |
|---------|---------|-------------|---------|
| **Linear Regression** | scikit-learn | Luôn chạy (baseline) | Đơn giản, ổn định, phù hợp chuỗi ngắn |
| **ARIMA(1,1,1)** | statsmodels | Khi có ≥ 8 data points | Tốt cho time series, capture autocorrelation |

#### File code
`src/mining/forecasting.py` → class `ScoreForecaster`

#### Quy trình Training & Dự báo

```
Dữ liệu gốc (2020-2025)
     │
     ▼
[1] Group by (school_name, major_name, subject_group)
    → Mỗi nhóm = 1 chuỗi thời gian [score_2020, score_2021, ..., score_2025]
     │
     ▼
[2] Filter: Chỉ giữ nhóm có ≥ 3 data points
     │
     ▼
[3] Với MỖI nhóm, chạy DỰ BÁO:
    ┌─────────────────────────────────────────────┐
    │                                             │
    │  Linear Regression (luôn chạy):             │
    │  ┌─────────────────────────────────────┐    │
    │  │ X = [2020, 2021, ..., 2025]         │    │
    │  │ y = [score_2020, ..., score_2025]   │    │
    │  │ model.fit(X, y)                     │    │
    │  │ pred = model.predict([[2026]])       │    │
    │  │ CI = 1.96 × std(residuals)          │    │
    │  └─────────────────────────────────────┘    │
    │                                             │
    │  ARIMA (chỉ khi ≥ 8 data points):           │
    │  ┌─────────────────────────────────────┐    │
    │  │ model = ARIMA(scores, order=(1,1,1))│    │
    │  │ fitted = model.fit()                │    │
    │  │ forecast = fitted.get_forecast(1)   │    │
    │  │ pred + conf_int                     │    │
    │  └─────────────────────────────────────┘    │
    │                                             │
    │  Chiến lược chọn model:                     │
    │  - Nếu ARIMA khả dụng → ưu tiên ARIMA      │
    │  - Nếu không → dùng Linear Regression       │
    │                                             │
    └─────────────────────────────────────────────┘
     │
     ▼
[4] Output cho mỗi nhóm:
    {
      predicted_score: 25.34,
      lower_bound: 23.12,    // 95% CI
      upper_bound: 27.56,    // 95% CI
      model_used: "LinearRegression",
      trend: "Tăng" / "Giảm" / "Ổn định"
    }
     │
     ▼
[5] Clip điểm dự báo về [0, 30] (điểm hợp lệ)
     │
     ▼
[6] Save: score_forecasts.csv
```

#### Validation (Đánh giá mô hình)

| Phương pháp | Chi tiết |
|------------|---------|
| **Time Series Split** | Train trên 2020–2024, test trên 2025 |
| **Không random split** | Vì vi phạm temporal dependency |
| **Sample** | Đánh giá trên 30 nhóm ngẫu nhiên để tối ưu thời gian |

#### Kết quả đánh giá thực tế

| Metric | Giá trị | Ý nghĩa |
|--------|---------|---------|
| **MAE** | **0.561** | Dự báo lệch trung bình chỉ ±0.56 điểm |
| **RMSE** | **0.697** | Sai số bình phương trung bình thấp |
| **MAPE** | **3.02%** | Sai số % tuyệt đối trung bình cực nhỏ |

> ⚡ **Nhận xét:** Với MAE = 0.56, mô hình dự báo sai lệch trung bình chưa đến 1 điểm so với thực tế. Đây là kết quả tốt cho bài toán dự báo điểm chuẩn.

---

### 3.5 Kỹ thuật 4: Recommendation System — Hệ thống gợi ý

#### Mục tiêu
Giúp thí sinh **chọn trường/ngành phù hợp** dựa trên điểm thi, tổ hợp xét tuyển, và khu vực ưu tiên.

#### Đây KHÔNG phải Machine Learning model

> ⚠️ **Lưu ý quan trọng:** Hệ thống gợi ý **không dùng ML model** mà dùng **rule-based scoring** (tính toán dựa trên quy tắc). Cụ thể, nó tính Safety Score bằng công thức toán học rồi phân loại.

#### File code
- `src/recommendation/scorer.py` → class `SafetyScorer` (tính Safety Score)
- `src/recommendation/recommender.py` → class `AdmissionRecommender` (engine gợi ý)

#### Luồng hoạt động chi tiết

```
INPUT: scores=[8.5, 9.0, 8.0], group="A00", region="KV2"
     │
     ▼
[Bước 1] TÍNH TỔNG ĐIỂM XÉT TUYỂN
     │  Tổng điểm = Tổng 3 môn + Điểm ưu tiên KV + Điểm ưu tiên đối tượng
     │  = (8.5 + 9.0 + 8.0) + 0.25 + 0.0 = 25.75
     │
     │  Bảng điểm ưu tiên khu vực:
     │  ┌─────────┬───────────┐
     │  │ KV1     │ +0.75     │  (Miền núi, hải đảo)
     │  │ KV2-NT  │ +0.50     │  (Nông thôn)
     │  │ KV2     │ +0.25     │  (Ven đô)
     │  │ KV3     │ +0.00     │  (Đô thị)
     │  └─────────┴───────────┘
     │
     ▼
[Bước 2] LỌC CANDIDATES
     │  Từ bảng fact_admission (năm mới nhất = 2025):
     │  - Chỉ lấy ngành có cùng tổ hợp = "A00"
     │  - Chỉ lấy ngành có điểm chuẩn ≤ tổng điểm + 2.0 (buffer rủi ro)
     │    → ≤ 25.75 + 2.0 = 27.75
     │  - (Tùy chọn) Lọc theo nhóm ngành, khu vực trường
     │
     ▼
[Bước 3] TÍNH SAFETY SCORE
     │  Với mỗi candidate:
     │  Safety Score (%) = (Điểm thí sinh - Điểm chuẩn) / Điểm chuẩn × 100
     │
     │  Ví dụ:
     │  - Thí sinh 25.75, ĐC 22.00 → Safety = +17.0% ✅
     │  - Thí sinh 25.75, ĐC 25.00 → Safety = +3.0%  ⚠️
     │  - Thí sinh 25.75, ĐC 27.00 → Safety = -4.6%  🟠
     │
     ▼
[Bước 4] PHÂN LOẠI MỨC AN TOÀN
     │  ┌──────────────────────┬──────────────┬───────────────────────┐
     │  │ Mức                  │ Safety Score │ Ý nghĩa               │
     │  ├──────────────────────┼──────────────┼───────────────────────┤
     │  │ 🟢 An toàn           │ ≥ +10%       │ Điểm cao hơn ≥10%    │
     │  │ 🟡 Tương đối         │ 0% → +10%    │ Vừa đủ hoặc hơi cao  │
     │  │ 🟠 Rủi ro            │ -10% → 0%    │ Thấp hơn, rủi ro     │
     │  │ 🔴 Không khuyến nghị │ < -10%       │ Quá thấp, trượt cao  │
     │  └──────────────────────┴──────────────┴───────────────────────┘
     │
     ▼
[Bước 5] ENRICH (BỔ SUNG THÔNG TIN)
     │  + Gắn cluster_label từ kết quả Clustering (nếu có)
     │    → "Trường Top", "Trường Khá"...
     │  + Gắn forecast_trend từ kết quả Forecasting (nếu có)
     │    → "📈 Tăng", "📉 Giảm", "➡️ Ổn định"
     │
     ▼
[Bước 6] SORT & RETURN
     │  Sắp xếp: An toàn → Tương đối → Rủi ro
     │  Trong cùng nhóm: điểm chuẩn cao nhất trước
     │
     ▼
OUTPUT: DataFrame với top_n kết quả
```

---

## 4. Luồng hoạt động End-to-End

### Sơ đồ tổng quát

```
╔══════════════════════════════════════════════════════════════════╗
║                    LUỒNG DỮ LIỆU END-TO-END                    ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  [Bước 1] WEB CRAWLING                                          ║
║  Website Bộ GD&ĐT, thituyensinh.vn, tuyensinh247.com           ║
║      │ HTTP/HTML Parsing (requests + BeautifulSoup)              ║
║      ▼                                                          ║
║  data/raw/*.csv (6 file CSV × ~31K records)                      ║
║                                                                  ║
║  [Bước 2] ETL PIPELINE                                          ║
║      │ Cleaning → Normalization → Feature Engineering            ║
║      ▼                                                          ║
║  data/cleaned/admission_cleaned.csv (dữ liệu sạch)              ║
║  data/processed/admission_processed.csv (+ features mới)         ║
║                                                                  ║
║  [Bước 3] DATA WAREHOUSE                                        ║
║      │ Load vào PostgreSQL (Star Schema)                         ║
║      ▼                                                          ║
║  PostgreSQL: vietnam_admission_dw                                ║
║  ┌──────────────────────────────────────────────┐                ║
║  │ 1 Fact Table: fact_admission                 │                ║
║  │ 5 Dim Tables: school, major, year,           │                ║
║  │               subject_group, region          │                ║
║  └──────────────────────────────────────────────┘                ║
║                                                                  ║
║  [Bước 4] EDA (Exploratory Data Analysis)                        ║
║      │ 5 Jupyter Notebooks (overview, trends, school, major)     ║
║      ▼                                                          ║
║  Insights + Visualizations (matplotlib, seaborn, plotly)         ║
║                                                                  ║
║  [Bước 5] DATA MINING                                           ║
║      │ 3 kỹ thuật song song                                     ║
║      ├── K-Means Clustering → school_clusters.csv                ║
║      ├── Apriori Association → association_rules.csv             ║
║      └── LinReg + ARIMA     → score_forecasts.csv                ║
║                                                                  ║
║  [Bước 6] POWER BI DASHBOARD                                    ║
║      │ Kết nối PostgreSQL hoặc CSV                               ║
║      ▼                                                          ║
║  4 trang Dashboard tương tác                                     ║
║                                                                  ║
║  [Bước 7] RECOMMENDATION SYSTEM                                 ║
║      │ Input: điểm thi + tổ hợp + khu vực                       ║
║      ▼                                                          ║
║  Output: Danh sách trường/ngành + Safety Score                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### Lệnh chạy từng bước

| Bước | Lệnh | Mô tả |
|------|-------|-------|
| 1 | `python -m src.crawler.run_crawler` | Crawl dữ liệu |
| 2 | `python -m src.preprocessing.etl_pipeline` | ETL Pipeline |
| 3 | `psql -f sql/create_schema.sql` | Tạo schema DW |
| 4 | `jupyter notebook notebooks/` | Chạy EDA |
| 5a | `python -m src.mining.clustering` | Phân cụm |
| 5b | `python -m src.mining.association_rules` | Luật kết hợp |
| 5c | `python -m src.mining.forecasting` | Dự báo |
| 6 | `python -m src.preprocessing.export_powerbi` | Export cho Power BI |
| 7 | `python -m src.recommendation.recommender --scores 8.5 9.0 8.0 --group A00` | Gợi ý |

---

## 5. Kiến trúc hệ thống chi tiết

### 5.1 Mô hình Pipeline 7 lớp

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: DATA SOURCES (Web)                                     │
│   thituyensinh.vn │ tuyensinh247.com │ diemthi.hcm.edu.vn      │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ Layer 2: DATA COLLECTION (Python Crawler)                       │
│   BaseCrawler → AdmissionCrawler + SchoolInfoCrawler            │
│   Rate limiting, Retry, User-Agent rotation, Checkpoint         │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ Layer 3: DATA CLEANING & ETL (pandas + numpy)                   │
│   Normalize → Dedup → Missing → Feature Engineering → Validate  │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ Layer 4: DATA WAREHOUSE (PostgreSQL Star Schema)                │
│   1 Fact Table + 5 Dimension Tables                             │
└────────────┬──────────────────────────────┬─────────────────────┘
             ▼                              ▼
┌────────────────────────┐    ┌──────────────────────────────────┐
│ Layer 5: EDA           │    │ Layer 5: DATA MINING             │
│ Jupyter Notebooks      │    │ Clustering + Association + Fore. │
└────────────┬───────────┘    └──────────────┬───────────────────┘
             └──────────────┬────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Layer 6: BUSINESS INTELLIGENCE (Power BI Dashboard)             │
│   4 trang: Executive │ School │ Major │ Forecast                │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ Layer 7: DECISION SUPPORT (Recommendation System)               │
│   Input: Điểm thi → Output: Danh sách trường/ngành + Safety    │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Cấu trúc mã nguồn

```
src/
├── crawler/                      # Layer 2: Thu thập dữ liệu
│   ├── base_crawler.py           # Abstract class (fetch, parse, retry)
│   ├── admission_crawler.py      # Crawl điểm chuẩn theo năm
│   ├── school_info_crawler.py    # Crawl thông tin trường
│   ├── config.py                 # Cấu hình URL, User-Agent pool
│   ├── utils.py                  # Helper functions
│   └── run_crawler.py            # CLI entry point
│
├── preprocessing/                # Layer 3: ETL Pipeline
│   ├── data_cleaner.py           # Cleaning: normalize, dedup, missing
│   ├── feature_engineering.py    # Tạo features mới (delta, level, group)
│   ├── validators.py             # Data quality checks
│   ├── etl_pipeline.py           # Orchestrator pipeline
│   ├── db_loader.py              # Load vào PostgreSQL
│   └── export_powerbi.py         # Export CSV cho Power BI
│
├── mining/                       # Layer 5: Data Mining
│   ├── clustering.py             # K-Means Clustering
│   ├── association_rules.py      # Apriori Association Rules
│   └── forecasting.py            # Linear Regression + ARIMA
│
└── recommendation/               # Layer 7: Recommendation System
    ├── scorer.py                  # SafetyScorer: tính Safety Score
    └── recommender.py            # AdmissionRecommender: engine gợi ý
```

---

## 6. Data Warehouse — Star Schema

### Sơ đồ quan hệ

```
                      ┌──────────────┐
                      │   dim_year   │
                      │──────────────│
                      │ year_key PK  │
                      │ year         │
                      │ period_label │
                      └──────┬───────┘
                             │ FK
  ┌──────────────┐    ┌──────┴───────────┐    ┌────────────────┐
  │  dim_school  │    │  fact_admission  │    │   dim_major    │
  │──────────────│    │──────────────────│    │────────────────│
  │ school_key PK├───▶│ admission_key PK │◀───┤ major_key PK   │
  │ school_name  │    │ admission_score  │    │ major_name     │
  │ school_type  │    │ quota            │    │ major_group    │
  │ region_code  │    │ delta_score      │    └────────────────┘
  └──────┬───────┘    │ competition_level│
         │            └──────┬───────────┘
  ┌──────┴───────┐           │            ┌──────────────────┐
  │  dim_region  │           └───────────▶│dim_subject_group │
  │──────────────│                        │──────────────────│
  │ region_key   │                        │ group_code (A00) │
  │ region_name  │                        │ subject_1/2/3    │
  └──────────────┘                        └──────────────────┘
```

**Tại sao dùng Star Schema?**
- Tối ưu cho truy vấn phân tích (OLAP)
- Power BI tự detect relationships qua Foreign Keys
- Dễ aggregate theo nhiều chiều: năm, trường, ngành, khu vực, tổ hợp

---

## 7. ETL Pipeline — Tiền xử lý dữ liệu

### Quy trình 5 bước

| Bước | Module | Công việc chính |
|------|--------|----------------|
| **1. Load** | `data_cleaner.py` | Đọc 6 file CSV raw, merge thành 1 DataFrame |
| **2. Clean** | `data_cleaner.py` | Normalize Unicode, chuẩn hóa tên trường/ngành, xử lý missing, dedup |
| **3. Feature** | `feature_engineering.py` | Tạo `delta_score`, `competition_level`, `major_group`, `score_trend` |
| **4. Validate** | `validators.py` | Kiểm tra data quality, log vi phạm |
| **5. Export** | `db_loader.py` | Load vào PostgreSQL Star Schema + export CSV |

### Features được tạo ra

| Feature | Công thức | Ý nghĩa |
|---------|----------|---------|
| `delta_score` | `score[t] - score[t-1]` | Chênh lệch điểm so với năm trước |
| `delta_score_pct` | `delta / score[t-1] × 100` | % thay đổi |
| `competition_level` | ≥25: Rất cao, ≥22: Cao, ≥18: TB, <18: Thấp | Mức cạnh tranh |
| `score_trend` | Δ ≥ 0.5: Tăng, Δ ≤ -0.5: Giảm, else: Ổn định | Xu hướng điểm |
| `major_group` | Keyword matching trên tên ngành | Nhóm ngành (7 nhóm) |

### Thống kê Cleaning

```
Raw records      : 190,254
Duplicates xóa   : 2,580
Clean records    : 187,674
Retention rate   : 98.6%
```

---

## 8. Các kỹ thuật Data Mining

### Tóm tắt so sánh

| Kỹ thuật | Thuật toán | Thư viện | Input | Output | Mục đích chính |
|----------|-----------|---------|-------|--------|---------------|
| **Clustering** | K-Means | scikit-learn | Vector features trường/ngành | Cluster labels (Top/Khá/TB/Đại trà) | Phân nhóm để so sánh |
| **Association** | Apriori | mlxtend | Transaction matrix | Luật kết hợp (Support, Confidence, Lift) | Tìm mối quan hệ ẩn |
| **Forecasting** | LinReg + ARIMA | sklearn + statsmodels | Time series điểm chuẩn | Dự báo 2026 + CI | Dự báo tương lai |
| **Recommendation** | Rule-based | pandas (tự code) | Điểm thi + tổ hợp | Ranked list + Safety Score | Hỗ trợ quyết định |

### Notebooks Mining

| Notebook | Nội dung |
|----------|---------|
| `06_clustering.ipynb` | Elbow plot, PCA scatter, cluster profiles |
| `07_association_rules.ipynb` | Top rules, network graph |
| `08_forecasting.ipynb` | Model comparison, actual vs predicted |
| `09_recommendation_demo.ipynb` | Demo gợi ý trường/ngành |

---

## 9. Công nghệ sử dụng

| Layer | Công nghệ | Phiên bản | Vai trò |
|-------|----------|-----------|---------|
| Data Collection | Python, requests, BeautifulSoup4, Selenium | Python 3.10+ | Crawl web |
| ETL | pandas, numpy, SQLAlchemy, loguru | pandas 2.0+ | Xử lý dữ liệu |
| Data Warehouse | PostgreSQL | 15+ | Lưu trữ OLAP |
| EDA | Jupyter, matplotlib, seaborn, plotly | Latest | Phân tích khám phá |
| Data Mining | scikit-learn, mlxtend, statsmodels | Latest | Khai phá dữ liệu |
| BI Dashboard | Microsoft Power BI Desktop | Latest | Trực quan hóa |
| Version Control | Git | 2.x | Quản lý mã nguồn |
| Testing | pytest | Latest | Kiểm thử |

---

## 10. Hạn chế & Hướng phát triển

### 10.1 Hạn chế hiện tại

| Hạn chế | Giải thích |
|---------|-----------|
| Ít data points cho Forecasting | 6 năm (2020–2025) → ARIMA bị hạn chế, chủ yếu dùng Linear Regression |
| Association Rules phụ thuộc ngưỡng | Kết quả thay đổi khi thay đổi min_support, min_confidence |
| Clustering nhạy với outliers | Cần StandardScaler, kết quả phụ thuộc random_state |
| Không capture yếu tố ngoài | Chính sách mới Bộ GD&ĐT, COVID, thay đổi phương thức xét tuyển |
| Chỉ xét tuyển bằng điểm thi THPT | Không bao gồm xét học bạ, ĐGNL, ĐGTD |
| Recommendation chưa cá nhân hóa sâu | Chỉ dựa trên điểm thi + tổ hợp, chưa có sở thích/mục tiêu |
| CLI interface | Chưa có Web UI cho recommendation |

### 10.2 Hướng phát triển tương lai

| Hướng | Mô tả |
|-------|-------|
| **Web Application** | Xây dựng Flask/Django web app cho Recommendation System |
| **Deep Learning** | Dùng LSTM/Transformer cho forecasting |
| **Thêm phương thức xét tuyển** | Xét học bạ, ĐGNL, ĐGTD |
| **Cá nhân hóa** | Thêm sở thích, năng lực, mục tiêu nghề nghiệp |
| **Real-time updates** | Tự động crawl khi Bộ GD&ĐT công bố dữ liệu mới |
| **Mobile App** | Phát triển ứng dụng di động |
| **NLP** | Phân tích sentiment từ review trường ĐH |

---

## Phụ lục: Danh sách tài liệu dự án

| # | File | Nội dung |
|---|------|---------|
| 00 | `docs/00_Project_Overview.md` | Tổng quan dự án |
| 01 | `docs/01_Problem_Statement.md` | Phân tích bài toán |
| 02 | `docs/02_System_Architecture.md` | Kiến trúc hệ thống |
| 03 | `docs/03_Data_Collection.md` | Thu thập dữ liệu |
| 04 | `docs/04_Data_Preprocessing.md` | ETL & Cleaning |
| 05 | `docs/05_Data_Warehouse.md` | Star Schema PostgreSQL |
| 06 | `docs/06_Exploratory_Data_Analysis.md` | EDA |
| 07 | `docs/07_Data_Mining.md` | Thuật toán & kết quả Mining |
| 08 | `docs/08_PowerBI_Dashboard.md` | Thiết kế Dashboard |
| 09 | `docs/09_Recommendation_System.md` | Hệ thống gợi ý |
| 10 | `docs/10_Project_Implementation.md` | Hướng dẫn triển khai |
| 11 | `docs/11_Project_Management.md` | Timeline & quản lý |
| 12 | `docs/12_Future_Work.md` | Định hướng mở rộng |
| 13 | `docs/13_Data_Mining_Report.md` | Báo cáo Data Mining |

---

*Tài liệu được tạo tự động từ phân tích mã nguồn và tài liệu dự án — Vietnam University Admission Data Mining*

# 07_Data_Mining.md

# Khai phá Dữ liệu — Data Mining

---

## 1. Tổng quan

Phase Data Mining áp dụng 3 kỹ thuật khai phá dữ liệu trên tập dữ liệu tuyển sinh đã xử lý:

| # | Kỹ thuật | Thuật toán | Mục tiêu |
|---|---------|-----------|---------|
| 1 | Clustering (Phân cụm) | K-Means | Phân nhóm trường/ngành theo đặc điểm tuyển sinh |
| 2 | Association Rule Mining | Apriori | Tìm quy tắc kết hợp giữa các thuộc tính |
| 3 | Forecasting (Dự báo) | Linear Regression + ARIMA | Dự báo điểm chuẩn năm tới |

**Modules:**
- `src/mining/clustering.py`
- `src/mining/association_rules.py`
- `src/mining/forecasting.py`

---

## 2. Clustering — Phân cụm K-Means

### 2.1 Mục tiêu

Phân nhóm các **trường đại học** thành các cluster dựa trên đặc điểm tuyển sinh, giúp:
- Xác định nhóm trường "top", "khá", "trung bình"
- So sánh trường với các trường tương tự
- Hỗ trợ Recommendation System phân loại kết quả

### 2.2 Features sử dụng

| Feature | Mô tả | Nguồn |
|---------|-------|-------|
| `avg_score` | Điểm chuẩn trung bình | Aggregate từ fact_admission |
| `max_score` | Điểm chuẩn cao nhất | Aggregate |
| `avg_delta` | Biến động điểm TB | Feature engineering |
| `num_majors` | Số ngành tuyển | Count distinct |
| `avg_quota` | Chỉ tiêu trung bình | Aggregate |

### 2.3 Tiền xử lý

1. **Aggregate:** Từ record-level → school-level
2. **StandardScaler:** Chuẩn hóa features (mean=0, std=1)
3. **Handle NaN:** Loại bỏ hoặc fill median

### 2.4 Xác định K tối ưu

| Phương pháp | Cách dùng |
|------------|----------|
| Elbow Method | Vẽ SSE (inertia) vs K, chọn "khuỷu tay" |
| Silhouette Score | Chọn K có silhouette score cao nhất |

**Range K:** 2 → 8

### 2.5 Kết quả dự kiến

| Cluster | Đặc điểm | Ví dụ trường |
|---------|----------|-------------|
| 0 — Top | Điểm ≥25, nhiều ngành, cạnh tranh rất cao | HUST, NEU, FTU |
| 1 — Khá | Điểm 20–25, cạnh tranh cao | UEH, PTIT, UIT |
| 2 — Trung bình | Điểm 16–20, cạnh tranh TB | Đại học địa phương |
| 3 — Thấp | Điểm <16, chỉ tiêu lớn, cạnh tranh thấp | Một số trường tư thục |

### 2.6 Visualization

- **PCA 2D Scatter:** Giảm chiều về 2D, mỗi điểm = 1 trường, màu = cluster
- **Radar Chart:** Profile trung bình mỗi cluster
- **Centroid Analysis Table:** Giá trị trung bình mỗi feature theo cluster

### 2.7 Module

```python
from src.mining.clustering import ClusteringAnalyzer

analyzer = ClusteringAnalyzer(df_processed)
schools_clustered = analyzer.cluster_schools(k=4)
analyzer.plot_elbow(max_k=8, save_path="images/elbow.png")
analyzer.plot_clusters_2d(save_path="images/clusters_2d.png")
```

---

## 3. Association Rule Mining — Luật kết hợp Apriori

### 3.1 Mục tiêu

Tìm **quy tắc kết hợp** (association rules) giữa các thuộc tính tuyển sinh:
- "Thí sinh chọn tổ hợp A00 thường đăng ký ngành gì?"
- "Trường ở khu vực Bắc thường tuyển ngành gì?"
- "Ngành nào thường đi cùng mức cạnh tranh nào?"

### 3.2 Transaction Design

Mỗi record tuyển sinh được chuyển thành 1 transaction chứa các item:

```
Transaction = {
    "Ngành:Kỹ thuật - Công nghệ",
    "TH:A00",
    "KV:Bắc",
    "Cạnh tranh:Rất cao",
    "Xu hướng:Tăng"
}
```

### 3.3 Tham số

| Tham số | Giá trị | Ý nghĩa |
|---------|---------|---------|
| `min_support` | 0.05 (5%) | Item set xuất hiện ≥5% transactions |
| `min_confidence` | 0.5 (50%) | Độ tin cậy ≥50% |
| `min_lift` | 1.2 | Lift ≥1.2 (mối liên hệ thực sự, không ngẫu nhiên) |

### 3.4 Metrics

| Metric | Công thức | Ý nghĩa |
|--------|----------|---------|
| **Support** | P(A ∩ B) | Tần suất xuất hiện cùng nhau |
| **Confidence** | P(B\|A) = P(A ∩ B) / P(A) | Xác suất B xảy ra khi A xảy ra |
| **Lift** | P(B\|A) / P(B) | Mức tăng xác suất so với ngẫu nhiên |

### 3.5 Kết quả dự kiến

| Luật | Confidence | Lift |
|------|-----------|------|
| {A00} → {Kỹ thuật - Công nghệ} | 0.65 | 1.8 |
| {D01, KV:Bắc} → {Kinh tế - Quản trị} | 0.58 | 1.5 |
| {Cạnh tranh:Rất cao} → {KV:Bắc} | 0.55 | 1.3 |

### 3.6 Module

```python
from src.mining.association_rules import AssociationRuleMiner

miner = AssociationRuleMiner(df_processed)
rules = miner.mine_rules(min_support=0.05, min_confidence=0.5)
miner.print_rules(rules, top_n=20)
```

---

## 4. Forecasting — Dự báo điểm chuẩn

### 4.1 Mục tiêu

Dự báo **điểm chuẩn năm tới** (2026) cho từng cặp (trường, ngành) dựa trên lịch sử 2020–2025.

### 4.2 Thuật toán

| Mô hình | Thư viện | Ưu điểm | Nhược điểm |
|---------|---------|---------|-----------|
| **Linear Regression** | scikit-learn | Đơn giản, baseline | Không capture tính mùa vụ |
| **ARIMA** | statsmodels | Tốt cho time series | Cần ≥5 data points |

### 4.3 Quy trình

```
Dữ liệu gốc (2020-2025)
    │
    ▼
Group by (school, major)
    │
    ▼
Filter: ≥ 3 data points
    │
    ▼
┌──────────────┐    ┌──────────────┐
│   Linear     │    │    ARIMA     │
│  Regression  │    │  (1,1,0)     │
└──────┬───────┘    └──────┬───────┘
       │                    │
       ▼                    ▼
    Predict 2026         Predict 2026
       │                    │
       └────────┬───────────┘
                ▼
         Ensemble (nếu cả 2 khả dụng)
                │
                ▼
         Forecast Result + Confidence Interval
```

### 4.4 Metrics đánh giá

| Metric | Công thức | Mục tiêu |
|--------|----------|---------|
| **MAE** | Σ\|actual - predicted\| / n | Càng nhỏ càng tốt |
| **RMSE** | √(Σ(actual - predicted)² / n) | Càng nhỏ càng tốt |
| **MAPE** | Σ\|actual - predicted\| / actual / n × 100 | <10% = tốt |
| **R²** | 1 - SS_res / SS_total | >0.7 = tốt |

### 4.5 Validation

- **Time Series Split:** Train trên 2020–2024, test trên 2025
- Không dùng random split (vi phạm temporal dependency)

### 4.6 Module

```python
from src.mining.forecasting import ScoreForecaster

forecaster = ScoreForecaster(df_processed)
result = forecaster.forecast_school_major(
    school_name="Đại học Bách khoa Hà Nội",
    major_name="Công nghệ thông tin",
    forecast_year=2026
)
print(f"Dự báo: {result['predicted_score']:.2f}")
```

---

## 5. Notebooks Mining

| # | Notebook | Nội dung |
|---|----------|---------|
| 6 | `06_clustering.ipynb` | Elbow plot, PCA scatter, cluster profiles |
| 7 | `07_association_rules.ipynb` | Top rules, network graph |
| 8 | `08_forecasting.ipynb` | Model comparison, actual vs predicted |

---

## 6. Hạn chế & Lưu ý

| Hạn chế | Giải thích |
|---------|-----------|
| Ít data points cho forecasting | 6 năm (2020–2025) → ARIMA bị hạn chế |
| Association rules phụ thuộc discretization | Kết quả thay đổi khi thay đổi ngưỡng binning |
| Clustering nhạy với outliers | Cần StandardScaler trước khi clustering |
| Không capture yếu tố ngoài | Chính sách mới của Bộ GD&ĐT, dịch COVID... |

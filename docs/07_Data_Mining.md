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

### 2.5 Kết quả thực tế

| Cluster | Đặc điểm | Phân lớp |
|---------|----------|-------------|
| Cluster 0 | Điểm trung bình thấp (15–18), chỉ tiêu lớn | Trường Đại trà |
| Cluster 1 | Điểm trung bình khá (18–23) | Trường Khá |
| Cluster 2 | Điểm trung bình rất cao (23–30) | Trường Top |

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
| `min_support` | 0.005 (0.5%) | Item set xuất hiện ≥0.5% transactions (tương đương ~900 dòng) |
| `min_confidence` | 0.3 (30%) | Độ tin cậy ≥30% |
| `min_lift` | 1.1 | Lift ≥1.1 (mối liên hệ thực sự, không ngẫu nhiên) |

### 3.4 Metrics

| Metric | Công thức | Ý nghĩa |
|--------|----------|---------|
| **Support** | P(A ∩ B) | Tần suất xuất hiện cùng nhau |
| **Confidence** | P(B\|A) = P(A ∩ B) / P(A) | Xác suất B xảy ra khi A xảy ra |
| **Lift** | P(B\|A) / P(B) | Mức tăng xác suất so với ngẫu nhiên |

### 3.5 Kết quả thực tế (Top 3 Luật kết hợp theo Lift)

| Luật | Confidence | Lift | Support |
|------|-----------|------|---------|
| `Ngành:Sư phạm - Giáo dục + Xu hướng:Ổn định → Cạnh tranh:Rất cao` | 0.653 | 4.457 | 0.022 |
| `Ngành:Sư phạm - Giáo dục → Cạnh tranh:Rất cao + Xu hướng:Ổn định` | 0.397 | 4.315 | 0.022 |
| `Ngành:Sư phạm - Giáo dục → Cạnh tranh:Rất cao` | 0.617 | 4.213 | 0.035 |

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

### 4.4 Kết quả đánh giá sai số thực tế

| Metric | Giá trị thực tế đạt được | Ý nghĩa |
|--------|--------------------------|---------|
| **MAE** | **0.561** | Điểm chuẩn dự báo chỉ lệch trung bình ±0.56 điểm |
| **RMSE** | **0.697** | Sai số bình phương trung bình thấp |
| **MAPE** | **3.02%** | Sai số phần trăm tuyệt đối trung bình cực nhỏ |

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

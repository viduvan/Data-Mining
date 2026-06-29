# 09_Recommendation_System.md

# Hệ thống Gợi ý Trường/Ngành — Recommendation System

---

## 1. Tổng quan

Hệ thống gợi ý (Recommendation System) hỗ trợ thí sinh **chọn trường/ngành phù hợp** dựa trên điểm thi, tổ hợp xét tuyển và khu vực ưu tiên.

### Đặc điểm:
- **Input:** Điểm 3 môn + tổ hợp + khu vực ưu tiên
- **Output:** Danh sách trường/ngành xếp hạng theo mức an toàn
- **Tích hợp:** Cluster labels + Forecast trends (nếu có)
- **Interface:** CLI hoặc import Python module

---

## 2. Kiến trúc Hệ thống

```
                 ┌──────────────────┐
                 │   INPUT          │
                 │ - 3 điểm thi     │
                 │ - Tổ hợp (A00)   │
                 │ - Khu vực (KV2)  │
                 └────────┬─────────┘
                          ▼
                 ┌──────────────────┐
                 │ COMPUTE SCORE    │
                 │ Tổng = 3 môn +   │
                 │ điểm ưu tiên KV  │
                 │ + đối tượng ƯT   │
                 └────────┬─────────┘
                          ▼
                 ┌──────────────────┐
                 │ FILTER CANDIDATES│
                 │ - Tổ hợp match   │
                 │ - Năm mới nhất   │
                 │ - Nhóm ngành     │
                 │ - Khu vực trường │
                 └────────┬─────────┘
                          ▼
                 ┌──────────────────┐
                 │ SAFETY SCORING   │
                 │ Safety% =        │
                 │ (Điểm TS - ĐC)  │
                 │ / ĐC × 100      │
                 └────────┬─────────┘
                          ▼
                 ┌──────────────────┐
                 │ CLASSIFY + RANK  │
                 │ 🟢 An toàn       │
                 │ 🟡 Tương đối     │
                 │ 🟠 Rủi ro        │
                 │ 🔴 Không k.nghị  │
                 └────────┬─────────┘
                          ▼
                 ┌──────────────────┐
                 │ ENRICH (optional)│
                 │ + Cluster label  │
                 │ + Forecast trend │
                 └────────┬─────────┘
                          ▼
                 ┌──────────────────┐
                 │    OUTPUT        │
                 │ Danh sách ranked │
                 │ trường/ngành     │
                 └──────────────────┘
```

---

## 3. Chi tiết Logic

### 3.1 Tính tổng điểm xét tuyển

```
Tổng điểm = Điểm 3 môn + Điểm ưu tiên khu vực + Điểm ưu tiên đối tượng
```

**Điểm ưu tiên khu vực (theo quy định Bộ GD&ĐT):**

| Khu vực | Điểm cộng |
|---------|----------|
| KV1 (Nông thôn miền núi, hải đảo) | +0.75 |
| KV2-NT (Ngoại thành, nông thôn) | +0.50 |
| KV2 (Vùng ven đô thị) | +0.25 |
| KV3 (Đô thị) | +0.00 |

**Điểm ưu tiên đối tượng:**

| Đối tượng | Điểm cộng |
|----------|----------|
| UT1 (Anh hùng, Bà mẹ VN anh hùng...) | +2.0 |
| UT2 (Đối tượng ưu tiên 2) | +1.0 |
| Bình thường | +0.0 |

### 3.2 Tính Safety Score

```
Safety Score (%) = (Điểm thí sinh - Điểm chuẩn) / Điểm chuẩn × 100
```

**Ví dụ:**
- Thí sinh 25.5 điểm, điểm chuẩn 23.0 → Safety = +10.9% (**An toàn**)
- Thí sinh 25.5 điểm, điểm chuẩn 25.0 → Safety = +2.0% (**Tương đối**)
- Thí sinh 25.5 điểm, điểm chuẩn 27.0 → Safety = -5.6% (**Rủi ro**)

### 3.3 Phân loại mức an toàn

| Mức | Safety Score | Ý nghĩa |
|-----|-------------|---------|
| 🟢 **An toàn** | ≥ 10% | Điểm thí sinh cao hơn ≥10% so với điểm chuẩn |
| 🟡 **Tương đối** | 0% ≤ Safety < 10% | Vừa đủ hoặc hơi cao hơn điểm chuẩn |
| 🟠 **Rủi ro** | -10% ≤ Safety < 0% | Thấp hơn điểm chuẩn, rủi ro trượt |
| 🔴 **Không khuyến nghị** | < -10% | Quá thấp, khả năng trượt rất cao |

### 3.4 Lọc Candidates

| Bộ lọc | Logic |
|--------|------|
| Tổ hợp xét tuyển | Chỉ lấy ngành có cùng tổ hợp |
| Năm tham chiếu | Mặc định: năm mới nhất (2025) |
| Biên độ rủi ro | Cho phép tìm ngành có ĐC cao hơn tối đa +2.0 điểm |
| Nhóm ngành (optional) | Lọc theo "Kỹ thuật", "Kinh tế"... |
| Khu vực trường (optional) | Lọc theo "Bắc", "Trung", "Nam" |

---

## 4. Cách sử dụng

### 4.1 CLI (Command Line)

```bash
python -m src.recommendation.recommender \
  --scores 8.5 9.0 8.0 \
  --group A00 \
  --region KV2 \
  --top 15
```

**Output mẫu:**
```
══════════════════════════════════════════════════════════════════════
KẾT QUẢ GỢI Ý TRƯỜNG/NGÀNH
Điểm thí sinh: 25.75
══════════════════════════════════════════════════════════════════════

🟢 An toàn (5 kết quả):
----------------------------------------------------------------------
  Đại học FPT                              | CNTT                      | Điểm: 22.00 | Safety: +17.0%
  Đại học Điện lực                          | Kỹ thuật điện             | Điểm: 21.50 | Safety: +19.8%

🟡 Tương đối (3 kết quả):
----------------------------------------------------------------------
  Đại học Bách khoa Hà Nội                 | Kỹ thuật điện             | Điểm: 24.50 | Safety: +5.1%
  Đại học Kinh tế Quốc dân                 | Kinh tế                   | Điểm: 26.50 | Safety: -2.8%

══════════════════════════════════════════════════════════════════════
```

### 4.2 Python Module

```python
from src.recommendation.recommender import AdmissionRecommender

# Từ CSV
recommender = AdmissionRecommender.from_csv("data/processed/admission_processed.csv")

# Từ PostgreSQL
recommender = AdmissionRecommender.from_db()

# Gợi ý
results = recommender.recommend(
    scores=[8.5, 9.0, 8.0],
    subject_group="A00",
    priority_region="KV2",
    major_group="Kỹ thuật - Công nghệ",
    top_n=20,
    include_risky=True,
)

# In kết quả
recommender.print_results(results)
```

---

## 5. Tích hợp với Mining

### 5.1 Cluster Integration

Khi có cluster data, kết quả gợi ý sẽ bao gồm thêm cột `cluster_label`:
- "Nhóm trường Top" → Trường top, cạnh tranh rất cao
- "Nhóm trường Khá" → Trường tầm trung-khá
- Giúp thí sinh hiểu bối cảnh trường

### 5.2 Forecast Integration

Khi có forecast data, kết quả gợi ý sẽ bao gồm:
- `forecast_score`: Điểm chuẩn dự báo năm tới
- `forecast_trend`: Xu hướng tăng/giảm/ổn định
- Giúp thí sinh đánh giá rủi ro tương lai

---

## 6. Modules

| File | Vai trò |
|------|--------|
| `src/recommendation/__init__.py` | Package init |
| `src/recommendation/scorer.py` | SafetyScorer — Tính safety score & phân loại |
| `src/recommendation/recommender.py` | AdmissionRecommender — Engine gợi ý chính |

---

## 7. Hạn chế & Hướng cải thiện

| Hạn chế | Cải thiện trong tương lai |
|---------|-------------------------|
| Chỉ dùng điểm chuẩn lịch sử | Kết hợp thêm tỷ lệ chọi, feedback thí sinh |
| Không tính phương thức xét tuyển khác | Thêm xét học bạ, ĐGNL, ĐGTD |
| CLI interface | Xây dựng Web Application (Flask/Django) |
| Không cá nhân hóa sâu | Thêm sở thích, năng lực, mục tiêu nghề nghiệp |
| Dữ liệu cắt ngang theo năm | Real-time updates khi Bộ GD&ĐT công bố |

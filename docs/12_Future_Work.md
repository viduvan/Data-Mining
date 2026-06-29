# 12_Future_Work.md

# Hướng Phát triển Tương lai — Future Work

---

## 1. Tổng quan

Dự án hiện tại đã xây dựng nền tảng hoàn chỉnh từ thu thập dữ liệu đến phân tích và gợi ý. Dưới đây là các hướng mở rộng nhằm nâng cao giá trị và phạm vi ứng dụng của hệ thống.

---

## 2. Mở rộng Ngắn hạn (3–6 tháng)

### 2.1 Web Application

**Mục tiêu:** Xây dựng giao diện web thân thiện cho thí sinh.

| Hạng mục | Chi tiết |
|----------|---------|
| Framework | Flask hoặc Django (Python) |
| Frontend | HTML/CSS/JS hoặc React |
| Tính năng | Form nhập điểm → Hiển thị gợi ý trường/ngành |
| API | RESTful API cho mobile apps |

**Wireframe:**
```
┌─────────────────────────────────────────┐
│ 🎓 GỢI Ý TRƯỜNG ĐẠI HỌC               │
├─────────────────────────────────────────┤
│ Điểm Toán:  [  8.5  ]                  │
│ Điểm Lý:   [  9.0  ]                  │
│ Điểm Hóa:  [  8.0  ]                  │
│ Tổ hợp:    [ A00 ▼ ]                  │
│ Khu vực:   [ KV2  ▼ ]                  │
│                                         │
│ [       🔍 TÌM TRƯỜNG PHÙ HỢP       ]  │
├─────────────────────────────────────────┤
│ 🟢 An toàn (5 kết quả)                  │
│  - ĐH FPT — CNTT — 22.0 — +17%        │
│  - ĐH Điện lực — KT Điện — 21.5 — +19%│
│                                         │
│ 🟡 Tương đối (3 kết quả)                │
│  - HUST — KT Điện — 24.5 — +5%         │
└─────────────────────────────────────────┘
```

### 2.2 Mở rộng Nguồn Dữ liệu

| Nguồn mới | Dữ liệu | Ưu tiên |
|----------|---------|--------|
| Điểm thi THPT | Phổ điểm từng môn toàn quốc | Cao |
| Tỷ lệ chọi | Số đăng ký / chỉ tiêu | Cao |
| Feedback thí sinh | Đánh giá sau nhập học | Trung bình |
| Bảng xếp hạng QS/THE | Ranking quốc tế | Thấp |

### 2.3 Cải thiện Mô hình

| Cải thiện | Chi tiết |
|----------|---------|
| Ensemble Forecasting | Kết hợp LinearRegression + ARIMA + XGBoost |
| Feature Selection | LASSO / Mutual Information cho feature quan trọng |
| Cross-validation mạnh hơn | Time-series CV với expanding window |
| Hyperparameter tuning | GridSearchCV cho K-Means, ARIMA(p,d,q) |

---

## 3. Mở rộng Trung hạn (6–12 tháng)

### 3.1 Machine Learning nâng cao

| Mô hình | Ứng dụng |
|---------|---------|
| **Random Forest / XGBoost** | Dự báo điểm chuẩn với nhiều features |
| **LSTM (Deep Learning)** | Time series forecasting dài hạn |
| **Collaborative Filtering** | Gợi ý dựa trên thí sinh tương tự |
| **Content-Based Filtering** | Gợi ý dựa trên profile ngành/trường |

### 3.2 Real-time Data Pipeline

```
Web Sources → Scrapy/Airflow → Kafka → PostgreSQL → Dashboard
     ↑                                        ↓
     └──── Scheduled crawl (daily/weekly) ← Alerts
```

| Thành phần | Công cụ |
|-----------|--------|
| Scheduler | Apache Airflow |
| Message Queue | Apache Kafka |
| Stream Processing | Apache Spark Streaming |
| Monitoring | Grafana + Prometheus |

### 3.3 NLP — Phân tích Đánh giá

- Crawl reviews từ forums (Reddit, Facebook groups)
- Sentiment Analysis cho từng trường
- Topic Modeling (LDA) cho concerns phổ biến
- Word Cloud visualization

### 3.4 Mobile Application

| Platform | Công nghệ |
|---------|----------|
| iOS / Android | React Native hoặc Flutter |
| Backend | FastAPI (Python) |
| Push Notifications | Thông báo khi có điểm chuẩn mới |

---

## 4. Mở rộng Dài hạn (1–2 năm)

### 4.1 Hệ thống Tư vấn Thông minh (AI Advisor)

Sử dụng LLM (Large Language Model) để:
- Chat tư vấn tuyển sinh bằng tiếng Việt
- Trả lời câu hỏi phức tạp: "Tôi thích IT nhưng điểm chỉ 24, nên chọn trường nào?"
- Phân tích profile cá nhân (sở thích, năng lực, mục tiêu nghề nghiệp)

### 4.2 Multi-country Expansion

- Mở rộng sang các nước ASEAN (Thái Lan, Indonesia, Philippines)
- So sánh hệ thống tuyển sinh giữa các quốc gia
- Chuẩn hóa data model cho đa quốc gia

### 4.3 API Service cho Third-party

```
POST /api/v1/recommend
{
    "scores": [8.5, 9.0, 8.0],
    "subject_group": "A00",
    "region": "KV2",
    "top_n": 20
}

→ Response:
{
    "total_score": 25.75,
    "results": [
        {
            "school": "Đại học FPT",
            "major": "CNTT",
            "admission_score": 22.0,
            "safety_score": 17.0,
            "safety_label": "An toàn"
        },
        ...
    ]
}
```

---

## 5. Research Directions (Nghiên cứu)

| Hướng | Câu hỏi nghiên cứu |
|-------|-------------------|
| Công bằng giáo dục | Có bất bình đẳng khu vực trong tiếp cận giáo dục ĐH? |
| Impact COVID | COVID ảnh hưởng dài hạn đến xu hướng tuyển sinh? |
| Policy Analysis | Chính sách mới (bỏ điểm sàn, tự chủ tuyển sinh) ảnh hưởng thế nào? |
| Career Outcome | Mối liên hệ giữa ngành học và kết quả nghề nghiệp? |

---

## 6. Ưu tiên Triển khai

| # | Hạng mục | Ưu tiên | Effort | Impact |
|---|---------|--------|--------|--------|
| 1 | Web Application | 🔴 Cao | Medium | Rất cao |
| 2 | Thêm nguồn dữ liệu (tỷ lệ chọi) | 🔴 Cao | Low | Cao |
| 3 | Ensemble Forecasting | 🟡 Trung | Medium | Trung bình |
| 4 | Mobile Application | 🟡 Trung | High | Cao |
| 5 | NLP Sentiment Analysis | 🟢 Thấp | High | Trung bình |
| 6 | Real-time Pipeline | 🟢 Thấp | Very High | Cao (dài hạn) |
| 7 | AI Advisor (LLM) | 🟢 Thấp | Very High | Rất cao (dài hạn) |

# 06_Exploratory_Data_Analysis.md

# Phân tích Khám phá Dữ liệu — Exploratory Data Analysis (EDA)

---

## 1. Tổng quan

EDA được thực hiện trên dữ liệu tuyển sinh đại học Việt Nam giai đoạn 2020–2025 nhằm:

- Hiểu cấu trúc và phân bố dữ liệu
- Phát hiện patterns, trends, outliers
- Đặt nền tảng cho Data Mining (Phase 5)
- Trả lời các câu hỏi nghiên cứu mô tả (Q1–Q5)

---

## 2. Notebooks EDA

| # | Notebook | Nội dung chính |
|---|----------|---------------|
| 1 | `01_data_overview.ipynb` | Tổng quan dữ liệu, thống kê mô tả |
| 2 | `02_trend_analysis.ipynb` | Xu hướng điểm chuẩn theo thời gian |
| 3 | `03_school_analysis.ipynb` | Phân tích theo trường đại học |
| 4 | `04_major_analysis.ipynb` | Phân tích theo ngành / nhóm ngành |
| 5 | `05_subject_group_analysis.ipynb` | Phân tích theo tổ hợp xét tuyển |

---

## 3. Data Overview

### 3.1 Thống kê mô tả

| Chỉ số | Giá trị dự kiến |
|--------|----------------|
| Tổng records | ~50,000 – 100,000 |
| Số trường | ~250 – 300 |
| Số ngành (duy nhất) | ~500 – 800 |
| Số tổ hợp xét tuyển | ~20 – 30 |
| Số năm | 6 (2020–2025) |
| Điểm chuẩn trung bình | 20.0 – 24.0 |
| Điểm chuẩn min/max | ~13.0 / ~30.0 |

### 3.2 Phân bố điểm chuẩn

- **Histogram:** Phân bố chuông lệch phải (skew right)
- **Boxplot:** Phát hiện outliers ở hai đầu
- **Q-Q Plot:** Kiểm tra tính chuẩn

### 3.3 Missing Value Analysis

| Cột | % Missing | Xử lý |
|-----|-----------|-------|
| school_name | 0% | Bắt buộc |
| admission_score | 0% | Bắt buộc |
| quota | 10-20% | Nullable |
| major_code | 5-15% | Nullable |

---

## 4. Trend Analysis (Q1)

> **Q1:** Điểm chuẩn tuyển sinh thay đổi như thế nào qua các năm 2020–2025?

### 4.1 Xu hướng tổng thể

- **Line chart:** Điểm chuẩn trung bình tổng thể theo năm
- Giai đoạn COVID (2020-2022) vs Hậu COVID (2023-2025)
- YoY change bars

### 4.2 Xu hướng theo nhóm ngành

- **Multi-line chart:** Mỗi line = 1 nhóm ngành
- Nhóm ngành tăng mạnh nhất: CNTT, Kinh tế
- Nhóm ngành ổn định: Y Dược, Sư phạm

### 4.3 Heatmap điểm chuẩn

- **Heatmap:** Trường × Năm → Color = điểm chuẩn TB
- Phát hiện trường nào tăng/giảm rõ rệt

---

## 5. School Analysis (Q3, Q4)

> **Q3:** Trường nào có điểm chuẩn ổn định / biến động nhiều nhất?  
> **Q4:** Phân bố điểm chuẩn theo khu vực có khác nhau không?

### 5.1 Top trường

- **Bar chart:** Top 10 trường điểm TB cao nhất
- **Bar chart:** Top 10 trường có biến động (std) lớn nhất

### 5.2 Phân bố theo khu vực

- **Boxplot:** Điểm chuẩn theo khu vực (Bắc/Trung/Nam)
- **T-test / ANOVA:** Kiểm định sự khác biệt có ý nghĩa thống kê

### 5.3 Công lập vs Tư thục

- **Violin plot:** So sánh phân bố điểm
- Tư thục thường có điểm chuẩn thấp hơn

### 5.4 Scatter plot

- **Scatter:** Chỉ tiêu (x) vs Điểm chuẩn TB (y)
- Phát hiện: trường có chỉ tiêu ít + điểm cao → cạnh tranh khốc liệt

---

## 6. Major Analysis (Q2)

> **Q2:** Nhóm ngành nào có điểm chuẩn cao nhất / thấp nhất?

### 6.1 Ranking nhóm ngành

| Nhóm ngành | ĐTB dự kiến | Mức cạnh tranh |
|-----------|------------|---------------|
| Y - Dược | 26–28 | Rất cao |
| Công an - Quân sự | 25–27 | Rất cao |
| Kinh tế - Quản trị | 23–26 | Cao |
| Kỹ thuật - Công nghệ | 22–26 | Cao |
| Sư phạm - Giáo dục | 18–23 | Trung bình |
| Nông - Lâm - Ngư | 15–20 | Thấp |

### 6.2 Treemap

- Diện tích = số trường tuyển, màu = điểm chuẩn TB

### 6.3 Xu hướng nhóm ngành qua các năm

- CNTT: Tăng mạnh 2020–2023, ổn định 2024–2025
- Y Dược: Luôn ở đỉnh, ít biến động

---

## 7. Subject Group Analysis (Q5)

> **Q5:** Tổ hợp xét tuyển nào được sử dụng phổ biến nhất?

### 7.1 Top tổ hợp phổ biến

| Hạng | Tổ hợp | Môn | Số ngành sử dụng |
|------|--------|-----|-----------------|
| 1 | A00 | Toán, Lý, Hóa | ~300+ |
| 2 | D01 | Toán, Văn, Anh | ~250+ |
| 3 | A01 | Toán, Lý, Anh | ~200+ |
| 4 | B00 | Toán, Hóa, Sinh | ~150+ |
| 5 | C00 | Văn, Sử, Địa | ~100+ |

### 7.2 Xu hướng tổ hợp

- D01 (có tiếng Anh): Xu hướng tăng nhanh
- A00 (truyền thống): Vẫn phổ biến nhất nhưng tỷ lệ giảm dần

---

## 8. Correlation Analysis (Q7)

> **Q7:** Có mối liên hệ giữa chỉ tiêu tuyển sinh và điểm chuẩn không?

- **Correlation matrix:** Giữa admission_score, quota, delta_score
- **Kỳ vọng:** Tương quan âm yếu (trường chỉ tiêu nhiều → điểm thấp hơn)

---

## 9. Phát hiện chính (Key Insights)

1. **Điểm chuẩn tăng** nhẹ qua các năm (0.3–0.5 điểm/năm)
2. **Phân cực rõ rệt** giữa nhóm trường top (≥25) và nhóm trung bình (<20)
3. **CNTT** là ngành có tốc độ tăng điểm nhanh nhất giai đoạn 2020–2024
4. **Khu vực Bắc** có điểm chuẩn TB cao hơn Trung và Nam
5. **Tổ hợp D01** đang được sử dụng ngày càng phổ biến (xu hướng quốc tế hóa)

---

## 10. Ghi chú kỹ thuật

### Thư viện sử dụng

| Thư viện | Mục đích |
|---------|---------|
| pandas | Xử lý dữ liệu |
| matplotlib | Biểu đồ cơ bản |
| seaborn | Biểu đồ thống kê |
| plotly | Biểu đồ tương tác |
| scipy.stats | Kiểm định thống kê |

### Chạy notebooks

```bash
conda run -n testing jupyter notebook notebooks/ --no-browser --port=8888
```

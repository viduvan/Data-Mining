# 08_PowerBI_Dashboard.md

# Dashboard Power BI — Trực quan hóa Dữ liệu Tuyển sinh

---

## 1. Tổng quan

Dashboard Power BI gồm **4 trang** chính, cung cấp cái nhìn đa chiều về dữ liệu tuyển sinh đại học Việt Nam 2020–2025.

| Trang | Tên | Mục đích |
|-------|-----|---------|
| 1 | Executive Dashboard | KPIs tổng quan, xu hướng tổng thể |
| 2 | School Dashboard | Phân tích chi tiết theo trường |
| 3 | Major Dashboard | Phân tích chi tiết theo ngành |
| 4 | Forecast Dashboard | Dự báo điểm chuẩn tương lai |

**Bảng màu chủ đạo:**
- Xanh dương đậm: `#1E3A5F` (Header, tiêu đề)
- Cam: `#F5821E` (Highlight, KPI)
- Xám nhạt: `#F5F5F5` (Nền)
- Đỏ/Xanh lá: `#D32F2F` / `#388E3C` (Giảm/Tăng)

---

## 2. Data Model

### 2.1 Nguồn dữ liệu

**Option A — Import CSV:** `data/warehouse/admission_main.csv`  
**Option B — PostgreSQL:** `localhost:5432 / vietnam_admission_dw`

### 2.2 Data Model Relationships

```
fact_admission  ──►  dim_school      (school_key, Many-to-One)
fact_admission  ──►  dim_major       (major_key, Many-to-One)
fact_admission  ──►  dim_year        (year_key, Many-to-One)
fact_admission  ──►  dim_subject_grp (subject_group_key, Many-to-One)
dim_school      ──►  dim_region      (region_code, Many-to-One)
```

**Cross-filter direction:** Single (từ Dimension → Fact)

---

## 3. Trang 1: Executive Dashboard

### 3.1 Layout

```
┌─────────────────────────────────────────────────────────────┐
│ 🏫 PHÂN TÍCH TUYỂN SINH ĐH VN   [Slicer: Năm 2020-2025]   │
├───────┬───────┬───────┬───────┬───────┬─────────────────────┤
│ KPI   │ KPI   │ KPI   │ KPI   │ KPI   │ KPI               │
│ Tổng  │ Số    │ ĐTB   │ YoY Δ │ Top ↑ │ Ngành hot         │
│ Record│ Trường│ Điểm  │ Điểm  │ Trường│                    │
├───────┴───────┴───────┴───────┴───────┴─────────────────────┤
│ LINE CHART: Xu hướng điểm chuẩn trung bình theo năm         │
├──────────────────────┬──────────────────────────────────────┤
│ BAR: Top 10 Trường   │ MAP: Phân bố theo khu vực            │
├──────────────────────┼──────────────────────────────────────┤
│ DONUT: Mức cạnh tranh│ BAR: Top 5 nhóm ngành               │
└──────────────────────┴──────────────────────────────────────┘
```

### 3.2 DAX Measures

```dax
Total Records = COUNT(fact_admission[admission_key])
Total Schools = DISTINCTCOUNT(dim_school[school_name])
Avg Score = AVERAGE(fact_admission[admission_score])

YoY Score Change =
    VAR CurrentYear = SELECTEDVALUE(dim_year[year])
    VAR PrevAvg = CALCULATE(AVERAGE(fact_admission[admission_score]),
                            dim_year[year] = CurrentYear - 1)
    RETURN [Avg Score] - PrevAvg
```

---

## 4. Trang 2: School Dashboard

### 4.1 Layout

```
┌─────────────────────────────────────────────────────────────┐
│ PHÂN TÍCH THEO TRƯỜNG   [Slicer: Trường] [Slicer: Năm]     │
├───────┬───────┬───────┬───────┬─────────────────────────────┤
│ ĐTB   │ Max   │ Min   │ Số    │ Tổng chỉ tiêu             │
│ điểm  │ điểm  │ điểm  │ ngành │                            │
├───────┴───────┴───────┴───────┴─────────────────────────────┤
│ LINE: Xu hướng điểm chuẩn của trường 2020-2025 (+ Trend)    │
├─────────────────────────┬───────────────────────────────────┤
│ TABLE: Ngành của trường │ SCATTER: Chỉ tiêu vs Điểm chuẩn  │
├─────────────────────────┴───────────────────────────────────┤
│ BAR: So sánh với trường cùng cluster                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Trang 3: Major Dashboard

### 5.1 Layout

```
┌─────────────────────────────────────────────────────────────┐
│ PHÂN TÍCH THEO NGÀNH   [Slicer: Nhóm ngành] [Slicer: TH]   │
├───────┬───────┬───────┬─────────────────────────────────────┤
│ Số    │ ĐTB   │ Max   │ Số trường tuyển ngành này          │
│ ngành │ nhóm  │ nhóm  │                                    │
├───────┴───────┴───────┴─────────────────────────────────────┤
│ HEATMAP: Điểm chuẩn theo ngành × năm (color gradient)       │
├─────────────────────────┬───────────────────────────────────┤
│ TREEMAP: Phân bố ngành  │ LINE: Xu hướng nhóm ngành         │
├─────────────────────────┴───────────────────────────────────┤
│ BAR: Top 10 ngành điểm cao nhất + YoY change                │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Trang 4: Forecast Dashboard

### 6.1 Layout

```
┌─────────────────────────────────────────────────────────────┐
│ DỰ BÁO ĐIỂM CHUẨN   [Slicer: Trường] [Slicer: Ngành]      │
├──────────┬──────────┬───────────────────────────────────────┤
│ Điểm dự  │ Trend    │ Model Accuracy (MAE / RMSE)           │
│ báo 2026 │ Tăng/Giảm│                                       │
├──────────┴──────────┴───────────────────────────────────────┤
│ LINE: Actual (2020-2025) + Forecast (2026) + CI              │
├─────────────────────────┬───────────────────────────────────┤
│ TABLE: Top 20 ngành dự  │ WATERFALL: Ngành tăng/giảm mạnh   │
│ báo tăng mạnh nhất      │ nhất                               │
└─────────────────────────┴───────────────────────────────────┘
```

---

## 7. Conditional Formatting

| Visual | Điều kiện | Màu |
|--------|----------|-----|
| Mức cạnh tranh | Rất cao (≥25) | 🔴 `#D32F2F` |
| | Cao (22-25) | 🟠 `#F57C00` |
| | Trung bình (18-22) | 🟢 `#388E3C` |
| | Thấp (<18) | 🔵 `#1976D2` |
| YoY Change | Tăng (>0) | 🟢 `#388E3C` |
| | Giảm (<0) | 🔴 `#D32F2F` |
| | Ổn định (=0) | ⚫ `#757575` |

---

## 8. Navigation

Tạo bookmarks + buttons cho navigation giữa 4 trang:
- 🏠 Tổng quan → Trang 1
- 🏫 Theo trường → Trang 2
- 📚 Theo ngành → Trang 3
- 📈 Dự báo → Trang 4

---

## 9. Hướng dẫn tạo Dashboard

### Bước 1: Import Data

1. Power BI Desktop → `Get Data` → `Text/CSV` (hoặc PostgreSQL)
2. Import `data/warehouse/admission_main.csv`
3. Kiểm tra data types trong Power Query Editor

### Bước 2: Tạo Relationships

Power BI tự detect nếu import từ PostgreSQL. Nếu import CSV thì tạo thủ công theo Data Model ở mục 2.2.

### Bước 3: Tạo Measures

Copy DAX từ `powerbi/dax_measures.md` vào Power BI (New Measure).

### Bước 4: Tạo Visuals

Tham khảo layout wireframe ở mỗi trang.

### Bước 5: Format & Publish

- Apply theme (Dark/Light)
- Publish lên Power BI Service (optional)

---

## 10. Tham khảo

- Layout chi tiết: `powerbi/dashboard_wireframe.md`
- DAX measures đầy đủ: `powerbi/dax_measures.md`

# dashboard_wireframe.md

# Thiết kế Dashboard Power BI — Vietnam University Admission

---

## Tổng quan

Dashboard gồm **4 trang** chính, liên kết với nhau qua Power BI navigation:

| Trang | Tên | Mục đích |
|-------|-----|---------|
| 1 | Executive Dashboard | Tổng quan KPIs, xu hướng tổng thể |
| 2 | School Dashboard | Phân tích chi tiết theo trường |
| 3 | Major Dashboard | Phân tích chi tiết theo ngành |
| 4 | Forecast Dashboard | Dự báo điểm chuẩn tương lai |

**Màu sắc chủ đạo:** Xanh dương (#1E3A5F) + Cam (#F5821E) + Trắng/Xám nhạt

---

## Trang 1: Executive Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🏫 VIETNAM UNIVERSITY ADMISSION ANALYSIS  [Year Slicer: 2020-2025]  │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────────┤
│ KPI 1    │ KPI 2    │ KPI 3    │ KPI 4    │ KPI 5    │ KPI 6        │
│ Tổng     │ Tổng     │ ĐTB      │ YoY Δ    │ Trường   │ Ngành        │
│ Records  │ Trường   │ Điểm     │ Điểm     │ Top ↑    │ Hot nhất     │
│ 85,000   │ 280      │ 23.5     │ +0.3     │ Bách khoa│ CNTT         │
├──────────┴──────────┴──────────┴──────────┴──────────┴──────────────┤
│ LINE CHART: Xu hướng điểm chuẩn trung bình theo năm                │
│ (Multi-line: Tổng thể, Kỹ thuật, Kinh tế, Y Dược, Sư phạm...)     │
├─────────────────────────────┬───────────────────────────────────────┤
│ BAR CHART: Top 10 Trường   │ MAP: Phân bố điểm chuẩn theo khu vực │
│ (ĐTB điểm chuẩn năm mới   │ (Bubble map: Bắc/Trung/Nam)          │
│ nhất, sắp xếp giảm dần)   │                                       │
├─────────────────────────────┼───────────────────────────────────────┤
│ DONUT: Phân bố mức cạnh   │ BAR CHART: Top 5 nhóm ngành          │
│ tranh (Rất cao/Cao/TB/Thấp)│ theo điểm chuẩn trung bình           │
└─────────────────────────────┴───────────────────────────────────────┘
```

### KPIs cần tạo (DAX):
- `Total Records` = COUNT(fact_admission[admission_key])
- `Total Schools` = DISTINCTCOUNT(dim_school[school_name])
- `Avg Score` = AVERAGE(fact_admission[admission_score])
- `YoY Score Change` = [Avg Score] - CALCULATE([Avg Score], PREVIOUSYEAR(...))
- Top school, Top major

---

## Trang 2: School Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│ PHÂN TÍCH THEO TRƯỜNG   [Slicer: Trường] [Slicer: Năm] [Slicer: Loại]│
├──────────┬──────────┬──────────┬──────────────────────────────────  │
│ KPI: ĐTB │ KPI: Max │ KPI: Min │ KPI: Số ngành  │ KPI: Tổng chỉ tiêu│
│ điểm     │ điểm     │ điểm     │                │                   │
├──────────┴──────────┴──────────┴──────────────────────────────────  │
│ LINE CHART: Xu hướng điểm chuẩn của trường qua 2020-2025           │
│ (Actual + Trend line + Forecast điểm năm tới)                      │
├────────────────────────────┬────────────────────────────────────────┤
│ TABLE: Ngành của trường    │ SCATTER: Chỉ tiêu vs Điểm chuẩn      │
│ (Tên ngành, Tổ hợp, Điểm, │ (mỗi điểm = 1 ngành, hover tooltip)  │
│ Safety vs năm trước)       │                                        │
├────────────────────────────┴────────────────────────────────────────┤
│ BAR CHART: So sánh với trường tương tự (cùng cluster)              │
│ (Horizontal bar chart so sánh ĐTB điểm chuẩn)                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Trang 3: Major Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│ PHÂN TÍCH THEO NGÀNH   [Slicer: Nhóm ngành] [Slicer: Tổ hợp]      │
├──────────────┬──────────────┬──────────────┬────────────────────────┤
│ KPI: Số ngành│ KPI: ĐTB     │ KPI: Điểm Max│ KPI: Số trường tuyển │
│ trong nhóm  │ nhóm ngành   │ trong nhóm  │                        │
├──────────────┴──────────────┴──────────────┴────────────────────────┤
│ HEATMAP: Điểm chuẩn theo ngành × năm                               │
│ (Rows = nhóm ngành, Columns = năm, Color = điểm chuẩn)            │
├───────────────────────────┬─────────────────────────────────────────┤
│ TREEMAP: Phân bố ngành   │ LINE CHART: Xu hướng nhóm ngành         │
│ theo nhóm và số trường   │ (Multi-line, mỗi line = 1 nhóm ngành)  │
├───────────────────────────┴─────────────────────────────────────────┤
│ BAR CHART: Top 10 ngành điểm cao nhất năm mới nhất                 │
│ + YoY change (dual-axis hoặc color-coded)                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Trang 4: Forecast Dashboard

```
┌─────────────────────────────────────────────────────────────────────┐
│ DỰ BÁO ĐIỂM CHUẨN   [Slicer: Trường] [Slicer: Ngành]              │
├──────────┬──────────┬──────────────────────────────────────────────  │
│ Điểm dự │ Trend    │ Biên độ sai số (CI 95%)                       │
│ báo 2026 │ Tăng/Giảm│                                               │
├──────────┴──────────┴──────────────────────────────────────────────  │
│ LINE CHART: Actual (2020-2025) + Forecast (2026)                    │
│ (Với ribbon/area cho confidence interval)                           │
├────────────────────────────┬────────────────────────────────────────┤
│ TABLE: Top 20 ngành dự   │ BAR CHART: Ngành dự báo tăng/giảm     │
│ báo điểm tăng mạnh nhất  │ nhiều nhất (waterfall chart)           │
├────────────────────────────┴────────────────────────────────────────┤
│ CARD: Model accuracy metrics (MAE, RMSE, MAPE)                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Kết nối dữ liệu

### Option A: Kết nối trực tiếp PostgreSQL
1. Power BI Desktop → Get Data → PostgreSQL Database
2. Server: `localhost:5432`
3. Database: `vietnam_admission_dw`
4. Chọn tables: `fact_admission` + tất cả `dim_*`

### Option B: Import CSV
1. Power BI Desktop → Get Data → Text/CSV
2. Import từ `data/warehouse/admission_main.csv` và các file khác

---

## Navigation Setup

Tạo bookmarks + buttons cho navigation giữa 4 trang:
- Button "🏠 Tổng quan" → Trang 1
- Button "🏫 Theo trường" → Trang 2
- Button "📚 Theo ngành" → Trang 3
- Button "📈 Dự báo" → Trang 4

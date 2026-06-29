# dax_measures.md

# DAX Measures — Vietnam University Admission Dashboard

---

## Trang 1: Executive Dashboard

```dax
-- Tổng số records
Total Records =
    COUNT(fact_admission[admission_key])

-- Tổng số trường
Total Schools =
    DISTINCTCOUNT(dim_school[school_name])

-- Tổng số ngành
Total Majors =
    DISTINCTCOUNT(dim_major[major_name])

-- Điểm chuẩn trung bình
Avg Score =
    AVERAGE(fact_admission[admission_score])

-- Điểm chuẩn trung bình năm được chọn
Avg Score Selected Year =
    CALCULATE(
        AVERAGE(fact_admission[admission_score]),
        ALLEXCEPT(fact_admission, dim_year[year])
    )

-- Thay đổi điểm chuẩn so với năm trước (YoY)
YoY Score Change =
    VAR CurrentYear = SELECTEDVALUE(dim_year[year])
    VAR PrevYear = CurrentYear - 1
    VAR CurrentAvg = [Avg Score]
    VAR PrevAvg =
        CALCULATE(
            AVERAGE(fact_admission[admission_score]),
            dim_year[year] = PrevYear
        )
    RETURN
        IF(
            NOT ISBLANK(PrevAvg),
            CurrentAvg - PrevAvg,
            BLANK()
        )

-- % thay đổi so với năm trước
YoY Score Change % =
    DIVIDE([YoY Score Change], [Avg Score] - [YoY Score Change], 0) * 100

-- Điểm chuẩn cao nhất
Max Score = MAX(fact_admission[admission_score])

-- Điểm chuẩn thấp nhất
Min Score = MIN(fact_admission[admission_score])
```

---

## Trang 2: School Dashboard

```dax
-- Điểm trung bình của trường được chọn
School Avg Score =
    CALCULATE(
        AVERAGE(fact_admission[admission_score]),
        ALLEXCEPT(fact_admission, dim_school[school_name])
    )

-- Số ngành của trường
School Num Majors =
    CALCULATE(
        DISTINCTCOUNT(dim_major[major_key]),
        ALLEXCEPT(fact_admission, dim_school[school_name])
    )

-- Tổng chỉ tiêu của trường
School Total Quota =
    CALCULATE(
        SUM(fact_admission[quota]),
        ALLEXCEPT(fact_admission, dim_school[school_name])
    )

-- Rank trường theo điểm chuẩn
School Score Rank =
    RANKX(
        ALL(dim_school[school_name]),
        [School Avg Score],
        ,
        DESC,
        SKIP
    )

-- YoY thay đổi cho từng ngành của trường
Major YoY Delta =
    AVERAGE(fact_admission[delta_score])
```

---

## Trang 3: Major Dashboard

```dax
-- Điểm chuẩn trung bình nhóm ngành
Major Group Avg Score =
    CALCULATE(
        AVERAGE(fact_admission[admission_score]),
        ALLEXCEPT(fact_admission, dim_major[major_group])
    )

-- Số trường tuyển sinh ngành này
Num Schools For Major =
    CALCULATE(
        DISTINCTCOUNT(dim_school[school_key]),
        ALLEXCEPT(fact_admission, dim_major[major_name])
    )

-- Rank ngành theo điểm chuẩn
Major Score Rank =
    RANKX(
        ALL(dim_major[major_name]),
        AVERAGE(fact_admission[admission_score]),
        ,
        DESC,
        SKIP
    )

-- Phân loại mức cạnh tranh (cho màu sắc)
Competition Color =
    SWITCH(
        SELECTEDVALUE(fact_admission[competition_level]),
        "Rất cao",   "#D32F2F",
        "Cao",       "#F57C00",
        "Trung bình","#388E3C",
        "Thấp",      "#1976D2",
        "#9E9E9E"
    )
```

---

## Trang 4: Forecast Dashboard

```dax
-- Điểm dự báo (từ bảng forecast nếu import)
Forecast Score =
    IF(
        HASONEVALUE(forecast_data[school_name]),
        SELECTEDVALUE(forecast_data[predicted_score]),
        BLANK()
    )

-- Chênh lệch dự báo vs thực tế năm cuối
Forecast Delta =
    [Forecast Score] - [Avg Score]

-- Label xu hướng
Forecast Trend Label =
    VAR delta = [Forecast Delta]
    RETURN
        IF(delta > 0.5, "📈 Tăng",
        IF(delta < -0.5, "📉 Giảm",
        "➡️ Ổn định"))
```

---

## Conditional Formatting Rules

### Màu sắc theo mức cạnh tranh:
- **Rất cao** (≥25): 🔴 `#D32F2F`
- **Cao** (22-25): 🟠 `#F57C00`
- **Trung bình** (18-22): 🟢 `#388E3C`
- **Thấp** (<18): 🔵 `#1976D2`

### Màu sắc YoY Change:
- Tăng (> 0): `#388E3C` (xanh lá)
- Giảm (< 0): `#D32F2F` (đỏ)
- Ổn định (= 0): `#757575` (xám)

---

## Data Model Relationships (Power BI)

```
fact_admission  →  dim_school      (school_key)
fact_admission  →  dim_major       (major_key)
fact_admission  →  dim_year        (year_key)
fact_admission  →  dim_subject_grp (subject_group_key)
dim_school      →  dim_region      (region_code)
```

**Cardinality:** Many-to-One (fact → dimension)
**Cross-filter direction:** Single (từ dim → fact)

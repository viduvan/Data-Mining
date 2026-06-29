-- ============================================================
-- sql/queries/trend_analysis.sql
-- Truy vấn phân tích xu hướng điểm chuẩn theo năm
-- ============================================================

-- Q1: Điểm chuẩn trung bình theo năm
SELECT
    y.year,
    y.period_label,
    COUNT(DISTINCT f.school_key)    AS num_schools,
    COUNT(DISTINCT f.major_key)     AS num_majors,
    COUNT(*)                        AS total_records,
    ROUND(AVG(f.admission_score), 2) AS avg_score,
    MIN(f.admission_score)           AS min_score,
    MAX(f.admission_score)           AS max_score,
    ROUND(STDDEV(f.admission_score), 2) AS std_score
FROM fact_admission f
JOIN dim_year y ON f.year_key = y.year_key
GROUP BY y.year, y.period_label
ORDER BY y.year;

-- Q2: Top 10 ngành có điểm chuẩn tăng mạnh nhất (2020-2025)
SELECT
    m.major_name,
    m.major_group,
    MIN(CASE WHEN y.year = 2020 THEN f.admission_score END) AS score_2020,
    MAX(CASE WHEN y.year = 2025 THEN f.admission_score END) AS score_2025,
    (MAX(CASE WHEN y.year = 2025 THEN f.admission_score END) -
     MIN(CASE WHEN y.year = 2020 THEN f.admission_score END)) AS total_change
FROM fact_admission f
JOIN dim_major m ON f.major_key = m.major_key
JOIN dim_year y ON f.year_key = y.year_key
WHERE y.year IN (2020, 2025)
GROUP BY m.major_name, m.major_group
HAVING COUNT(DISTINCT y.year) = 2
ORDER BY total_change DESC
LIMIT 10;

-- Q3: Top 10 ngành có điểm chuẩn giảm mạnh nhất
SELECT
    m.major_name,
    m.major_group,
    MIN(CASE WHEN y.year = 2020 THEN f.admission_score END) AS score_2020,
    MAX(CASE WHEN y.year = 2025 THEN f.admission_score END) AS score_2025,
    (MAX(CASE WHEN y.year = 2025 THEN f.admission_score END) -
     MIN(CASE WHEN y.year = 2020 THEN f.admission_score END)) AS total_change
FROM fact_admission f
JOIN dim_major m ON f.major_key = m.major_key
JOIN dim_year y ON f.year_key = y.year_key
WHERE y.year IN (2020, 2025)
GROUP BY m.major_name, m.major_group
HAVING COUNT(DISTINCT y.year) = 2
ORDER BY total_change ASC
LIMIT 10;

-- Q4: Xu hướng điểm chuẩn theo nhóm ngành qua các năm
SELECT
    m.major_group,
    y.year,
    ROUND(AVG(f.admission_score), 2) AS avg_score,
    COUNT(*) AS num_records
FROM fact_admission f
JOIN dim_major m ON f.major_key = m.major_key
JOIN dim_year y ON f.year_key = y.year_key
WHERE m.major_group IS NOT NULL
GROUP BY m.major_group, y.year
ORDER BY m.major_group, y.year;

-- Q5: Phân bố mức độ cạnh tranh theo năm
SELECT
    y.year,
    f.competition_level,
    COUNT(*) AS count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY y.year), 1) AS pct
FROM fact_admission f
JOIN dim_year y ON f.year_key = y.year_key
WHERE f.competition_level IS NOT NULL
GROUP BY y.year, f.competition_level
ORDER BY y.year, f.competition_level;

-- Q6: Điểm chuẩn YoY change theo khu vực
SELECT
    r.area AS region,
    y.year,
    ROUND(AVG(f.admission_score), 2) AS avg_score,
    ROUND(AVG(f.delta_score), 2) AS avg_delta
FROM fact_admission f
JOIN dim_school s ON f.school_key = s.school_key
JOIN dim_region r ON s.region_code = r.region_code
JOIN dim_year y ON f.year_key = y.year_key
GROUP BY r.area, y.year
ORDER BY r.area, y.year;

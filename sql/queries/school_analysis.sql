-- ============================================================
-- sql/queries/school_analysis.sql
-- Truy vấn phân tích theo trường đại học
-- ============================================================

-- Q1: Top 20 trường có điểm chuẩn trung bình cao nhất (2023-2025)
SELECT
    s.school_name,
    s.school_type,
    s.province,
    ROUND(AVG(f.admission_score), 2) AS avg_score,
    MIN(f.admission_score)           AS min_score,
    MAX(f.admission_score)           AS max_score,
    ROUND(STDDEV(f.admission_score), 2) AS std_score,
    COUNT(DISTINCT f.major_key)      AS num_majors
FROM fact_admission f
JOIN dim_school s ON f.school_key = s.school_key
JOIN dim_year y ON f.year_key = y.year_key
WHERE y.year >= 2023
GROUP BY s.school_name, s.school_type, s.province
ORDER BY avg_score DESC
LIMIT 20;

-- Q2: Điểm chuẩn trường theo từng năm (cho line chart)
SELECT
    s.school_name,
    y.year,
    ROUND(AVG(f.admission_score), 2) AS avg_score,
    COUNT(*) AS num_records
FROM fact_admission f
JOIN dim_school s ON f.school_key = s.school_key
JOIN dim_year y ON f.year_key = y.year_key
GROUP BY s.school_name, y.year
ORDER BY s.school_name, y.year;

-- Q3: Trường có điểm chuẩn ổn định nhất (std_dev thấp qua các năm)
SELECT
    s.school_name,
    s.school_type,
    ROUND(AVG(f.admission_score), 2)    AS avg_score,
    ROUND(STDDEV(f.admission_score), 3) AS std_dev,
    COUNT(DISTINCT y.year)              AS years_present
FROM fact_admission f
JOIN dim_school s ON f.school_key = s.school_key
JOIN dim_year y ON f.year_key = y.year_key
GROUP BY s.school_name, s.school_type
HAVING COUNT(DISTINCT y.year) >= 4  -- Có dữ liệu ít nhất 4 năm
ORDER BY std_dev ASC
LIMIT 15;

-- Q4: So sánh trường công lập vs tư thục
SELECT
    s.school_type,
    y.year,
    COUNT(DISTINCT s.school_key)        AS num_schools,
    ROUND(AVG(f.admission_score), 2)    AS avg_score,
    MIN(f.admission_score)              AS min_score,
    MAX(f.admission_score)              AS max_score
FROM fact_admission f
JOIN dim_school s ON f.school_key = s.school_key
JOIN dim_year y ON f.year_key = y.year_key
WHERE s.school_type IS NOT NULL
GROUP BY s.school_type, y.year
ORDER BY s.school_type, y.year;

-- Q5: Phân bố trường theo khu vực và mức điểm
SELECT
    r.area AS region,
    f.competition_level,
    COUNT(*) AS count,
    ROUND(AVG(f.admission_score), 2) AS avg_score
FROM fact_admission f
JOIN dim_school s ON f.school_key = s.school_key
JOIN dim_region r ON s.region_code = r.region_code
WHERE r.area IS NOT NULL
GROUP BY r.area, f.competition_level
ORDER BY r.area, f.competition_level;

-- Q6: Tương quan chỉ tiêu và điểm chuẩn
SELECT
    s.school_name,
    y.year,
    SUM(f.quota) AS total_quota,
    ROUND(AVG(f.admission_score), 2) AS avg_score
FROM fact_admission f
JOIN dim_school s ON f.school_key = s.school_key
JOIN dim_year y ON f.year_key = y.year_key
WHERE f.quota IS NOT NULL
GROUP BY s.school_name, y.year
ORDER BY y.year, total_quota DESC;

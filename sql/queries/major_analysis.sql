-- ============================================================
-- sql/queries/major_analysis.sql
-- Truy vấn phân tích theo ngành học
-- ============================================================

-- Q1: Top 20 ngành có điểm chuẩn cao nhất năm gần nhất
SELECT
    m.major_name,
    m.major_group,
    COUNT(DISTINCT f.school_key)        AS num_schools,
    ROUND(AVG(f.admission_score), 2)    AS avg_score,
    MAX(f.admission_score)              AS max_score,
    MIN(f.admission_score)              AS min_score
FROM fact_admission f
JOIN dim_major m ON f.major_key = m.major_key
JOIN dim_year y ON f.year_key = y.year_key
WHERE y.year = (SELECT MAX(year) FROM dim_year)
GROUP BY m.major_name, m.major_group
ORDER BY avg_score DESC
LIMIT 20;

-- Q2: Điểm chuẩn theo nhóm ngành (major_group) qua từng năm
SELECT
    m.major_group,
    y.year,
    COUNT(DISTINCT m.major_key)         AS num_majors,
    COUNT(DISTINCT f.school_key)        AS num_schools,
    ROUND(AVG(f.admission_score), 2)    AS avg_score,
    MAX(f.admission_score)              AS max_score,
    MIN(f.admission_score)              AS min_score
FROM fact_admission f
JOIN dim_major m ON f.major_key = m.major_key
JOIN dim_year y ON f.year_key = y.year_key
WHERE m.major_group IS NOT NULL AND m.major_group != 'Khác'
GROUP BY m.major_group, y.year
ORDER BY m.major_group, y.year;

-- Q3: Ngành có nhiều trường tuyển sinh nhất (phổ biến nhất)
SELECT
    m.major_name,
    m.major_group,
    COUNT(DISTINCT f.school_key) AS num_schools,
    ROUND(AVG(f.admission_score), 2) AS avg_score
FROM fact_admission f
JOIN dim_major m ON f.major_key = m.major_key
GROUP BY m.major_name, m.major_group
ORDER BY num_schools DESC
LIMIT 20;

-- Q4: Tổ hợp xét tuyển phổ biến theo ngành
SELECT
    m.major_group,
    sg.group_code AS subject_group,
    COUNT(*) AS frequency,
    ROUND(AVG(f.admission_score), 2) AS avg_score
FROM fact_admission f
JOIN dim_major m ON f.major_key = m.major_key
JOIN dim_subject_group sg ON f.subject_group_key = sg.subject_group_key
WHERE m.major_group IS NOT NULL
GROUP BY m.major_group, sg.group_code
ORDER BY m.major_group, frequency DESC;

-- Q5: Ngành có chỉ tiêu lớn nhất
SELECT
    m.major_name,
    m.major_group,
    y.year,
    SUM(f.quota) AS total_quota,
    COUNT(DISTINCT f.school_key) AS num_schools
FROM fact_admission f
JOIN dim_major m ON f.major_key = m.major_key
JOIN dim_year y ON f.year_key = y.year_key
WHERE f.quota IS NOT NULL
GROUP BY m.major_name, m.major_group, y.year
ORDER BY y.year, total_quota DESC
LIMIT 30;

-- Q6: Heatmap data: Điểm chuẩn ngành × năm (cho major group)
SELECT
    m.major_group,
    MAX(CASE WHEN y.year = 2020 THEN ROUND(AVG(f.admission_score), 2) END) AS "2020",
    MAX(CASE WHEN y.year = 2021 THEN ROUND(AVG(f.admission_score), 2) END) AS "2021",
    MAX(CASE WHEN y.year = 2022 THEN ROUND(AVG(f.admission_score), 2) END) AS "2022",
    MAX(CASE WHEN y.year = 2023 THEN ROUND(AVG(f.admission_score), 2) END) AS "2023",
    MAX(CASE WHEN y.year = 2024 THEN ROUND(AVG(f.admission_score), 2) END) AS "2024",
    MAX(CASE WHEN y.year = 2025 THEN ROUND(AVG(f.admission_score), 2) END) AS "2025"
FROM fact_admission f
JOIN dim_major m ON f.major_key = m.major_key
JOIN dim_year y ON f.year_key = y.year_key
WHERE m.major_group IS NOT NULL AND m.major_group != 'Khác'
GROUP BY m.major_group
ORDER BY m.major_group;

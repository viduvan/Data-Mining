-- ============================================================
-- sql/create_schema.sql
-- Tạo Star Schema Data Warehouse cho tuyển sinh đại học VN
-- 
-- Star Schema:
--   1 Fact Table: fact_admission
--   5 Dimension Tables: dim_school, dim_major, dim_year,
--                       dim_subject_group, dim_region
--
-- Chạy:
--   psql -U admission_user -d vietnam_admission_dw -f sql/create_schema.sql
-- ============================================================

\echo '=== Tạo Star Schema: Vietnam Admission Data Warehouse ==='

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

-- Chiều Khu vực (Miền Bắc / Trung / Nam)
CREATE TABLE IF NOT EXISTS dim_region (
    region_key      SERIAL PRIMARY KEY,
    region_code     VARCHAR(10) UNIQUE NOT NULL,   -- B, T, N, UK
    region_name     VARCHAR(100) NOT NULL,           -- Miền Bắc, Miền Trung, Miền Nam
    area            VARCHAR(50)                      -- Bắc, Trung, Nam
);
COMMENT ON TABLE dim_region IS 'Chiều khu vực địa lý';

-- Chiều Năm
CREATE TABLE IF NOT EXISTS dim_year (
    year_key        SERIAL PRIMARY KEY,
    year            INT UNIQUE NOT NULL,             -- 2020, 2021, ...
    period_label    VARCHAR(100)                     -- Giai đoạn COVID, Hậu COVID...
);
COMMENT ON TABLE dim_year IS 'Chiều năm tuyển sinh';

-- Chiều Trường Đại học
CREATE TABLE IF NOT EXISTS dim_school (
    school_key      SERIAL PRIMARY KEY,
    school_code     VARCHAR(20),                     -- Mã trường do Bộ GD&ĐT cấp
    school_name     VARCHAR(300) UNIQUE NOT NULL,    -- Tên trường đầy đủ
    school_type     VARCHAR(50)                      -- Công lập / Tư thục / Nước ngoài
                    CHECK (school_type IN ('Công lập', 'Tư thục', 'Nước ngoài', 'Khác')),
    province        VARCHAR(100),                    -- Tỉnh/thành phố
    region_code     VARCHAR(10)                      -- FK → dim_region (lưu code để join linh hoạt)
                    REFERENCES dim_region(region_code) ON DELETE SET NULL,
    website         VARCHAR(255),
    established_year INT
);
COMMENT ON TABLE dim_school IS 'Chiều trường đại học';
CREATE INDEX IF NOT EXISTS idx_school_name ON dim_school(school_name);
CREATE INDEX IF NOT EXISTS idx_school_type ON dim_school(school_type);
CREATE INDEX IF NOT EXISTS idx_school_region ON dim_school(region_code);

-- Chiều Ngành học
CREATE TABLE IF NOT EXISTS dim_major (
    major_key       SERIAL PRIMARY KEY,
    major_code      VARCHAR(20),                     -- Mã ngành (7 số)
    major_name      VARCHAR(300) UNIQUE NOT NULL,    -- Tên ngành
    major_group     VARCHAR(100),                    -- Nhóm ngành (Kỹ thuật, Kinh tế, Y Dược...)
    field_of_study  VARCHAR(200)                     -- Lĩnh vực học tập chi tiết hơn
);
COMMENT ON TABLE dim_major IS 'Chiều ngành học';
CREATE INDEX IF NOT EXISTS idx_major_group ON dim_major(major_group);

-- Chiều Tổ hợp xét tuyển
CREATE TABLE IF NOT EXISTS dim_subject_group (
    subject_group_key SERIAL PRIMARY KEY,
    group_code      VARCHAR(10) UNIQUE NOT NULL,     -- A00, D01, C00...
    group_name      VARCHAR(100) NOT NULL,
    subject_1       VARCHAR(100),                    -- Môn 1 (Toán, Ngữ văn...)
    subject_2       VARCHAR(100),                    -- Môn 2
    subject_3       VARCHAR(100)                     -- Môn 3
);
COMMENT ON TABLE dim_subject_group IS 'Chiều tổ hợp xét tuyển';

-- ============================================================
-- FACT TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_admission (
    admission_key       SERIAL PRIMARY KEY,
    -- Foreign Keys → Dimensions
    school_key          INT NOT NULL REFERENCES dim_school(school_key) ON DELETE CASCADE,
    major_key           INT REFERENCES dim_major(major_key) ON DELETE SET NULL,
    year_key            INT NOT NULL REFERENCES dim_year(year_key) ON DELETE CASCADE,
    subject_group_key   INT REFERENCES dim_subject_group(subject_group_key) ON DELETE SET NULL,

    -- Measures
    admission_score     NUMERIC(5, 2),              -- Điểm chuẩn (0.00 - 30.00)
    quota               INT,                         -- Chỉ tiêu tuyển sinh
    admission_method    VARCHAR(200),                -- Phương thức xét tuyển

    -- Derived Features (từ Feature Engineering)
    delta_score         NUMERIC(5, 2),               -- Chênh lệch điểm so với năm trước
    delta_score_pct     NUMERIC(7, 2),               -- Chênh lệch %
    competition_level   VARCHAR(20)                  -- Rất cao / Cao / Trung bình / Thấp
                        CHECK (competition_level IN ('Rất cao', 'Cao', 'Trung bình', 'Thấp')),
    score_trend         VARCHAR(20),                 -- Tăng / Giảm / Ổn định

    -- Metadata
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint: Không có 2 records trùng cùng trường+ngành+tổ hợp+năm
    CONSTRAINT uq_admission UNIQUE (school_key, major_key, subject_group_key, year_key)
);
COMMENT ON TABLE fact_admission IS 'Bảng sự kiện điểm chuẩn tuyển sinh';

-- Indexes cho Fact Table
CREATE INDEX IF NOT EXISTS idx_fact_school ON fact_admission(school_key);
CREATE INDEX IF NOT EXISTS idx_fact_major ON fact_admission(major_key);
CREATE INDEX IF NOT EXISTS idx_fact_year ON fact_admission(year_key);
CREATE INDEX IF NOT EXISTS idx_fact_score ON fact_admission(admission_score);
CREATE INDEX IF NOT EXISTS idx_fact_competition ON fact_admission(competition_level);
CREATE INDEX IF NOT EXISTS idx_fact_year_score ON fact_admission(year_key, admission_score);

-- ============================================================
-- SEED DATA cho Dimension Tables
-- ============================================================

-- Seed dim_region
INSERT INTO dim_region (region_code, region_name, area) VALUES
    ('B', 'Miền Bắc', 'Bắc'),
    ('T', 'Miền Trung', 'Trung'),
    ('N', 'Miền Nam', 'Nam'),
    ('UK', 'Không xác định', 'Không xác định')
ON CONFLICT (region_code) DO NOTHING;

-- Seed dim_year (2020-2025)
INSERT INTO dim_year (year, period_label) VALUES
    (2020, 'Giai đoạn COVID (2020-2022)'),
    (2021, 'Giai đoạn COVID (2020-2022)'),
    (2022, 'Giai đoạn COVID (2020-2022)'),
    (2023, 'Giai đoạn Hậu COVID (2023-2025)'),
    (2024, 'Giai đoạn Hậu COVID (2023-2025)'),
    (2025, 'Giai đoạn Hậu COVID (2023-2025)')
ON CONFLICT (year) DO NOTHING;

-- Seed dim_subject_group (tổ hợp phổ biến)
INSERT INTO dim_subject_group (group_code, group_name, subject_1, subject_2, subject_3) VALUES
    ('A00', 'Toán - Vật lý - Hóa học',  'Toán', 'Vật lý', 'Hóa học'),
    ('A01', 'Toán - Vật lý - Tiếng Anh', 'Toán', 'Vật lý', 'Tiếng Anh'),
    ('B00', 'Toán - Hóa học - Sinh học', 'Toán', 'Hóa học', 'Sinh học'),
    ('B08', 'Toán - Sinh học - Tiếng Anh', 'Toán', 'Sinh học', 'Tiếng Anh'),
    ('C00', 'Ngữ văn - Lịch sử - Địa lý', 'Ngữ văn', 'Lịch sử', 'Địa lý'),
    ('D01', 'Toán - Ngữ văn - Tiếng Anh', 'Toán', 'Ngữ văn', 'Tiếng Anh'),
    ('D07', 'Toán - Hóa học - Tiếng Anh', 'Toán', 'Hóa học', 'Tiếng Anh'),
    ('D08', 'Toán - Sinh học - Tiếng Anh', 'Toán', 'Sinh học', 'Tiếng Anh'),
    ('D14', 'Ngữ văn - Lịch sử - Tiếng Anh', 'Ngữ văn', 'Lịch sử', 'Tiếng Anh'),
    ('C01', 'Toán - Ngữ văn - Vật lý', 'Toán', 'Ngữ văn', 'Vật lý'),
    ('D90', 'Toán - KHTN - Tiếng Anh', 'Toán', 'KHTN', 'Tiếng Anh'),
    ('A16', 'Toán - KHTN - Tiếng Anh', 'Toán', 'KHTN', 'Tiếng Anh')
ON CONFLICT (group_code) DO NOTHING;

\echo '=== Schema tạo thành công! ==='
\echo 'Tiếp theo: chạy ETL Pipeline để load dữ liệu'

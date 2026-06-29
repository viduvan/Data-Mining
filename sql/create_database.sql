-- ============================================================
-- sql/create_database.sql
-- Tạo database PostgreSQL cho Data Warehouse
-- Chạy với user postgres:
--   sudo -u postgres psql -f sql/create_database.sql
-- ============================================================

-- Tạo user (nếu chưa có)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'admission_user') THEN
        CREATE USER admission_user WITH PASSWORD 'admission_pass_2024';
        RAISE NOTICE 'User admission_user đã được tạo';
    ELSE
        RAISE NOTICE 'User admission_user đã tồn tại';
    END IF;
END $$;

-- Tạo database
SELECT 'CREATE DATABASE vietnam_admission_dw'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'vietnam_admission_dw'
)\gexec

-- Cấp quyền
GRANT ALL PRIVILEGES ON DATABASE vietnam_admission_dw TO admission_user;

\echo 'Database vietnam_admission_dw đã sẵn sàng!'
\echo 'Tiếp theo: psql -U admission_user -d vietnam_admission_dw -f sql/create_schema.sql'

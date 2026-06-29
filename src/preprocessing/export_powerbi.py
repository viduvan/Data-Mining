"""
src/preprocessing/export_powerbi.py
Export dữ liệu từ PostgreSQL → CSV/Excel cho Power BI import
"""

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
WAREHOUSE_DIR = PROJECT_ROOT / "data" / "warehouse"
WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)


def get_engine():
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "vietnam_admission_dw")
    user = os.getenv("DB_USER", "admission_user")
    password = os.getenv("DB_PASSWORD", "")
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    return create_engine(url)


# ================================================================
# Các truy vấn export
# ================================================================

EXPORT_QUERIES = {
    # Bảng tổng hợp chính — denormalized cho Power BI
    "admission_main": """
        SELECT
            f.admission_key,
            s.school_name,
            s.school_type,
            s.province,
            m.major_name,
            m.major_group,
            sg.group_code AS subject_group,
            sg.subject_1, sg.subject_2, sg.subject_3,
            y.year,
            y.period_label,
            r.area AS region,
            f.admission_score,
            f.quota,
            f.admission_method,
            f.delta_score,
            f.competition_level
        FROM fact_admission f
        LEFT JOIN dim_school s ON f.school_key = s.school_key
        LEFT JOIN dim_major m ON f.major_key = m.major_key
        LEFT JOIN dim_year y ON f.year_key = y.year_key
        LEFT JOIN dim_subject_group sg ON f.subject_group_key = sg.subject_group_key
        LEFT JOIN dim_region r ON s.region_code = r.region_code
        ORDER BY y.year, s.school_name, m.major_name
    """,

    # Thống kê theo năm
    "yearly_stats": """
        SELECT
            y.year,
            y.period_label,
            COUNT(DISTINCT s.school_key) AS num_schools,
            COUNT(DISTINCT m.major_key) AS num_majors,
            COUNT(*) AS num_records,
            AVG(f.admission_score)::NUMERIC(5,2) AS avg_score,
            MIN(f.admission_score) AS min_score,
            MAX(f.admission_score) AS max_score,
            STDDEV(f.admission_score)::NUMERIC(5,2) AS std_score
        FROM fact_admission f
        JOIN dim_year y ON f.year_key = y.year_key
        JOIN dim_school s ON f.school_key = s.school_key
        JOIN dim_major m ON f.major_key = m.major_key
        GROUP BY y.year, y.period_label
        ORDER BY y.year
    """,

    # Thống kê theo trường
    "school_stats": """
        SELECT
            s.school_name,
            s.school_type,
            s.province,
            y.year,
            AVG(f.admission_score)::NUMERIC(5,2) AS avg_score,
            MIN(f.admission_score) AS min_score,
            MAX(f.admission_score) AS max_score,
            SUM(f.quota) AS total_quota,
            COUNT(*) AS num_majors
        FROM fact_admission f
        JOIN dim_school s ON f.school_key = s.school_key
        JOIN dim_year y ON f.year_key = y.year_key
        GROUP BY s.school_name, s.school_type, s.province, y.year
        ORDER BY y.year, avg_score DESC
    """,

    # Thống kê theo ngành
    "major_stats": """
        SELECT
            m.major_name,
            m.major_group,
            y.year,
            COUNT(DISTINCT s.school_key) AS num_schools,
            AVG(f.admission_score)::NUMERIC(5,2) AS avg_score,
            MAX(f.admission_score) AS max_score,
            MIN(f.admission_score) AS min_score,
            AVG(f.delta_score)::NUMERIC(5,2) AS avg_delta
        FROM fact_admission f
        JOIN dim_major m ON f.major_key = m.major_key
        JOIN dim_school s ON f.school_key = s.school_key
        JOIN dim_year y ON f.year_key = y.year_key
        GROUP BY m.major_name, m.major_group, y.year
        ORDER BY y.year, avg_score DESC
    """,

    # Top schools for Power BI ranking
    "top_schools": """
        SELECT
            s.school_name,
            s.school_type,
            s.province,
            r.area AS region,
            AVG(f.admission_score)::NUMERIC(5,2) AS overall_avg_score,
            MAX(f.admission_score) AS max_score,
            COUNT(*) AS total_records
        FROM fact_admission f
        JOIN dim_school s ON f.school_key = s.school_key
        JOIN dim_region r ON s.region_code = r.region_code
        GROUP BY s.school_name, s.school_type, s.province, r.area
        ORDER BY overall_avg_score DESC
    """,
}


def export_for_powerbi(output_dir: Path = None, format: str = "csv") -> dict:
    """
    Export tất cả bảng dữ liệu ra CSV/Excel cho Power BI.
    Hỗ trợ tự động fallback sang đọc file CSV processed nếu không có PostgreSQL.
    """
    output_dir = output_dir or WAREHOUSE_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    use_db = True
    try:
        engine = get_engine()
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.warning(f"Không thể kết nối PostgreSQL ({e}). Tự động kích hoạt cơ chế fallback đọc từ file CSV processed...")
        use_db = False

    exported = {}

    if use_db:
        for table_name, query in EXPORT_QUERIES.items():
            try:
                logger.info(f"Exporting {table_name} từ PostgreSQL...")
                with engine.connect() as conn:
                    df = pd.read_sql(text(query), conn)

                filepath = write_dataframe(df, table_name, output_dir, format)
                exported[table_name] = str(filepath)
                logger.success(f"  {table_name}: {len(df):,} records → {filepath.name}")
            except Exception as e:
                logger.error(f"  {table_name}: lỗi export DB: {e}")
        engine.dispose()
    else:
        # Fallback logic dùng pandas xử lý trực tiếp files CSV
        exported = export_from_csv_fallback(output_dir, format)

    logger.success(f"Export hoàn tất: {len(exported)} files → {output_dir}")
    return exported


def write_dataframe(df: pd.DataFrame, table_name: str, output_dir: Path, format: str) -> Path:
    """Ghi dataframe ra file format tương ứng."""
    if format == "excel":
        filepath = output_dir / f"{table_name}.xlsx"
        df.to_excel(filepath, index=False, engine="openpyxl")
    else:
        filepath = output_dir / f"{table_name}.csv"
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
    return filepath


def export_from_csv_fallback(output_dir: Path, format: str) -> dict:
    """Fallback: Đọc file processed.csv và schools_info.csv để tạo các bảng tổng hợp cho Power BI."""
    logger.info("Bắt đầu sinh các bảng tổng hợp Power BI từ tệp tin CSV processed...")
    processed_file = PROJECT_ROOT / "data" / "processed" / "admission_processed.csv"
    schools_file = PROJECT_ROOT / "data" / "raw" / "schools_info.csv"

    if not processed_file.exists():
        logger.error(f"Không tìm thấy file processed: {processed_file}. Vui lòng chạy ETL pipeline trước!")
        return {}

    try:
        df_processed = pd.read_csv(processed_file, encoding="utf-8-sig")
        df_schools = pd.read_csv(schools_file, encoding="utf-8-sig") if schools_file.exists() else pd.DataFrame()
    except Exception as e:
        logger.error(f"Lỗi đọc files CSV: {e}")
        return {}

    # Chuẩn bị bảng schools để join (tránh trùng tên cột)
    # Join bằng school_code thay vì school_name vì tên trường có thể khác format
    if not df_schools.empty:
        join_cols = ["school_code"]
        extra_cols = [c for c in ["school_type", "province", "region"] if c in df_schools.columns]
        df_schools_subset = df_schools[join_cols + extra_cols].drop_duplicates(subset=["school_code"])
    else:
        df_schools_subset = pd.DataFrame(columns=["school_code", "school_type", "province", "region"])

    # 1. admission_main (denormalized table)
    # Join processed data với schools info để lấy region, province, school_type
    df_main = df_processed.copy()
    if not df_schools_subset.empty and "school_code" in df_main.columns:
        # Xóa các cột trùng trong df_main trước khi merge để tránh hậu tố _x, _y
        cols_to_drop = [c for c in ["school_type", "province", "region"] if c in df_main.columns]
        if cols_to_drop:
            df_main = df_main.drop(columns=cols_to_drop)
        df_main = df_main.merge(df_schools_subset, on="school_code", how="left")
    
    # Đảm bảo có các cột cần thiết cho Power BI
    if "region" in df_main.columns:
        df_main = df_main.rename(columns={"region": "area"})  # để map với Area (Bắc/Trung/Nam)
    else:
        df_main["area"] = "Không xác định"
        
    df_main["period_label"] = df_main["year"].apply(
        lambda y: "Giai đoạn COVID (2020-2022)" if y <= 2022 else "Giai đoạn Hậu COVID (2023-2025)"
    )

    exported = {}
    exported["admission_main"] = str(write_dataframe(df_main, "admission_main", output_dir, format))
    logger.success(f"  admission_main: {len(df_main):,} records")

    # 2. yearly_stats
    try:
        df_yr = df_main.groupby(["year", "period_label"]).agg(
            num_schools=("school_name", "nunique"),
            num_majors=("major_name", "nunique"),
            num_records=("admission_score", "count"),
            avg_score=("admission_score", "mean"),
            min_score=("admission_score", "min"),
            max_score=("admission_score", "max"),
            std_score=("admission_score", "std")
        ).reset_index()
        df_yr = df_yr.round({"avg_score": 2, "std_score": 2})
        exported["yearly_stats"] = str(write_dataframe(df_yr, "yearly_stats", output_dir, format))
        logger.success(f"  yearly_stats: {len(df_yr):,} records")
    except Exception as e:
        logger.error(f"  yearly_stats lỗi: {e}")

    # 3. school_stats
    try:
        # Xây dựng group keys linh hoạt — chỉ dùng cột thực sự tồn tại
        sch_group = ["school_name", "year"]
        for opt_col in ["school_type", "province"]:
            if opt_col in df_main.columns and df_main[opt_col].notna().any():
                sch_group.append(opt_col)
        df_sch = df_main.groupby(sch_group).agg(
            avg_score=("admission_score", "mean"),
            min_score=("admission_score", "min"),
            max_score=("admission_score", "max"),
            total_quota=("quota", "sum"),
            num_majors=("admission_score", "count")
        ).reset_index()
        df_sch = df_sch.round({"avg_score": 2})
        exported["school_stats"] = str(write_dataframe(df_sch, "school_stats", output_dir, format))
        logger.success(f"  school_stats: {len(df_sch):,} records")
    except Exception as e:
        logger.error(f"  school_stats lỗi: {e}")

    # 4. major_stats
    try:
        df_mj = df_main.groupby(["major_name", "major_group", "year"]).agg(
            num_schools=("school_name", "nunique"),
            avg_score=("admission_score", "mean"),
            max_score=("admission_score", "max"),
            min_score=("admission_score", "min"),
            avg_delta=("delta_score", "mean")
        ).reset_index()
        df_mj = df_mj.round({"avg_score": 2, "avg_delta": 2})
        exported["major_stats"] = str(write_dataframe(df_mj, "major_stats", output_dir, format))
        logger.success(f"  major_stats: {len(df_mj):,} records")
    except Exception as e:
        logger.error(f"  major_stats lỗi: {e}")

    # 5. top_schools
    try:
        # Group by school để tính điểm chuẩn tổng quan qua tất cả các năm
        top_group = ["school_name"]
        for opt_col in ["school_type", "province", "area"]:
            if opt_col in df_main.columns and df_main[opt_col].notna().any():
                top_group.append(opt_col)
        df_top = df_main.groupby(top_group).agg(
            overall_avg_score=("admission_score", "mean"),
            max_score=("admission_score", "max"),
            total_records=("admission_score", "count")
        ).reset_index()
        df_top = df_top.round({"overall_avg_score": 2})
        if "area" in df_top.columns:
            df_top = df_top.rename(columns={"area": "region"})
        df_top = df_top.sort_values("overall_avg_score", ascending=False)
        exported["top_schools"] = str(write_dataframe(df_top, "top_schools", output_dir, format))
        logger.success(f"  top_schools: {len(df_top):,} records")
    except Exception as e:
        logger.error(f"  top_schools lỗi: {e}")

    return exported


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Export dữ liệu cho Power BI")
    parser.add_argument("--output", type=str, default=str(WAREHOUSE_DIR))
    parser.add_argument("--format", choices=["csv", "excel"], default="csv")
    args = parser.parse_args()

    export_for_powerbi(Path(args.output), args.format)

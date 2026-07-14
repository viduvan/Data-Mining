"""
src/api/data_loader.py
Load và cache dữ liệu từ CSV (hướng mở PostgreSQL).

Dữ liệu được load 1 lần khi startup rồi cache trong memory.
Kiến trúc tách rõ interface để sau dễ switch sang PostgreSQL.

3 nguồn dữ liệu:
  1. admission_processed.csv  — Điểm chuẩn tuyển sinh 2020-2025
  2. vietnamnet_hanoi_cutoffs.csv — Điểm chuẩn VietNamNet Hà Nội 2016-2025
  3. du-lieu-diem-thi-main/*.txt — Điểm thi thí sinh THPT 2016-2019
"""

import hashlib
from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ── Mapping khối thi → tên môn ────────────────────────────────────────────

SUBJECT_GROUP_SUBJECTS = {
    "A00": ["Toán", "Vật Lý", "Hóa Học"],
    "A01": ["Toán", "Vật Lý", "Tiếng Anh"],
    "A02": ["Toán", "Vật Lý", "Sinh Học"],
    "A03": ["Toán", "Vật Lý", "Lịch Sử"],
    "A04": ["Toán", "Vật Lý", "Địa Lý"],
    "A05": ["Toán", "Hóa Học", "Lịch Sử"],
    "A06": ["Toán", "Hóa Học", "Địa Lý"],
    "A07": ["Toán", "Lịch Sử", "Địa Lý"],
    "A08": ["Toán", "Lịch Sử", "GDCD"],
    "A09": ["Toán", "Địa Lý", "GDCD"],
    "A10": ["Toán", "Vật Lý", "GDCD"],
    "A11": ["Toán", "Hóa Học", "GDCD"],
    "A14": ["Toán", "Âm nhạc", "Vẽ mỹ thuật"],
    "A16": ["Toán", "Khoa học tự nhiên", "Ngữ Văn"],
    "A17": ["Toán", "Vật Lý", "Ngữ Văn"],
    "A18": ["Toán", "Hóa Học", "Ngữ Văn"],
    "B00": ["Toán", "Hóa Học", "Sinh Học"],
    "B01": ["Toán", "Sinh Học", "Lịch Sử"],
    "B02": ["Toán", "Sinh Học", "Địa Lý"],
    "B03": ["Toán", "Sinh Học", "Ngữ Văn"],
    "B04": ["Toán", "Sinh Học", "GDCD"],
    "B05": ["Toán", "Hóa Học", "Ngữ Văn"],
    "B08": ["Toán", "Sinh Học", "Tiếng Anh"],
    "C00": ["Ngữ Văn", "Lịch Sử", "Địa Lý"],
    "C01": ["Ngữ Văn", "Toán", "Vật Lý"],
    "C02": ["Ngữ Văn", "Toán", "Hóa Học"],
    "C03": ["Ngữ Văn", "Toán", "Lịch Sử"],
    "C04": ["Ngữ Văn", "Toán", "Địa Lý"],
    "C14": ["Ngữ Văn", "Toán", "GDCD"],
    "C15": ["Ngữ Văn", "Toán", "Khoa học xã hội"],
    "D01": ["Ngữ Văn", "Toán", "Tiếng Anh"],
    "D02": ["Ngữ Văn", "Toán", "Tiếng Nga"],
    "D03": ["Ngữ Văn", "Toán", "Tiếng Pháp"],
    "D04": ["Ngữ Văn", "Toán", "Tiếng Trung"],
    "D05": ["Ngữ Văn", "Toán", "Tiếng Đức"],
    "D06": ["Ngữ Văn", "Toán", "Tiếng Nhật"],
    "D07": ["Toán", "Hóa Học", "Tiếng Anh"],
    "D08": ["Toán", "Sinh Học", "Tiếng Anh"],
    "D09": ["Toán", "Lịch Sử", "Tiếng Anh"],
    "D10": ["Toán", "Địa Lý", "Tiếng Anh"],
    "D14": ["Ngữ Văn", "Lịch Sử", "Tiếng Anh"],
    "D15": ["Ngữ Văn", "Địa Lý", "Tiếng Anh"],
}

# ── Mapping cột khối trong dữ liệu điểm thi → mã khối ────────────────────

EXAM_KHOI_COL_MAP = {
    "KhoiA": "A00",
    "KhoiA1": "A01",
    "KhoiA02": "A02",
    "KhoiB": "B00",
    "KhoiC": "C00",
    "KhoiC01": "C01",
    "KhoiD": "D01",
    "KhoiD07": "D07",
}


def _generate_major_code(major_name: str) -> str:
    """
    Sinh mã ngành fake 7 chữ số từ tên ngành (deterministic).

    Format: 7XXXXXX — giống mã ngành thật của Bộ GD&ĐT.
    Cùng major_name → luôn sinh cùng mã.
    """
    h = hashlib.md5(major_name.strip().lower().encode("utf-8")).hexdigest()
    # Lấy 6 chữ số từ hash, prefix = "7"
    digits = int(h[:6], 16) % 1_000_000
    return f"7{digits:06d}"


class DataStore:
    """
    Quản lý load / cache dữ liệu cho API.

    Hiện tại đọc từ CSV. Thiết kế interface để dễ mở rộng
    sang PostgreSQL bằng cách override các method `_load_*`.
    """

    def __init__(self):
        self.admission_df: Optional[pd.DataFrame] = None
        self.export_df: Optional[pd.DataFrame] = None
        self.exam_scores: Optional[dict] = None  # {khoi_code: {year: stats}}
        self._major_code_map: dict[str, str] = {}
        self._loaded = False

    # ── Public interface ──────────────────────────────────────────────────

    def load_all(self) -> None:
        """Load toàn bộ dữ liệu. Gọi 1 lần khi startup."""
        if self._loaded:
            return
        self._load_admission_data()
        self._load_export_data()
        self._load_exam_score_data()
        self._loaded = True
        logger.success("DataStore: tất cả dữ liệu đã được load.")

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    # ── Load dữ liệu điểm chuẩn chính (tuyensinh247) ────────────────────

    def _load_admission_data(self) -> None:
        """Load admission_processed.csv và bổ sung major_code."""
        path = PROJECT_ROOT / "data" / "processed" / "admission_processed.csv"
        try:
            df = pd.read_csv(path, encoding="utf-8-sig")
            logger.info(f"Loaded {len(df):,} records từ {path.name}")
        except FileNotFoundError:
            logger.warning(f"Không tìm thấy {path}. Admission data sẽ trống.")
            self.admission_df = pd.DataFrame()
            return

        # Bổ sung major_code (fake) cho các record chưa có
        df["major_code"] = df["major_name"].apply(
            lambda x: _generate_major_code(str(x)) if pd.notna(x) else ""
        )

        # Lưu mapping để tra cứu
        self._major_code_map = dict(
            zip(df["major_name"].astype(str), df["major_code"])
        )

        # Đảm bảo school_code có giá trị (lấy phần trước dấu '-' trong school_name)
        if "school_code" in df.columns:
            df["school_code"] = df["school_code"].fillna("").astype(str)
        else:
            df["school_code"] = ""

        self.admission_df = df
        logger.info(
            f"Admission data: {len(df):,} records, "
            f"{df['subject_group'].nunique()} khối, "
            f"{df['major_code'].nunique()} ngành"
        )

    # ── Load dữ liệu VietNamNet Hà Nội ───────────────────────────────────

    def _load_export_data(self) -> None:
        """Load vietnamnet_hanoi_cutoffs.csv."""
        path = PROJECT_ROOT / "export" / "vietnamnet_hanoi_cutoffs.csv"
        try:
            df = pd.read_csv(path, encoding="utf-8-sig")
            # Chuẩn hóa cutoff_score thành float
            df["cutoff_score"] = pd.to_numeric(df["cutoff_score"], errors="coerce")
            logger.info(f"Loaded {len(df):,} records từ {path.name}")
            self.export_df = df
        except FileNotFoundError:
            logger.warning(f"Không tìm thấy {path}. Export data sẽ trống.")
            self.export_df = pd.DataFrame()

    # ── Load dữ liệu điểm thi thí sinh ───────────────────────────────────

    def _load_exam_score_data(self) -> None:
        """
        Load dữ liệu điểm thi thí sinh và tính thống kê theo khối.

        File rất lớn (~280MB) nên chỉ đọc các cột cần thiết
        và tổng hợp thống kê ngay, không giữ toàn bộ raw data.
        """
        exam_dir = PROJECT_ROOT / "du-lieu-diem-thi-main"
        txt_files = sorted(exam_dir.glob("*.txt")) if exam_dir.exists() else []

        if not txt_files:
            logger.warning(f"Không tìm thấy file điểm thi trong {exam_dir}")
            self.exam_scores = {}
            return

        # Chỉ đọc cột năm + các cột khối
        needed_cols = ["Nam"] + list(EXAM_KHOI_COL_MAP.keys())

        all_stats: dict[str, dict[int, dict]] = {}
        # {khoi_code: {year: {"mean": ..., "min": ..., "max": ..., "count": ...}}}

        for fpath in txt_files:
            logger.info(f"Đang xử lý điểm thi: {fpath.name} ...")
            try:
                # Đọc chunk để tiết kiệm RAM
                for chunk in pd.read_csv(
                    fpath,
                    encoding="utf-8-sig",
                    usecols=lambda c: c in needed_cols,
                    chunksize=100_000,
                ):
                    # Chuyển năm 2 chữ số → 4 chữ số
                    chunk["year"] = chunk["Nam"].apply(
                        lambda x: 2000 + int(x) if int(x) < 100 else int(x)
                    )

                    for col_name, khoi_code in EXAM_KHOI_COL_MAP.items():
                        if col_name not in chunk.columns:
                            continue
                        valid = chunk[[col_name, "year"]].dropna(subset=[col_name])
                        if valid.empty:
                            continue

                        for yr, group in valid.groupby("year"):
                            yr = int(yr)
                            scores = group[col_name]
                            if khoi_code not in all_stats:
                                all_stats[khoi_code] = {}
                            if yr not in all_stats[khoi_code]:
                                all_stats[khoi_code][yr] = {
                                    "sum": 0.0,
                                    "count": 0,
                                    "min": float("inf"),
                                    "max": float("-inf"),
                                }
                            st = all_stats[khoi_code][yr]
                            st["sum"] += scores.sum()
                            st["count"] += len(scores)
                            st["min"] = min(st["min"], scores.min())
                            st["max"] = max(st["max"], scores.max())

            except Exception as e:
                logger.error(f"Lỗi đọc {fpath.name}: {e}")

        # Tính mean từ sum/count
        for khoi_code in all_stats:
            for yr in all_stats[khoi_code]:
                st = all_stats[khoi_code][yr]
                st["mean"] = round(st["sum"] / st["count"], 2) if st["count"] > 0 else None
                st["min"] = round(st["min"], 2)
                st["max"] = round(st["max"], 2)
                del st["sum"]  # Không cần giữ

        self.exam_scores = all_stats
        total_khoi = len(all_stats)
        total_years = sum(len(v) for v in all_stats.values())
        logger.info(
            f"Exam scores: {total_khoi} khối × {total_years} year-groups loaded"
        )

    # ── Query helpers ─────────────────────────────────────────────────────

    def get_subject_groups(self) -> list[dict]:
        """Trả về danh sách khối thi unique từ admission data."""
        if self.admission_df is None or self.admission_df.empty:
            return []

        groups = (
            self.admission_df.groupby("subject_group")
            .size()
            .reset_index(name="total_records")
            .sort_values("total_records", ascending=False)
        )

        result = []
        for _, row in groups.iterrows():
            code = row["subject_group"]
            result.append(
                {
                    "code": code,
                    "subjects": SUBJECT_GROUP_SUBJECTS.get(code, []),
                    "total_records": int(row["total_records"]),
                }
            )
        return result

    def get_avg_scores(
        self, subject_group: str, year: Optional[int] = None
    ) -> dict:
        """
        Tính điểm trung bình theo khối thi.

        Trả về cả:
          - Điểm thi TB thí sinh (từ du-lieu-diem-thi)
          - Điểm chuẩn TB (từ admission_processed)
        """
        result = {
            "subject_group": subject_group,
            "year": year,
            "avg_exam_score": None,
            "min_exam_score": None,
            "max_exam_score": None,
            "total_candidates": None,
            "avg_cutoff_score": None,
            "min_cutoff_score": None,
            "max_cutoff_score": None,
            "total_majors": 0,
        }

        # ── Điểm thi thí sinh (exam_scores) ──
        if self.exam_scores and subject_group in self.exam_scores:
            khoi_data = self.exam_scores[subject_group]
            if year and year in khoi_data:
                st = khoi_data[year]
                result["avg_exam_score"] = st["mean"]
                result["min_exam_score"] = st["min"]
                result["max_exam_score"] = st["max"]
                result["total_candidates"] = st["count"]
            elif not year:
                # Aggregate toàn bộ các năm
                total_count = 0
                total_sum = 0.0
                global_min = float("inf")
                global_max = float("-inf")
                for yr_st in khoi_data.values():
                    total_count += yr_st["count"]
                    total_sum += yr_st["mean"] * yr_st["count"]
                    global_min = min(global_min, yr_st["min"])
                    global_max = max(global_max, yr_st["max"])
                if total_count > 0:
                    result["avg_exam_score"] = round(total_sum / total_count, 2)
                    result["min_exam_score"] = round(global_min, 2)
                    result["max_exam_score"] = round(global_max, 2)
                    result["total_candidates"] = total_count

        # ── Điểm chuẩn (admission data) ──
        if self.admission_df is not None and not self.admission_df.empty:
            mask = self.admission_df["subject_group"] == subject_group
            if year:
                mask &= self.admission_df["year"] == year
            subset = self.admission_df.loc[mask, "admission_score"].dropna()

            if not subset.empty:
                result["avg_cutoff_score"] = round(float(subset.mean()), 2)
                result["min_cutoff_score"] = round(float(subset.min()), 2)
                result["max_cutoff_score"] = round(float(subset.max()), 2)
                result["total_majors"] = int(
                    self.admission_df.loc[mask, "major_name"].nunique()
                )

        return result

    def get_majors_by_group(
        self,
        subject_group: str,
        year: Optional[int] = None,
        top_n: int = 50,
    ) -> dict:
        """
        Query ngành/trường theo khối thi.

        Bao gồm major_code (fake), điểm chuẩn, điểm TB qua các năm.
        """
        if self.admission_df is None or self.admission_df.empty:
            return {
                "subject_group": subject_group,
                "year": year or 0,
                "total_results": 0,
                "avg_cutoff_score": None,
                "majors": [],
            }

        df = self.admission_df

        # Nếu không chỉ định năm, dùng năm mới nhất
        ref_year = year or int(df["year"].max())

        # Lọc theo khối + năm
        mask = (df["subject_group"] == subject_group) & (df["year"] == ref_year)
        candidates = df[mask].copy()

        if candidates.empty:
            return {
                "subject_group": subject_group,
                "year": ref_year,
                "total_results": 0,
                "avg_cutoff_score": None,
                "majors": [],
            }

        # Tính điểm TB qua các năm cho mỗi cặp (school_name, major_name)
        avg_all_years = (
            df[df["subject_group"] == subject_group]
            .groupby(["school_name", "major_name"])["admission_score"]
            .mean()
            .reset_index()
            .rename(columns={"admission_score": "avg_score_all_years"})
        )

        candidates = candidates.merge(
            avg_all_years,
            on=["school_name", "major_name"],
            how="left",
        )

        # Sắp xếp theo điểm chuẩn giảm dần
        candidates = candidates.sort_values("admission_score", ascending=False)

        total_results = len(candidates)
        avg_cutoff = round(float(candidates["admission_score"].mean()), 2)

        # Giới hạn top_n
        candidates = candidates.head(top_n)

        majors = []
        for _, row in candidates.iterrows():
            majors.append(
                {
                    "major_code": str(row.get("major_code", "")),
                    "major_name": str(row.get("major_name", "")),
                    "school_code": str(row.get("school_code", "")),
                    "school_name": str(row.get("school_name", "")),
                    "subject_group": subject_group,
                    "admission_score": round(float(row.get("admission_score", 0)), 2),
                    "avg_score": (
                        round(float(row["avg_score_all_years"]), 2)
                        if pd.notna(row.get("avg_score_all_years"))
                        else None
                    ),
                    "year": ref_year,
                    "competition_level": str(row.get("competition_level", ""))
                    if pd.notna(row.get("competition_level"))
                    else None,
                    "score_trend": str(row.get("score_trend", ""))
                    if pd.notna(row.get("score_trend"))
                    else None,
                }
            )

        return {
            "subject_group": subject_group,
            "year": ref_year,
            "total_results": total_results,
            "avg_cutoff_score": avg_cutoff,
            "majors": majors,
        }


# ── Singleton instance ────────────────────────────────────────────────────

data_store = DataStore()

"""
src/recommendation/recommender.py
Hệ thống gợi ý trường/ngành phù hợp theo điểm thi

Cách dùng:
    # Từ CSV (không cần PostgreSQL)
    recommender = AdmissionRecommender.from_csv("data/processed/admission_processed.csv")

    # Từ PostgreSQL
    recommender = AdmissionRecommender.from_db()

    # Gợi ý
    results = recommender.recommend(
        scores=[8.0, 8.5, 9.0],
        subject_group="A00",
        priority_region="KV2",
        top_n=20,
    )
    recommender.print_results(results)
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
from loguru import logger

from .scorer import SafetyScorer, PRIORITY_SCORE


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class AdmissionRecommender:
    """
    Hệ thống gợi ý trường/ngành học theo điểm thi.

    Thuật toán:
    1. Tính tổng điểm thí sinh (bao gồm điểm ưu tiên)
    2. Lọc candidates: trường/ngành có cùng tổ hợp xét tuyển,
       điểm chuẩn ≤ tổng điểm thí sinh + biên độ rủi ro
    3. Tính safety score cho từng candidate
    4. Phân loại và rank kết quả
    5. Enrich với thông tin cluster (nếu có)
    6. Enrich với dự báo xu hướng (nếu có)

    Output: Danh sách xếp hạng theo mức an toàn
    """

    # Biên độ rủi ro: cho phép tìm ngành có điểm chuẩn cao hơn tổng điểm tối đa N điểm
    # (để user biết "vươn tới" được không)
    RISK_BUFFER = 2.0

    def __init__(
        self,
        admission_data: pd.DataFrame,
        forecast_data: pd.DataFrame = None,
        cluster_data: pd.DataFrame = None,
    ):
        """
        Args:
            admission_data: DataFrame điểm chuẩn (đã processed)
            forecast_data: DataFrame dự báo điểm chuẩn (optional)
            cluster_data: DataFrame cluster labels trường (optional)
        """
        self.data = admission_data
        self.forecast_data = forecast_data
        self.cluster_data = cluster_data
        self.scorer = SafetyScorer()
        self._latest_year = int(self.data["year"].max()) if not self.data.empty else 2024
        logger.info(f"Recommender khởi tạo. Dữ liệu năm mới nhất: {self._latest_year}")

    @classmethod
    def from_csv(
        cls,
        data_path: str = None,
        forecast_path: str = None,
        cluster_path: str = None,
    ) -> "AdmissionRecommender":
        """Tạo Recommender từ file CSV."""
        data_path = data_path or str(PROJECT_ROOT / "data" / "processed" / "admission_processed.csv")
        try:
            df = pd.read_csv(data_path, encoding="utf-8-sig")
            logger.info(f"Loaded {len(df):,} records từ {data_path}")
        except Exception as e:
            logger.error(f"Không đọc được {data_path}: {e}")
            df = pd.DataFrame()

        forecast_df = None
        if forecast_path:
            try:
                forecast_df = pd.read_csv(forecast_path, encoding="utf-8-sig")
            except Exception:
                pass

        cluster_df = None
        if cluster_path:
            try:
                cluster_df = pd.read_csv(cluster_path, encoding="utf-8-sig")
            except Exception:
                pass

        return cls(df, forecast_df, cluster_df)

    @classmethod
    def from_db(cls) -> "AdmissionRecommender":
        """Tạo Recommender từ PostgreSQL."""
        try:
            from src.preprocessing.export_powerbi import get_engine
            import sqlalchemy as sa
            engine = get_engine()
            query = """
                SELECT
                    s.school_name, m.major_name, m.major_group,
                    sg.group_code AS subject_group,
                    y.year, f.admission_score, f.quota,
                    f.delta_score, f.competition_level, f.score_trend,
                    r.area AS region
                FROM fact_admission f
                JOIN dim_school s ON f.school_key = s.school_key
                JOIN dim_major m ON f.major_key = m.major_key
                JOIN dim_year y ON f.year_key = y.year_key
                LEFT JOIN dim_subject_group sg ON f.subject_group_key = sg.subject_group_key
                LEFT JOIN dim_region r ON s.region_code = r.region_code
            """
            with engine.connect() as conn:
                df = pd.read_sql(sa.text(query), conn)
            engine.dispose()
            logger.info(f"Loaded {len(df):,} records từ PostgreSQL")
            return cls(df)
        except Exception as e:
            logger.error(f"Lỗi kết nối DB: {e}. Thử from_csv() thay thế.")
            return cls(pd.DataFrame())

    def recommend(
        self,
        scores: list,
        subject_group: str,
        priority_region: str = "KV3",
        priority_object: str = "Bình thường",
        major_group: str = None,
        region: str = None,
        school_type: str = None,
        top_n: int = 20,
        include_risky: bool = True,
        reference_year: int = None,
    ) -> pd.DataFrame:
        """
        Gợi ý trường/ngành phù hợp.

        Args:
            scores: Danh sách điểm 3 môn [môn1, môn2, môn3]
            subject_group: Tổ hợp xét tuyển (A00, D01...)
            priority_region: Khu vực ưu tiên (KV1/KV2-NT/KV2/KV3)
            priority_object: Đối tượng ưu tiên
            major_group: Lọc theo nhóm ngành (optional)
            region: Lọc theo khu vực trường (Bắc/Trung/Nam, optional)
            school_type: Lọc theo loại trường (Công lập/Tư thục, optional)
            top_n: Số kết quả trả về tối đa
            include_risky: Có bao gồm kết quả "Rủi ro" không
            reference_year: Năm tham chiếu (mặc định: năm mới nhất)

        Returns:
            DataFrame xếp hạng trường/ngành phù hợp
        """
        if self.data.empty:
            logger.error("Không có dữ liệu để gợi ý")
            return pd.DataFrame()

        # Tính tổng điểm
        total_score = self.scorer.compute_total_score(scores, priority_region, priority_object)
        logger.info(
            f"Tổng điểm: {sum(scores):.2f} + ưu tiên {PRIORITY_SCORE.get(priority_region, 0):.2f} "
            f"= {total_score:.2f}"
        )

        # Lấy điểm chuẩn năm tham chiếu
        ref_year = reference_year or self._latest_year
        candidates = self.data[self.data["year"] == ref_year].copy()

        # Lọc theo tổ hợp xét tuyển
        if subject_group and "subject_group" in candidates.columns:
            candidates = candidates[
                candidates["subject_group"] == subject_group
            ]

        # Lọc thêm theo nhóm ngành (optional)
        if major_group and "major_group" in candidates.columns:
            candidates = candidates[candidates["major_group"] == major_group]

        # Lọc theo khu vực trường (optional)
        if region and "region" in candidates.columns:
            candidates = candidates[candidates["region"] == region]

        if candidates.empty:
            logger.warning(f"Không tìm thấy candidates với tổ hợp {subject_group} năm {ref_year}")
            return pd.DataFrame()

        # Lọc theo điểm (thí sinh có thể đậu = điểm chuẩn ≤ tổng điểm + buffer)
        max_score_allowed = total_score + self.RISK_BUFFER
        candidates = candidates[
            candidates["admission_score"] <= max_score_allowed
        ]

        if not include_risky:
            candidates = candidates[
                candidates["admission_score"] <= total_score
            ]

        # Lấy điểm chuẩn mới nhất (1 record mỗi cặp trường-ngành)
        candidates = (
            candidates.sort_values("year", ascending=False)
            .drop_duplicates(subset=["school_name", "major_name", "subject_group"])
        )

        if candidates.empty:
            logger.info("Không có kết quả phù hợp")
            return pd.DataFrame()

        # Tính safety score
        results = self.scorer.score_recommendations(candidates, total_score)

        # Enrich với cluster data
        if self.cluster_data is not None and not self.cluster_data.empty:
            results = results.merge(
                self.cluster_data[["school_name", "cluster_label"]],
                on="school_name",
                how="left",
            )

        # Enrich với dự báo
        if self.forecast_data is not None and not self.forecast_data.empty:
            forecast_subset = self.forecast_data[
                ["school_name", "major_name", "subject_group",
                 "predicted_score", "trend", "delta_forecast"]
            ].rename(columns={
                "predicted_score": "forecast_score",
                "trend": "forecast_trend",
            })
            results = results.merge(
                forecast_subset,
                on=["school_name", "major_name", "subject_group"],
                how="left",
            )

        # Chọn cột output
        output_cols = [
            "school_name", "major_name", "major_group", "subject_group",
            "admission_score", "student_score", "safety_score", "safety_label",
            "competition_level", "score_trend", "quota",
        ]
        if "cluster_label" in results.columns:
            output_cols.append("cluster_label")
        if "forecast_score" in results.columns:
            output_cols.extend(["forecast_score", "forecast_trend"])

        available_cols = [c for c in output_cols if c in results.columns]
        results = results[available_cols].head(top_n)

        logger.success(f"Gợi ý {len(results)} kết quả cho điểm {total_score:.2f} - Tổ hợp {subject_group}")
        return results

    def print_results(self, results: pd.DataFrame, max_display: int = 20) -> None:
        """In kết quả gợi ý ra console theo nhóm an toàn."""
        if results.empty:
            print("Không có kết quả gợi ý.")
            return

        print("\n" + "=" * 70)
        print(f"KẾT QUẢ GỢI Ý TRƯỜNG/NGÀNH")
        print(f"Điểm thí sinh: {results['student_score'].iloc[0]:.2f}")
        print("=" * 70)

        for label_group in ["🟢 An toàn", "🟡 Tương đối", "🟠 Rủi ro", "🔴 Không khuyến nghị"]:
            subset = results[results["safety_label"] == label_group]
            if subset.empty:
                continue

            print(f"\n{label_group} ({len(subset)} kết quả):")
            print("-" * 70)

            for _, row in subset.head(max_display // 4 + 5).iterrows():
                print(
                    f"  {row.get('school_name', '')[:40]:<40} | "
                    f"{row.get('major_name', '')[:25]:<25} | "
                    f"Điểm: {row.get('admission_score', 0):.2f} | "
                    f"Safety: {row.get('safety_score', 0):+.1f}%"
                )

        print("=" * 70)


def main():
    """CLI entry point cho Recommendation System."""
    parser = argparse.ArgumentParser(
        description="Hệ thống gợi ý trường/ngành học"
    )
    parser.add_argument("--scores", nargs=3, type=float, required=True,
                        metavar=("DIEM1", "DIEM2", "DIEM3"),
                        help="Điểm 3 môn thi (VD: 8.5 9.0 8.0)")
    parser.add_argument("--group", type=str, required=True,
                        help="Tổ hợp xét tuyển (VD: A00, D01)")
    parser.add_argument("--region", type=str, default="KV3",
                        choices=["KV1", "KV2-NT", "KV2", "KV3"],
                        help="Khu vực ưu tiên (mặc định: KV3)")
    parser.add_argument("--major-group", type=str, default=None,
                        help="Lọc theo nhóm ngành")
    parser.add_argument("--top", type=int, default=20,
                        help="Số kết quả trả về (mặc định: 20)")
    parser.add_argument("--data", type=str, default=None,
                        help="Đường dẫn file data CSV")
    parser.add_argument("--from-db", action="store_true",
                        help="Đọc dữ liệu từ PostgreSQL")

    args = parser.parse_args()

    if args.from_db:
        recommender = AdmissionRecommender.from_db()
    else:
        recommender = AdmissionRecommender.from_csv(data_path=args.data)

    if recommender.data.empty:
        logger.error("Không có dữ liệu. Kiểm tra lại --data hoặc --from-db")
        sys.exit(1)

    results = recommender.recommend(
        scores=args.scores,
        subject_group=args.group.upper(),
        priority_region=args.region,
        major_group=args.major_group,
        top_n=args.top,
    )

    recommender.print_results(results)


if __name__ == "__main__":
    main()

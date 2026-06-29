"""
src/recommendation/scorer.py
Tính Safety Score — mức độ an toàn khi đăng ký vào trường/ngành
"""

from typing import Optional
import pandas as pd
from loguru import logger


# Bảng điểm ưu tiên khu vực (theo quy định Bộ GD&ĐT)
PRIORITY_SCORE = {
    "KV1":    0.75,   # Nông thôn miền núi, hải đảo
    "KV2-NT": 0.5,    # Ngoại thành, nông thôn
    "KV2":    0.25,   # Vùng ven đô thị
    "KV3":    0.0,    # Đô thị (không cộng điểm)
}

# Bảng điểm ưu tiên đối tượng
PRIORITY_SCORE_OBJECT = {
    "UT1": 2.0,   # Đối tượng ưu tiên 1 (Anh hùng, Bà mẹ VN anh hùng...)
    "UT2": 1.0,   # Đối tượng ưu tiên 2
    "Bình thường": 0.0,
}

# Ngưỡng phân loại Safety
SAFETY_THRESHOLDS = {
    "An toàn":       0.10,    # safety_score ≥ 10% → An toàn
    "Tương đối":     0.0,     # 0% ≤ safety_score < 10% → Tương đối
    "Rủi ro":       -0.10,    # -10% ≤ safety_score < 0% → Rủi ro cao
    # < -10%: Không khuyến nghị
}


class SafetyScorer:
    """
    Tính mức độ an toàn khi đăng ký vào một trường/ngành.

    Safety Score = (Điểm thí sinh - Điểm chuẩn) / Điểm chuẩn × 100%

    Phân loại:
    - 🟢 An toàn      : Safety ≥ 10%  (điểm thí sinh cao hơn điểm chuẩn ≥ 10%)
    - 🟡 Tương đối    : 0% ≤ Safety < 10%
    - 🟠 Rủi ro       : -10% ≤ Safety < 0%
    - 🔴 Không khuyến nghị: Safety < -10%
    """

    def compute_total_score(
        self,
        subject_scores: list,
        priority_region: str = "KV3",
        priority_object: str = "Bình thường",
    ) -> float:
        """
        Tính tổng điểm xét tuyển (điểm thi + điểm ưu tiên).

        Args:
            subject_scores: [điểm môn 1, điểm môn 2, điểm môn 3]
            priority_region: Khu vực (KV1, KV2-NT, KV2, KV3)
            priority_object: Đối tượng ưu tiên

        Returns:
            Tổng điểm xét tuyển (đã cộng ưu tiên)
        """
        base_score = sum(subject_scores)
        region_bonus = PRIORITY_SCORE.get(priority_region, 0.0)
        object_bonus = PRIORITY_SCORE_OBJECT.get(priority_object, 0.0)
        total = base_score + region_bonus + object_bonus
        # Cap tối đa 30 điểm + ưu tiên (thực tế có thể > 30 với ưu tiên)
        return round(min(total, 30.0 + region_bonus + object_bonus), 2)

    def compute_safety_score(
        self,
        student_score: float,
        admission_score: float,
    ) -> float:
        """
        Tính Safety Score = (student - admission) / admission × 100.

        Returns:
            Safety score (%) — dương = an toàn, âm = rủi ro
        """
        if admission_score is None or admission_score <= 0:
            return 0.0
        return round((student_score - admission_score) / admission_score * 100, 2)

    def classify_safety(self, safety_score: float) -> str:
        """
        Phân loại mức độ an toàn.

        Returns:
            "🟢 An toàn" / "🟡 Tương đối" / "🟠 Rủi ro" / "🔴 Không khuyến nghị"
        """
        if safety_score >= SAFETY_THRESHOLDS["An toàn"] * 100:
            return "🟢 An toàn"
        elif safety_score >= SAFETY_THRESHOLDS["Tương đối"] * 100:
            return "🟡 Tương đối"
        elif safety_score >= SAFETY_THRESHOLDS["Rủi ro"] * 100:
            return "🟠 Rủi ro"
        else:
            return "🔴 Không khuyến nghị"

    def score_recommendations(
        self,
        candidates: pd.DataFrame,
        student_total_score: float,
        admission_year: int = None,
    ) -> pd.DataFrame:
        """
        Tính safety score cho tất cả candidates.

        Args:
            candidates: DataFrame với cột admission_score (điểm chuẩn năm gần nhất)
            student_total_score: Tổng điểm thí sinh (đã cộng ưu tiên)
            admission_year: Năm xét tuyển (để chọn điểm chuẩn đúng năm)

        Returns:
            DataFrame với thêm cột safety_score và safety_label
        """
        df = candidates.copy()

        df["student_score"] = student_total_score
        df["safety_score"] = df["admission_score"].apply(
            lambda x: self.compute_safety_score(student_total_score, x)
        )
        df["safety_label"] = df["safety_score"].apply(self.classify_safety)

        # Sort: an toàn nhất trên cùng, trong cùng nhóm thì điểm chuẩn cao nhất trước
        safety_order = {
            "🟢 An toàn": 0,
            "🟡 Tương đối": 1,
            "🟠 Rủi ro": 2,
            "🔴 Không khuyến nghị": 3,
        }
        df["safety_order"] = df["safety_label"].map(safety_order)
        df = df.sort_values(
            ["safety_order", "admission_score"],
            ascending=[True, False]
        ).drop(columns=["safety_order"])

        return df

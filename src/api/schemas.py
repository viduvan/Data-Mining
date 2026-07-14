"""
src/api/schemas.py
Pydantic models cho API response — Chatbot tuyển sinh.

Các schema dựa trên format dữ liệu từ 3 nguồn:
- admission_processed.csv (điểm chuẩn tuyển sinh)
- vietnamnet_hanoi_cutoffs.csv (điểm chuẩn VietNamNet Hà Nội)
- du-lieu-diem-thi-main (điểm thi thí sinh THPT)
"""

from typing import Optional
from pydantic import BaseModel, Field


# ── Khối thi / Subject Group ──────────────────────────────────────────────

class SubjectGroupInfo(BaseModel):
    """Thông tin 1 khối thi."""

    code: str = Field(..., description="Mã khối thi, ví dụ: A00, D01")
    subjects: list[str] = Field(
        default_factory=list,
        description="Danh sách tên môn trong khối (nếu biết)",
    )
    total_records: int = Field(
        ..., description="Tổng số bản ghi tuyển sinh có khối này"
    )


class SubjectGroupsResponse(BaseModel):
    """Response: danh sách tất cả khối thi."""

    total_groups: int
    groups: list[SubjectGroupInfo]


# ── Điểm trung bình theo khối ─────────────────────────────────────────────

class AvgScoreResponse(BaseModel):
    """Response: điểm trung bình theo khối thi."""

    subject_group: str = Field(..., description="Mã khối thi")
    year: Optional[int] = Field(None, description="Năm (None = tất cả các năm)")

    # Điểm thi trung bình (từ du-lieu-diem-thi — điểm thí sinh thực tế)
    avg_exam_score: Optional[float] = Field(
        None,
        description="Điểm thi trung bình của thí sinh theo khối (nguồn: dữ liệu điểm thi THPT)",
    )
    min_exam_score: Optional[float] = Field(None, description="Điểm thi thấp nhất")
    max_exam_score: Optional[float] = Field(None, description="Điểm thi cao nhất")
    total_candidates: Optional[int] = Field(
        None, description="Số thí sinh có điểm khối này"
    )

    # Điểm chuẩn trung bình (từ admission_processed — điểm chuẩn tuyển sinh)
    avg_cutoff_score: Optional[float] = Field(
        None,
        description="Điểm chuẩn tuyển sinh trung bình (nguồn: admission_processed.csv)",
    )
    min_cutoff_score: Optional[float] = Field(None, description="Điểm chuẩn thấp nhất")
    max_cutoff_score: Optional[float] = Field(None, description="Điểm chuẩn cao nhất")
    total_majors: int = Field(
        0, description="Số ngành/chương trình xét tuyển khối này"
    )


# ── Query ngành + trường theo khối ────────────────────────────────────────

class MajorInfo(BaseModel):
    """Thông tin 1 ngành/trường trong kết quả query."""

    major_code: str = Field(..., description="Mã ngành (7 chữ số)")
    major_name: str = Field(..., description="Tên ngành")
    school_code: str = Field(..., description="Mã trường")
    school_name: str = Field(..., description="Tên trường")
    subject_group: str = Field(..., description="Khối thi")
    admission_score: float = Field(..., description="Điểm chuẩn")
    avg_score: Optional[float] = Field(
        None,
        description="Điểm chuẩn trung bình của ngành này qua các năm",
    )
    year: int = Field(..., description="Năm xét tuyển")
    competition_level: Optional[str] = Field(
        None, description="Mức cạnh tranh (Thấp / Trung bình / Cao / Rất cao)"
    )
    score_trend: Optional[str] = Field(
        None, description="Xu hướng điểm (Tăng / Giảm / Ổn định)"
    )


class MajorsResponse(BaseModel):
    """Response: danh sách ngành/trường theo khối thi."""

    subject_group: str
    year: int
    total_results: int
    avg_cutoff_score: Optional[float] = Field(
        None, description="Điểm chuẩn TB của tất cả ngành trong khối"
    )
    majors: list[MajorInfo]


# ── Error response ────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Response khi có lỗi."""

    detail: str
    error_code: Optional[str] = None

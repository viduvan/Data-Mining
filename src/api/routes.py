"""
Endpoints:
    GET /api/subject-groups — Danh sách khối thi
    GET /api/avg-score      — Điểm trung bình theo khối thi
    GET /api/majors         — Query ngành/trường theo khối thi
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from .data_loader import data_store
from .schemas import (
    AvgScoreResponse,
    MajorInfo,
    MajorsResponse,
    SubjectGroupInfo,
    SubjectGroupsResponse,
)


router = APIRouter(prefix="/api", tags=["Chatbot Tuyển Sinh"])


# ── GET /api/subject-groups ───────────────────────────────────────────────

@router.get(
    "/subject-groups",
    response_model=SubjectGroupsResponse,
    summary="Danh sách khối thi",
    description="Trả về tất cả các khối thi (tổ hợp xét tuyển) có trong hệ thống, "
    "kèm danh sách môn thi và số lượng bản ghi.",
)
async def get_subject_groups():
    """Liệt kê tất cả khối thi có sẵn."""
    groups = data_store.get_subject_groups()

    if not groups:
        raise HTTPException(
            status_code=503,
            detail="Dữ liệu chưa được load. Vui lòng thử lại sau.",
        )

    return SubjectGroupsResponse(
        total_groups=len(groups),
        groups=[SubjectGroupInfo(**g) for g in groups],
    )


# ── GET /api/avg-score ────────────────────────────────────────────────────

@router.get(
    "/avg-score",
    response_model=AvgScoreResponse,
    summary="Điểm trung bình theo khối thi",
    description=(
        "Trả về điểm trung bình theo khối thi, bao gồm:\n"
        "- **Điểm thi trung bình** của thí sinh (nguồn: dữ liệu điểm thi THPT)\n"
        "- **Điểm chuẩn trung bình** tuyển sinh (nguồn: dữ liệu tuyển sinh)\n\n"
        "Có thể lọc theo năm."
    ),
)
async def get_avg_score(
    subject_group: str = Query(
        ...,
        description="Mã khối thi (ví dụ: A00, D01, B00)",
        examples=["A00", "D01", "B00"],
    ),
    year: Optional[int] = Query(
        None,
        description="Năm (VD: 2025). Nếu không truyền sẽ tính trên tất cả các năm.",
        ge=2016,
        le=2030,
    ),
):
    """Tính điểm trung bình (điểm thi thí sinh + điểm chuẩn) theo khối."""
    result = data_store.get_avg_scores(
        subject_group=subject_group.upper(), year=year
    )

    # Nếu cả 2 nguồn đều không có dữ liệu → 404
    if result["avg_exam_score"] is None and result["avg_cutoff_score"] is None:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy dữ liệu cho khối {subject_group.upper()}"
            + (f" năm {year}" if year else ""),
        )

    return AvgScoreResponse(**result)


# ── GET /api/majors ───────────────────────────────────────────────────────

@router.get(
    "/majors",
    response_model=MajorsResponse,
    summary="Query ngành/trường theo khối thi",
    description=(
        "Trả về danh sách mã ngành + trường xét tuyển theo khối thi.\n\n"
        "Bao gồm: mã ngành, tên ngành, mã trường, tên trường, "
        "điểm chuẩn, điểm trung bình qua các năm, mức cạnh tranh."
    ),
)
async def get_majors(
    subject_group: str = Query(
        ...,
        description="Mã khối thi (ví dụ: A00, D01, B00)",
        examples=["A00", "D01", "B00"],
    ),
    year: Optional[int] = Query(
        None,
        description="Năm (VD: 2025). Mặc định: năm mới nhất.",
        ge=2016,
        le=2030,
    ),
    top_n: int = Query(
        50,
        description="Số kết quả trả về tối đa.",
        ge=1,
        le=500,
    ),
):
    """Query danh sách ngành/trường xét tuyển theo khối."""
    result = data_store.get_majors_by_group(
        subject_group=subject_group.upper(),
        year=year,
        top_n=top_n,
    )

    if result["total_results"] == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy ngành nào cho khối {subject_group.upper()}"
            + (f" năm {year}" if year else ""),
        )

    return MajorsResponse(
        subject_group=result["subject_group"],
        year=result["year"],
        total_results=result["total_results"],
        avg_cutoff_score=result["avg_cutoff_score"],
        majors=[MajorInfo(**m) for m in result["majors"]],
    )
